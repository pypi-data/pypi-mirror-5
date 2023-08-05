typedef struct {
  PyObject_HEAD
} PyPTPConstant;

typedef struct {
  char* name;
  long value;
} int_const_t;

static PyObject* init_int_constant_class_dict(void* data) {
  int i = 0, set_dict_res;
  PyObject *result, *value;
  int_const_t* int_data = (int_const_t*) data;

  result = PyDict_New();
  if (result == NULL)
    return NULL;

  while (int_data[i].name) {
    value = PyInt_FromLong(int_data[i].value);
    if (value == NULL) {
      Py_DECREF(result);
      return NULL;
    }
    set_dict_res = PyDict_SetItemString(result, int_data[i].name, value);
    Py_DECREF(value);
    if (set_dict_res) {
      Py_DECREF(result);
      return NULL;
    }
    i++;
  }
  return result;
}

typedef PyObject* init_dict_func(void* data);

/* sample of what should be in pyptp-constants-data.c:
static int_const_t PyPTPConstant_data[] = {
  {"ONE", 1},
  {"TWO", 2},
  {NULL},
};

static struct {
  char *full_name;
  char *name;
  char *doc;
  void *data;
  init_dict_func *init_dict;
} constant_info[] = {
  {"ptp.PTPConstant", "PTPConstant", NULL, PyPTPConstant_data,
   init_int_constant_class_dict},
  {NULL}
};

*/

#include "pyptp-constants-data.c"

static int init_constant_class(int constant_index, PyObject *module) {
  PyTypeObject *type_object;
  PyObject *dict_data;

  type_object = malloc(sizeof(PyTypeObject));
  if (type_object == NULL) {
    return -1;
  }
  memset(type_object, 0, sizeof(PyTypeObject));

  type_object->tp_name = constant_info[constant_index].full_name;
  type_object->tp_doc = constant_info[constant_index].doc;
  type_object->tp_basicsize = sizeof(PyPTPConstant);
  type_object->tp_flags = Py_TPFLAGS_DEFAULT;

  dict_data = (*constant_info[constant_index].init_dict)(
      constant_info[constant_index].data);
  if (dict_data == 0) {
    free(type_object);
    return -1;
  }
  type_object->tp_dict = dict_data;

  Py_INCREF(type_object);
  if (PyType_Ready(type_object) < 0)
    return -1;
  PyModule_AddObject(module, constant_info[constant_index].name,
                     (PyObject*) type_object);
  return 0;
}

static int init_all_constants(PyObject* module) {
  int i = 0;
  while (constant_info[i].name) {
    if (init_constant_class(i, module))
      return -1;
    i++;
  }
  return 0;
}
