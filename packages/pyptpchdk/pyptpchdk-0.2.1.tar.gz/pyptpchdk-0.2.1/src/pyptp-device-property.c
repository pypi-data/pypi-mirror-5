/* Copyright Abel Deuring 2012
   python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.
 */

// class PTPDeviceProperty. Note that this class is _not_ decclared
// on module level: Only PTPDevice should create instances.

typedef struct {
  PyObject_HEAD
  PTPDevice* device;
  PTPDevicePropDesc ptp_property;
} PTPDeviceProperty;

static PyTypeObject PTPDeviceType;

static PyObject* PTPDeviceProperty_get_id(PyObject* obj, void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  return PyInt_FromLong(self->ptp_property.DevicePropertyCode);
}

static PyObject* PTPDeviceProperty_get_readonly(PyObject* obj, void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  int readonly = self->ptp_property.GetSet == PTP_DPGS_GetSet ? 0 : 1;
  return PyBool_FromLong(readonly);
}

// common helper for PTPDeviceProperty_get_current_value and
// PTPDeviceProperty_get_default_value
static PyObject* PTPDeviceProperty_get_value(void* value, uint16_t type_) {

  /* xxxx this CAN happen:
     For property type 0x4006, for example: PTP_DTC_AUINT32. Seems that
     the version of PTP we are currently using does not support
  if (value == NULL) {
    // xxx can this happen? Should we call a warning callback?
    Py_INCREF(Py_None);
    return Py_None;
  }
  */
  switch (type_) {
    case PTP_DTC_UNDEF:
      Py_INCREF(Py_None);
      return Py_None;
    case PTP_DTC_INT8:
      return PyInt_FromLong(*(char*)value);
    case PTP_DTC_UINT8:
      return PyInt_FromLong(*(unsigned char*)value);
    case PTP_DTC_INT16:
      return PyInt_FromLong(*(int16_t*)value);
    case PTP_DTC_UINT16:
      return PyInt_FromLong(*(uint16_t*)value);
    case PTP_DTC_INT32:
      return PyInt_FromLong(*(int32_t*)value);
    case PTP_DTC_UINT32:
      return PyInt_FromLong(*(uint32_t*)value);
    case PTP_DTC_INT64:
    case PTP_DTC_UINT64:
    case PTP_DTC_INT128:
    case PTP_DTC_UINT128:
    case PTP_DTC_AINT8:
    case PTP_DTC_AUINT8:
    case PTP_DTC_AINT16:
    case PTP_DTC_AUINT16:
    case PTP_DTC_AINT32:
    case PTP_DTC_AUINT32:
    case PTP_DTC_AINT64:
    case PTP_DTC_AUINT64:
    case PTP_DTC_AINT128:
    case PTP_DTC_AUINT128:
      PyErr_Format(PTPError, "Can't (yet) access properties of type %i", type_);
      return NULL;
    case PTP_DTC_STR:
      return PyString_FromString((char*)value);
    default:
      PyErr_Format(PTPError, "Unknown PTP property type %04x", type_);
      return NULL;
  }
}

static PyObject* PTPDeviceProperty_get_default_value(PyObject *obj,
                                                     void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;

  return PTPDeviceProperty_get_value(self->ptp_property.FactoryDefaultValue,
                                     self->ptp_property.DataType);
}

static PyObject* PTPDeviceProperty_get_current_value(PyObject *obj,
                                                     void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  PyObject* result;
  void *value;
  uint16_t ptp_call_result;

  ptp_call_result = ptp_getdevicepropvalue(
      &self->device->ptp_params,
      self->ptp_property.DevicePropertyCode,
      &value, self->ptp_property.DataType);
  if (ptp_call_result != PTP_RC_OK) {
    set_python_error_from_PTP_RC(&self->device->ptp_info, ptp_call_result);
    return NULL;
  }
  result = PTPDeviceProperty_get_value(value, self->ptp_property.DataType);
  // yes, even for integer values there is a corresponding malloc()
  // in ptp_unpack_DPV.
  free(value);
  return result;
}

static int PTPDeviceProperty_set_integer_value(PyObject *obj,
                                               PyObject *py_value,
                                               uint16_t type_) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  long value, lower_limit, upper_limit;
  char char_value;
  unsigned char uchar_value;
  int16_t int16_value;
  uint16_t uint16_value;
  int32_t int32_value;
  uint32_t uint32_value;
  void *transfer;
  int check_limit = 1;
  uint16_t ptp_call_result;

  value = PyInt_AsLong(py_value);
  if (PyErr_Occurred())
    return -1;
  switch (type_) {
    case PTP_DTC_INT8:
      lower_limit = -128;
      upper_limit = 127;
      char_value = value;
      transfer = &char_value;
      break;
    case PTP_DTC_UINT8:
      lower_limit = 0;
      upper_limit = 255;
      uchar_value = value;
      transfer = &uchar_value;
      break;
    case PTP_DTC_INT16:
      lower_limit = - 128 * 256;
      upper_limit = 128 * 256 - 1;
      int16_value = value;
      transfer = &int16_value;
      break;
    case PTP_DTC_UINT16:
      lower_limit = 0;
      upper_limit = 256 * 256 - 1;
      uint16_value = value;
      transfer = &uint16_value;
      break;
    case PTP_DTC_INT32:
      int32_value = value;
      transfer = &int32_value;
      check_limit = 0;
      break;
    case PTP_DTC_UINT32:
      uint32_value = value;
      transfer = &uint32_value;
      check_limit = 0;
      break;
    case PTP_DTC_INT64:
    case PTP_DTC_UINT64:
    case PTP_DTC_INT128:
    case PTP_DTC_UINT128:
      PyErr_Format(PTPError, "Can't (yet) set properties of type %i", type_);
      return -1;
    default:
      PyErr_Format(PTPError, "Can't set integer properties of type %i", type_);
      return -1;
  }
  if (check_limit && (value < lower_limit || value > upper_limit)) {
    PyErr_Format(PTPError, "Value out of range, must be between %ld and %ld",
                 lower_limit, upper_limit);
    return -1;
  }
  ptp_call_result = ptp_setdevicepropvalue(
    &self->device->ptp_params, self->ptp_property.DevicePropertyCode,
    transfer, type_);
  if (ptp_call_result != PTP_RC_OK) {
    set_python_error_from_PTP_RC(&self->device->ptp_info, ptp_call_result);
    return -1;
  }
  return 0;
}

static int PTPDeviceProperty_set_current_value(PyObject *obj,
                                               PyObject* py_value,
                                               void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  uint16_t ptp_call_result, type_ = self->ptp_property.DataType;
  // Value copied from properties.c
  // xxxx is there really a need for this length limit?
  // xxxx we can as well directly pass the pointer to the
  // Python string to ptp_setdevicepropvalue()
  #define SVALLEN 256
  char strdata[SVALLEN];
  Py_ssize_t strdata_size;

  if (py_value == NULL) {
    PyErr_SetString(PTPError, "Cannot delete the property value.");
    return -1;
  }
  if (self->ptp_property.GetSet != PTP_DPGS_GetSet) {
    PyErr_SetString(PTPError, "Property is read-only.");
    return -1;
  }
  switch (type_) {
    case PTP_DTC_UNDEF:
      PyErr_SetString(PTPError, "Cannot set property of undefined PTP type.");
      return -1;
    case PTP_DTC_INT8:
    case PTP_DTC_UINT8:
    case PTP_DTC_INT16:
    case PTP_DTC_UINT16:
    case PTP_DTC_INT32:
    case PTP_DTC_UINT32:
    case PTP_DTC_INT64:
    case PTP_DTC_UINT64:
    case PTP_DTC_INT128:
    case PTP_DTC_UINT128:
      return PTPDeviceProperty_set_integer_value(obj, py_value, type_);
    case PTP_DTC_AINT8:
    case PTP_DTC_AUINT8:
    case PTP_DTC_AINT16:
    case PTP_DTC_AUINT16:
    case PTP_DTC_AINT32:
    case PTP_DTC_AUINT32:
    case PTP_DTC_AINT64:
    case PTP_DTC_AUINT64:
    case PTP_DTC_AINT128:
    case PTP_DTC_AUINT128:
      PyErr_Format(PTPError, "Can't (yet) access properties of type %i", type_);
      return -1;
    case PTP_DTC_STR:
      if (!PyString_Check(py_value)) {
        PyErr_SetString(PTPError, "Value must be a Python string.");
        return -1;
      }
      strdata_size = PyString_Size(py_value);
      strdata_size = strdata_size < SVALLEN-1 ? strdata_size : SVALLEN-1;
      memcpy(&strdata, PyString_AsString(py_value), strdata_size);
      strdata[strdata_size] = 0;
      ptp_call_result = ptp_setdevicepropvalue(
        &self->device->ptp_params, self->ptp_property.DevicePropertyCode,
        strdata, type_);
      if (ptp_call_result != PTP_RC_OK) {
        set_python_error_from_PTP_RC(&self->device->ptp_info, ptp_call_result);
        return -1;
      }
      return 0;
    default:
      PyErr_Format(PTPError, "Unknown PTP property type %i", type_);
      return -1;
  }
  return 0;
}

static PyObject* PTPDeviceProperty_get_type(PyObject *obj, void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  return PyInt_FromLong(self->ptp_property.DataType);
}

static PyObject* PTPDeviceProperty_get_constraint(PyObject *obj,
                                                  void* closure) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  PTPDevicePropDesc *ptp_prop = &self->ptp_property;
  PyObject *result, *element;
  int i;
  void **enum_values;

  switch (self->ptp_property.FormFlag) {
    // xxx make enum class?
    case PTP_DPFF_Enumeration:
      result = PyTuple_New(self->ptp_property.FORM.Enum.NumberOfValues);
      if (result == NULL)
        return NULL;
      enum_values = ptp_prop->FORM.Enum.SupportedValue;
      for (i = 0; i < ptp_prop->FORM.Enum.NumberOfValues; i++) {
        element = PTPDeviceProperty_get_value(enum_values[i],
                                              ptp_prop->DataType);
        if (element == NULL || PyTuple_SetItem(result, i, element)) {
          Py_DECREF(result);
          return NULL;
        }
      }
      return result;

  case PTP_DPFF_Range:
    //xxxxxxx UNTESTED
    result = PyList_New(3);
    if (result == NULL)
      return NULL;

    element = PTPDeviceProperty_get_value(ptp_prop->FORM.Range.MinimumValue,
                                          ptp_prop->DataType);
    if (element == NULL) {
      Py_DECREF(result);
      return NULL;
    }
    PyList_SetItem(result, 0, element);

    element = PTPDeviceProperty_get_value(ptp_prop->FORM.Range.MaximumValue,
                                          ptp_prop->DataType);
    if (element == NULL) {
      Py_DECREF(result);
      return NULL;
    }
    PyList_SetItem(result, 1, element);

    element = PTPDeviceProperty_get_value(self->ptp_property.FORM.Range.StepSize,
                                          self->ptp_property.DataType);
    if (element == NULL) {
      Py_DECREF(result);
      return NULL;
    }
    PyList_SetItem(result, 2, element);
    return result;

  case PTP_DPFF_None:
    Py_INCREF(Py_None);
    return Py_None;

  default:
    PyErr_Format(PTPError, "Unknown constraint type: %i",
                 self->ptp_property.FormFlag);
    return NULL;
  }
}

static PyGetSetDef PTPDeviceProperty_getsetters[] = {
  {"id", (getter)PTPDeviceProperty_get_id, NULL,
   "The PTP ID of the property."},
  {"readonly", (getter)PTPDeviceProperty_get_readonly, NULL,
   "True if this is a read-only property, else False."},
  {"default", (getter)PTPDeviceProperty_get_default_value, NULL,
   "The factory default value"},
  {"value", (getter)PTPDeviceProperty_get_current_value,
   PTPDeviceProperty_set_current_value,
   "The current value"},
  {"type", (getter)PTPDeviceProperty_get_type, NULL,
   "The type of the property."},
  {"constraint", (getter)PTPDeviceProperty_get_constraint, NULL,
   "The constraint of this property.\n"
   "  Tuple: Use only values from this tuple.\n"
   "  List: [min, max, stepsize]"},
  {NULL,}
};

static PyObject*
PTPDeviceProperty_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;
  self->device = 0;
  memset(&self->ptp_property, 0, sizeof(PTPDevicePropDesc));
  return (PyObject*) self;
}

static int
PTPDeviceProperty_init(PTPDeviceProperty *self, PyObject *args,
                       PyObject *kwargs) {
  PTPDevice *device;
  int property_id;
  uint16_t rc;

  static char *kwnames[] = {"device", "id", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi", kwnames, &device,
                                   &property_id))
    return -1;

  if (!PyObject_IsInstance((PyObject*)device, (PyObject*) &PTPDeviceType)) {
    PyErr_SetString(PTPError,
                    "Need a PTPDevice object to initialize a "
                    "PTPDeviceProperty");
    return -1;
  }

  rc = ptp_getdevicepropdesc(&device->ptp_params, property_id,
                                    &self->ptp_property);
  if (rc != PTP_RC_OK) {
    set_python_error_from_PTP_RC(&device->ptp_info, rc);
    return -1;
  }

  Py_XDECREF(self->device);
  self->device = device;
  Py_INCREF(device);
  return 0;
}

static void PTPDeviceProperty_dealloc(PyObject *obj) {
  PTPDeviceProperty* self = (PTPDeviceProperty*) obj;
  free(self->ptp_property.FactoryDefaultValue);
  free(self->ptp_property.CurrentValue);
  Py_XDECREF(self->device);
}

static PyTypeObject PTPDevicePropertyType = {
  PyObject_HEAD_INIT(NULL)
  0,                                 /*ob_size*/
  "ptp.PTPDeviceProperty",           /*tp_name*/
  sizeof(PTPDeviceProperty),         /*tp_basicsize*/
  0,                                 /*tp_itemsize*/
  PTPDeviceProperty_dealloc,         /*tp_dealloc*/
  0,                                 /*tp_print*/
  0,                                 /*tp_getattr*/
  0,                                 /*tp_setattr*/
  0,                                 /*tp_compare*/
  0,                                 /*tp_repr*/
  0,                                 /*tp_as_number*/
  0,                                 /*tp_as_sequence*/
  0,                                 /*tp_as_mapping*/
  0,                                 /*tp_hash */
  0,                                 /*tp_call*/
  0,                                 /*tp_str*/
  0,                                 /*tp_getattro*/
  0,                                 /*tp_setattro*/
  0,                                 /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT,                /*tp_flags*/
  "A PTPDeviceProperty. xxx needs doc",  /* tp_doc */
  0,		                     /* tp_traverse */
  0,		                     /* tp_clear */
  0,		                     /* tp_richcompare */
  0,		                     /* tp_weaklistoffset */
  0,		                     /* tp_iter */
  0,		                     /* tp_iternext */
  0,                                 /* tp_methods */
  0,                                 /* tp_members */
  PTPDeviceProperty_getsetters,      /* tp_getset */
  0,                                 /* tp_base */
  0,                                 /* tp_dict */
  0,                                 /* tp_descr_get */
  0,                                 /* tp_descr_set */
  0,                                 /* tp_dictoffset */
  (initproc)PTPDeviceProperty_init,  /* tp_init */
  0,                                 /* tp_alloc */
  PTPDeviceProperty_new,             /* tp_new */
};
