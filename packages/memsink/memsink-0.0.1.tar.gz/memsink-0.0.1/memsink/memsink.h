/*
 * Copyright 2013, David Wilson.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy
 * of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

/**
 * Generic copy-on-invalidate memory protocol for Python. This is code is
 * insane, a better solution is needed. This is headers-only so only a single
 * file needs copied into a project to support the protocol.
 *
 * See https://github.com/dw/acid/issues/23
 *
 * Theory of operation:
 *      1. SourceType represents some read-only chunk of memory, but that
 *         memory may go away at any time.
 *      2. SinkType represents some immutable view of that memory, so it
 *         has no real need to copy or modify it.
 *      3. SourceType and SinkType need to talk to each other to share this
 *         memory safely.
 *
 *      4. Programmer inserts a 'PyObject *sink_head' field anywhere in
 *         SourceType's PyObject struct.
 *      5. After PyType_Ready(&SourceType), programmer calls
 *         ms_init_source(&SourceType, offsetof(Source, sink_head)).
 *      6. In SourceType's implementation, programmer inserts ms_notify(self)
 *         anywhere its memory is about to become invalid.
 *
 *      7. Programmer inserts a 'struct ms_node sink_node' field anywhere in
 *         SinkType's PyObject struct, and a "PyObject *source" field to track
 *         the active SourceType, if any.
 *      8. Programmer writes a 'my_invalidate()' function to handle
 *         when SinkType is told SourceType's memory is about to go away.
 *         Probably it wants to copy the memory, and Py_CLEAR(self->source).
 *      9. After PyType_Ready(&SinkType), programmer calls
 *         ms_init_sink(&SinkType, offsetof(Sink, sink_node), my_invalidate).
 *      10. When SinkType is handed a piece of memory belonging to SourceType,
 *          programmer inserts "ms_listen(self->source, self)".
 *      11. In SinkType's PyTypeObject.tp_dealloc funcion, programmer inserts
 *          "ms_cancel(self->source, self)".
 */

#ifndef MEMSINK_H
#define MEMSINK_H

/**
 * List node that must appear somewhere within a sink's PyObject structure.
 * offsetof(ThatStruct, this_field) must be passed to ms_init_sink().
 */
struct ms_node {
    /** Borrowed reference to previous sink in list, or NULL to indicate
     * head of list (in which case borrowed reference is stored directly in
     * source object). */
    PyObject *prev;
    /** Borrowed reference to next sink in the list. */
    PyObject *next;
};

struct MemSink_CAPI {
    int (*is_source)(PyObject *);
    int (*listen)(PyObject *, PyObject *);
    int (*cancel)(PyObject *, PyObject *);
    int (*notify)(PyObject *, PyObject **);
    int (*init_sink)(PyTypeObject *type, Py_ssize_t node_offset,
                     int (*invalidate)(PyObject *, PyObject *));
    int (*init_source)(PyTypeObject *type, Py_ssize_t head_offset);
};

#ifndef BUILDING_MEMSINK
static struct MemSink_CAPI *_ms_api;
#define MemSink_IMPORT \
    MemSink_CAPI = (void *)PyCapsule_Import("memsink._memsink.CAPI", 0)

#define ms_is_source (_ms_api->is_source)
#define ms_listen (_ms_api->listen)
#define ms_cancel (_ms_api->cancel)
#define ms_notify (_ms_api->notify)
#define ms_init_sink (_ms_api->init_sink)
#define ms_init_source (_ms_api->init_source)
#endif

#endif /* !MEMSINK_H */
