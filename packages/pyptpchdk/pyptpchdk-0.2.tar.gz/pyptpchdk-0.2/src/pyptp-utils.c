/* Copyright Abel Deuring 2012
   python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.
 */

// misc utilities

static PyObject* uint16_array_to_tuple(const uint16_t* array, int len) {
  int i;
  PyObject *element, *result = (PyObject*) PyTuple_New(len);

  if (result == NULL) {
    return NULL;
  }
  for (i = 0; i < len; i++) {
    element = PyInt_FromLong(array[i]);
    if (element == NULL || PyTuple_SetItem(result, i, element)) {
      Py_XDECREF(element);
      Py_DECREF(result);
      return NULL;
    }
  }
  return result;
}

static PyObject* uint32_array_to_tuple(const uint32_t* array, int len) {
  int i;
  PyObject *element, *result = (PyObject*) PyTuple_New(len);

  if (result == NULL) {
    return NULL;
  }
  for (i = 0; i < len; i++) {
    element = PyInt_FromLong(array[i]);
    if (element == NULL || PyTuple_SetItem(result, i, element)) {
      Py_XDECREF(element);
      Py_DECREF(result);
      return NULL;
    }
  }
  return result;
}

// define a Python dictonary item from an integer; do all necessary
// tests; if errors occur, DEFREF the dictionary and return NULL.
#define set_dict_int_item(dict, name, value)                  \
{ PyObject *item;                                             \
  item = PyInt_FromLong(value);                               \
  if (item == NULL) {                                         \
    Py_DECREF(dict);                                          \
    return NULL;                                              \
  }                                                           \
  if (PyDict_SetItemString(result, name, item)) {             \
    Py_DECREF(dict);                                          \
    Py_DECREF(item);                                          \
    return NULL;                                              \
  }                                                           \
  Py_DECREF(item);                                            \
}

// define a Python dictonary item from a string; do all necessary
// tests; if errors occur, DEFREF the dictionary and return NULL.
#define set_dict_string_item(dict, name, value)               \
{ PyObject *item;                                             \
  item = PyString_FromString(value);                          \
  if (item == NULL) {                                         \
    Py_DECREF(dict);                                          \
    return NULL;                                              \
  }                                                           \
  if (PyDict_SetItemString(result, name, item)) {             \
    Py_DECREF(dict);                                          \
    Py_DECREF(item);                                          \
    return NULL;                                              \
  }                                                           \
  Py_DECREF(item);                                            \
}

PyObject* time_t_to_datetime(time_t *time) {
  // We assume that all times are local times. This fits for the
  // time values coming from ptp_getobjectinfo, which were generated
  // by mktime()
  struct tm *time_info;
  PyObject *params;

  if (NULL == (time_info = localtime(time))) {
    PyErr_SetString(
        PTPError, "Cant convert timestanp to Python datetime object");
    return NULL;
  }

  params = Py_BuildValue("iiiiii", time_info->tm_year + 1900,
                         time_info->tm_mon + 1, time_info->tm_mday,
                         time_info->tm_hour, time_info->tm_min,
                         time_info->tm_sec);
  if (params == NULL)
    return NULL;
  return PyObject_CallObject(datetime_class, params);
}
