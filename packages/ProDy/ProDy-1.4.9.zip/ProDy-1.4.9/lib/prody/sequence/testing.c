static int parseLabel(PyObject *labels, PyObject *mapping, char *line,
                      int length) {

    /* Append label to *labels*, extract identifier, and index label
       position in the list. Return 1 when successful, 0 on failure. */

    int i, ch, slash = 0, dash = 0;//, ipipe = 0, pipes[4] = {0, 0, 0, 0};

    for (i = 0; i < length; i++) {
        ch = line[i];
        if (ch < 32 && ch != 20)
            break;
        else if (ch == '/' && slash == 0 && dash == 0)
            slash = i;
        else if (ch == '-' && slash > 0 && dash == 0)
            dash = i;
        //else if (line[i] == '|' && ipipe < 4)
        //    pipes[ipipe++] = i;
    }

    PyObject *label, *index;
    #if PY_MAJOR_VERSION >= 3
    label = PyUnicode_FromStringAndSize(line, i);
    index = PyLong_FromSsize_t(PyList_Size(labels));
    #else
    label = PyString_FromStringAndSize(line, i);
    index = PyInt_FromSsize_t(PyList_Size(labels));
    #endif

    if (!label || !index || PyList_Append(labels, label) < 0) {
        PyObject *none = Py_None;
        PyList_Append(labels, none);
        Py_DECREF(none);

        Py_XDECREF(index);
        Py_XDECREF(label);
        return 0;
    }

    if (slash > 0 && dash > slash) {
        Py_DECREF(label);
        #if PY_MAJOR_VERSION >= 3
        label = PyUnicode_FromStringAndSize(line, slash);
        #else
        label = PyString_FromStringAndSize(line, slash);
        #endif
    }

    if (PyDict_Contains(mapping, label)) {
        PyObject *item = PyDict_GetItem(mapping, label); /* borrowed */
        if (PyList_Check(item)) {
            PyList_Append(item, index);
            Py_DECREF(index);
        } else {
            PyObject *list = PyList_New(2); /* new reference */
            PyList_SetItem(list, 0, item);
            Py_INCREF(item);
            PyList_SetItem(list, 1, index); /* steals reference, no DECREF */
            PyDict_SetItem(mapping, label, list);
            Py_DECREF(list);
        }
    } else {
        PyDict_SetItem(mapping, label, index);
        Py_DECREF(index);
    }

    Py_DECREF(label);
    return 1;
}