
#include <stdlib.h>
#include <stdio.h>
#include <Python.h>

#define BUILDING_MEMSINK
#include "memsink.h"

#define MS_SINK_MAGIC 0xCAF0
#define MS_SRC_MAGIC  0xCAF1
#define DEBUG(s, ...) fprintf(stderr, \
    "memsink: %s:%d: " s "\n", __func__, __LINE__, ## __VA_ARGS__);

/** Interned PyString "__memsource__" set by _ms_init(). */
static PyObject *src_attr;
/** Interned PyString "__memsink__" set by _ms_init(). */
static PyObject *sink_attr;

/**
 * Internal source descriptor, heap-allocated and stored in a PyCapsule as the
 * source type's __memsource__ attribute.
 */
struct ms_source {
    /** Changes when ABI changes. */
    int magic;
    /** Offset of "PyObject *" list head in type's PyObject struct. */
    Py_ssize_t head_offset;
};

/**
 * Internal sink descriptor, heap-allocated and stored in a PyCapsule as the
 * sink type's __memsink__ attribute.
 */
struct ms_sink {
    /** Changes when ABI changes. */
    int magic;
    /** Offset of "struct ms_node" stored in type's PyObject struct. */
    Py_ssize_t node_offset;
    /** Notification receiver invoked when src memory expires. */
    int (*invalidate)(PyObject *src, PyObject *sink);
};

/**
 * Fetch a "__memsink__" or "__memsource__" descriptor from `obj`'s type.
 * `attr` is the interned string attribute name, `magic` is the expected struct
 * magic. Return a pointer on success, or return NULL and set an exception on
 * error.
 */
static void *
_ms_get_desc(PyObject *obj, PyObject *attr, int magic)
{
    PyObject *capsule;
    void *desc;

    if(! ((capsule = PyDict_GetItem(obj->ob_type->tp_dict, attr)))) {
        return PyErr_Format(PyExc_TypeError, "Type %s lacks '%s' attribute.",
                            obj->ob_type->tp_name, PyString_AS_STRING(attr));
    }

    desc = PyCapsule_GetPointer(capsule, NULL);
    Py_DECREF(capsule);
    if(desc && (*(int *)desc) != magic) {
        return PyErr_Format(PyExc_TypeError,
            "Type %s '%s' magic is incorrect, got %08x, wanted %08x. "
            "Probable memsink.h version mismatch.",
            obj->ob_type->tp_name, PyString_AS_STRING(attr),
            *(int *)desc, magic);
        desc = NULL;
    }
    return desc;
}

#define SINK_DESC(sink) _ms_get_desc(sink, sink_attr, MS_SINK_MAGIC)
#define SRC_DESC(src) _ms_get_desc(src, src_attr, MS_SRC_MAGIC)
#define FIELD_AT(ptr, offset) ((void *) ((char *)(ptr)) + (offset))

/**
 * Return 1 if `source` supports the memsink protocol.
 */
static int
ms_is_source(PyObject *src)
{
    struct ms_source *desc = SRC_DESC(src);
    int ret = 1;
    if(! desc) {
        PyErr_Clear();
        ret = 0;
    }
    return ret;
}

/**
 * Notify subscribers to `src` that its memory is becoming invalid, and cancel
 * their subscription. Return 0 on success or return -1 and set an exception on
 * error.
 */
static int
ms_notify(PyObject *src, PyObject **list_head)
{
    PyObject *cur = *list_head;
    while(cur) {
        struct ms_sink *mcur;
        struct ms_node *mnode;
        if(! ((mcur = SINK_DESC(cur)))) {
            return -1;
        }
        mnode = FIELD_AT(cur, mcur->node_offset);
        mcur->invalidate(src, cur); // TODO how to handle -1?
        cur = mnode->next;
        mnode->prev = NULL;
        mnode->next = NULL;
    }
    return 0;
}

/**
 * Fetch the struct ms_node from a sink, or return NULL and set an exception on
 * error.
 */
static struct ms_node *
_ms_sink_node(PyObject *sink)
{
    struct ms_sink *desc = SINK_DESC(sink);
    struct ms_node *node = NULL;
    if(desc) {
        node = FIELD_AT(sink, desc->node_offset);
    }
    return node;
}

/**
 * Tell `sink` when memory exported by `src` becomes invalid. `src` must be of
 * a type for which ms_init_source() has been invoked, `sink` must be of a type
 * for which ms_init_sink() has been invoked. Return 0 on success or -1 on
 * error.
 */
static int
ms_listen(PyObject *src, PyObject *sink)
{
    // Push `sink` on the front of the list, updating the previous head if one
    // existed.
    struct ms_source *msrc;
    struct ms_node *node;
    PyObject **head;

    if(! (((msrc = SRC_DESC(src))) &&
          ((node = _ms_sink_node(sink))))) {
        return -1;
    }

    head = FIELD_AT(src, msrc->head_offset);
    if(*head) {
        struct ms_node *headnode = _ms_sink_node(*head);
        if(! headnode) {
            return -1;
        }
        headnode->prev = sink;
    }
    node->next = *head;
    node->prev = NULL;
    *head = sink;
    return 0;
}

/**
 * Cancel notification of `sink` when memory exported by `src` becomes invalid.
 * `src` must be of a type for which ms_init_source() has been invoked, `sink`
 * must be of a type for which ms_init_sink() has been invoked. Return 0 on
 * success or -1 on error.
 */
static int
ms_cancel(PyObject *src, PyObject *sink)
{
    PyObject **head;
    struct ms_source *srcdesc;
    struct ms_node *sinknode;
    struct ms_node *prevnode = NULL;
    struct ms_node *nextnode = NULL;

    if(! ((srcdesc = SRC_DESC(src)))) {
        return -1;
    }
    head = FIELD_AT(src, srcdesc->head_offset);

    if(! ((sinknode = _ms_sink_node(sink)))) {
        return -1;
    }
    if(sinknode->prev && !((prevnode = _ms_sink_node(sinknode->prev)))) {
        return -1;
    }
    if(sinknode->next && !((nextnode = _ms_sink_node(sinknode->next)))) {
        return -1;
    }
    if(nextnode) {
        nextnode->prev = sinknode->prev;
    }
    if(prevnode) {
        prevnode->next = sinknode->next;
    } else {
        if(*head != sink) {
            PyErr_SetString(PyExc_SystemError, "memsink.h list is corrupt.");
            return -1;
        }
        *head = sinknode->next;
    }

    sinknode->prev = NULL;
    sinknode->next = NULL;
    return 0;
}

/**
 * Capsule destructor function.
 */
static void _ms_capsule_destroy(PyObject *capsule)
{
    free(PyCapsule_GetPointer(capsule, NULL));
}

/**
 * Code shared between ms_init_sink() and ms_init_source().
 */
static void *
_ms_init_type(PyTypeObject *type, PyObject *attr, size_t size)
{
    void *ptr;
    PyObject *capsule;

    if(! ((ptr = malloc(size)))) {
        return NULL;
    }

    if(! ((capsule = PyCapsule_New(ptr, NULL, _ms_capsule_destroy)))) {
        free(ptr);
        return NULL;
    }

    if(PyDict_SetItem(type->tp_dict, attr, capsule)) {
        ptr = NULL;
    }
    Py_DECREF(capsule);
    return ptr;
}

/**
 * Decorate `type` to include the __memsink__ attribute. `node_offset` is the
 * offset into `type` where `struct ms_node` occurs, and `invalidate` is
 * the callback function that disassociates instances from any shared memory.
 * Return 0 on success or -1 on failure.
 */
static int
ms_init_sink(PyTypeObject *type, Py_ssize_t node_offset,
             int (*invalidate)(PyObject *, PyObject *))
{
    struct ms_sink *desc;
    if(! ((desc = _ms_init_type(type, sink_attr, sizeof *desc)))) {
        return -1;
    }
    desc->magic = MS_SINK_MAGIC;
    desc->node_offset = node_offset;
    desc->invalidate = invalidate;
    return 0;
}

/**
 * Decorate `type` to include the "__memsource__" attribute. `head_offset` is
 * the offset of the "PyObject *ms_head" in the type's PyObject struct. Return
 * 0 on success or return -1 and set an exception on failure.
 */
static int
ms_init_source(PyTypeObject *type, Py_ssize_t head_offset)
{
    struct ms_source *desc;
    if(! ((desc = _ms_init_type(type, src_attr, sizeof *desc)))) {
        return -1;
    }
    desc->magic = MS_SRC_MAGIC;
    desc->head_offset = head_offset;
    return 0;
}

static struct MemSink_CAPI api = {
    .is_source = ms_is_source,
    .listen = ms_listen,
    .cancel = ms_cancel,
    .notify = ms_notify,
    .init_sink = ms_init_sink,
    .init_source = ms_init_source
};

/**
 * Initialize the interned "__memsource__" and "__memsink__" string constants.
 * Return 0 on sucess or -1 on error.
 */
PyMODINIT_FUNC
init_memsink(void)
{
    src_attr = PyString_InternFromString("__memsource__");
    sink_attr = PyString_InternFromString("__memsink__");
    if(! (src_attr && sink_attr)) {
        abort();
    }

    PyObject *mod = Py_InitModule("memsink._memsink", NULL);
    if(! mod) {
        abort();
    }

    PyObject *dct = PyModule_GetDict(mod);
    if(! dct) {
        abort();
    }

    PyObject *capsule = PyCapsule_New(&api, "memsink._memsink.CAPI", NULL);
    if(PyDict_SetItemString(dct, "CAPI", capsule)) {
        abort();
    }
    return;
}
