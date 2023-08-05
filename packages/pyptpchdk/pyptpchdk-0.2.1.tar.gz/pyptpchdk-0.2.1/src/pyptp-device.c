/* Copyright Abel Deuring 2012
   python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.
 */

// 256 entries, 4 bytes each (sizeof(palette_entry_rgba_t)).
#define PALETTE_SIZE (sizeof(palette_entry_rgba_t) * 256)

// class PTPDevice.

typedef struct {
  PyObject_HEAD
  int camera_opened;
  PTPParams ptp_params;
  PTP_INFO ptp_info;
  struct usb_device* usb_dev;
  int palette_type;
  palette_entry_rgba_t *palette;
} PTPDevice;


static PyMemberDef PTPDeviceMembers[] = {
  // xxx is T_SHORT really equivalent to int16_t?
  // xxx is T_INT equivalent to int32_t?
  // xxx for "safety reason", we should move this to the computed
  // attribues. There, we can be sure that we grab a uint16_t or
  // whatever else.
  {"standard_version", T_USHORT,
   offsetof(PTPDevice, ptp_params.deviceinfo.StaqndardVersion),
   READONLY, "PTP standard version"},
  {"vendor_extension_id", T_UINT,
   offsetof(PTPDevice, ptp_params.deviceinfo.VendorExtensionID),
   READONLY, "VendorExtensionID"},
  {"vendor_extension_version", T_USHORT,
   offsetof(PTPDevice, ptp_params.deviceinfo.VendorExtensionVersion),
   READONLY, "Vendor extension version"},
  {"vendor_extension_description", T_STRING,
   offsetof(PTPDevice, ptp_params.deviceinfo.VendorExtensionDesc),
   READONLY, "Vendor extension description"},
  {"functional_mode", T_USHORT,
   offsetof(PTPDevice, ptp_params.deviceinfo.FunctionalMode),
   READONLY, "Functional mode"},
  {"vendor", T_STRING,
   offsetof(PTPDevice, ptp_params.deviceinfo.Manufacturer),
   READONLY, "Vendor name"},
  {"model", T_STRING,
   offsetof(PTPDevice, ptp_params.deviceinfo.Model),
   READONLY, "Model name"},
  {"version", T_STRING,
   offsetof(PTPDevice, ptp_params.deviceinfo.DeviceVersion),
   READONLY, "Model version"},
  {"serial_number", T_STRING,
   offsetof(PTPDevice, ptp_params.deviceinfo.SerialNumber),
   READONLY, "Device serial number"},
  {NULL,},
};

// computed attributes.

static PyObject* PTPDevice_get_supported_operations(PyObject* obj) {
  PTPDevice* self = (PTPDevice*) obj;

  return uint16_array_to_tuple(
    self->ptp_params.deviceinfo.OperationsSupported,
    self->ptp_params.deviceinfo.OperationsSupported_len);
}

static PyObject* PTPDevice_get_supported_properties(PyObject* obj) {
  PTPDevice* self = (PTPDevice*) obj;

  return uint16_array_to_tuple(
    self->ptp_params.deviceinfo.DevicePropertiesSupported,
    self->ptp_params.deviceinfo.DevicePropertiesSupported_len);
}

static PyObject* PTPDevice_get_capture_formats(PyObject* obj) {
  PTPDevice* self = (PTPDevice*) obj;

  return uint16_array_to_tuple(self->ptp_params.deviceinfo.CaptureFormats,
                               self->ptp_params.deviceinfo.CaptureFormats_len);
}

static PyObject* PTPDevice_get_image_formats(PyObject* obj) {
  PTPDevice* self = (PTPDevice*) obj;

  return uint16_array_to_tuple(self->ptp_params.deviceinfo.ImageFormats,
                               self->ptp_params.deviceinfo.ImageFormats_len);
}


static PyObject* PTPDevice_get_storage_ids(PyObject* obj) {
  PTPDevice* self = (PTPDevice*) obj;
  PTPStorageIDs storage_ids;
  uint16_t ptp_call_result;
  PyObject* result;

  if (PTP_RC_OK != (ptp_call_result = ptp_getstorageids(&self->ptp_params,
                                                        &storage_ids))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  result =  uint32_array_to_tuple(storage_ids.Storage, storage_ids.n);
  if (storage_ids.Storage)
    free(storage_ids.Storage);
  return result;
}

static PyGetSetDef PTPDevice_getsetters[] = {
  {"supported_operations", (getter)PTPDevice_get_supported_operations,
   NULL, "Supported operations"},
  {"supported_device_properties", (getter)PTPDevice_get_supported_properties,
   NULL, "Supported properties"},
  {"capture_formats", (getter)PTPDevice_get_capture_formats,
   NULL, "Capture formats"},
  {"image_formats", (getter)PTPDevice_get_image_formats,
   NULL, "Image formats"},
  {"storage_ids", (getter)PTPDevice_get_storage_ids, NULL, "Storage IDs"},
  {NULL,}
};

static PyObject*
PTPDevice_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
  PTPDevice* self = (PTPDevice*) type->tp_alloc(type, 0);
  if (self == NULL)
    return NULL;

  self->camera_opened = 0;
  memset(&self->ptp_params, 0, sizeof(PTPParams));
  memset(&self->ptp_info, 0, sizeof(PTP_INFO));
  self->usb_dev = NULL;
  self->palette = NULL;
  return (PyObject*) self;
}

static int
PTPDevice_init(PTPDevice *self, PyObject *args, PyObject *kwargs) {
  int bus = 0, device = 0, force = 0;
  static char *kwnames[] = {"bus", "device", "force", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|iii", kwnames, &bus,
                                   &device, &force))
    return -1;
  if (open_camera(bus, device, force, &self->ptp_info, &self->ptp_params,
                  &self->usb_dev)) {
    self->camera_opened = 0;
    if (self->ptp_info.error_message != NULL) {
      PyErr_SetObject(PTPError, self->ptp_info.error_message);
      Py_CLEAR(self->ptp_info.error_message);
    } else {
      // xxx Check: do we still need this variant, or is
      // self->ptp_info->error_message set for all possible errors?
      PyErr_SetString(PTPError, "Can't find a camera.");
    }
    return -1;
  }
  self->camera_opened = 1;
  return 0;
}

static void PTPDevice_dealloc(PyObject *obj) {
  PTPDevice* self = (PTPDevice*) obj;
  if (self->camera_opened)
    close_camera(&self->ptp_info, &self->ptp_params, self->usb_dev);
  if (self->palette != NULL)
    free(self->palette);
  Py_XDECREF(self->ptp_info.error_message);
}

static PyTypeObject PTPDevicePropertyType;

static PyObject* getDeviceProperty(PyObject* obj, PyObject *args) {
  PyObject *args2, *index, *result;

  if (!PyArg_ParseTuple(args, "O", &index))
    return NULL;
  args2 = PyTuple_Pack(2, obj, index);
  if (args2 == NULL)
    return NULL;

  result = PyObject_CallObject((PyObject *) &PTPDevicePropertyType, args2);
  Py_DECREF(args2);
  return result;
}

static PyObject* getStorageInfo(PyObject* obj, PyObject *args) {
  PTPDevice* self = (PTPDevice*) obj;
  uint32_t storage_id;
  uint16_t ptp_call_result;
  PTPStorageInfo info;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "i", &storage_id))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_getstorageinfo(&self->ptp_params,
                                                         storage_id,
                                                         &info))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  result = PyDict_New();
  if (result == NULL)
    return 0;

  set_dict_int_item(result, "storage_type", info.StorageType);
  set_dict_int_item(result, "file_system_type", info.FilesystemType);
  set_dict_int_item(result, "access_capability", info.AccessCapability);
  set_dict_int_item(result, "max_capability", info.MaxCapability);
  set_dict_int_item(result, "free_space_in_bytes", info.FreeSpaceInBytes);
  set_dict_int_item(result, "free_space_in_images", info.FreeSpaceInImages);
  if (info.StorageDescription) {
    set_dict_string_item(result, "description", info.StorageDescription);
    free(info.StorageDescription);
  }
  if (info.VolumeLabel) {
    set_dict_string_item(result, "volume_label", info.VolumeLabel);
    free(info.VolumeLabel);
  }
  return result;
}

static PyObject* getObjectHandles(PyObject* obj, PyObject* args,
                                              PyObject* kwargs) {
  PTPDevice* self = (PTPDevice*) obj;
  PTPObjectHandles handles;
  uint16_t ptp_call_result;
  uint32_t storage, format_code = 0, association_handle = 0;
  PyObject* result;

  static char *kwnames[] = {"storage", "format_code", "association_handle",
                            NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "i|ii", kwnames, &storage,
                                   &format_code, association_handle))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_getobjecthandles(&self->ptp_params,
                                                           storage,
                                                           format_code,
                                                           association_handle,
                                                           &handles))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  result = uint32_array_to_tuple(handles.Handler, handles.n);
  if (handles.Handler)
    free(handles.Handler);
  return result;
}

static PyObject* getObjectInfo(PyObject* obj, PyObject* args) {
  PTPDevice* self = (PTPDevice*) obj;
  PTPObjectInfo object_info;
  uint32_t object_handle;
  uint16_t ptp_call_result;
  PyObject *result, *item;

  // Seems that the libptp version we curently use does not set
  // object_handle.Keywords. Make sure that we have a proper NULL pointer.
  memset(&object_info, 0, sizeof(object_info));

  if (!PyArg_ParseTuple(args, "i", &object_handle))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_getobjectinfo(&self->ptp_params,
                                                       object_handle,
                                                        &object_info))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  result = PyDict_New();
  if (result == NULL)
    return 0;

  set_dict_int_item(result, "storage_id", object_info.StorageID);
  set_dict_int_item(result, "object_format", object_info.ObjectFormat);
  set_dict_int_item(result, "protection_status", object_info.ProtectionStatus);
  set_dict_int_item(result, "compressed_size",
                    object_info.ObjectCompressedSize);
  set_dict_int_item(result, "thumb_format", object_info.ThumbFormat);
  set_dict_int_item(result, "thumb_compressed_size",
                    object_info.ThumbCompressedSize);
  set_dict_int_item(result, "thumb_pix_width", object_info.ThumbPixWidth);
  set_dict_int_item(result, "thumb_pix_height", object_info.ThumbPixHeight);
  set_dict_int_item(result, "image_pix_width", object_info.ImagePixWidth);
  set_dict_int_item(result, "image_pix_height", object_info.ImagePixHeight);
  set_dict_int_item(result, "image_bit_depth", object_info.ImageBitDepth);
  set_dict_int_item(result, "parent_object", object_info.ParentObject);
  set_dict_int_item(result, "association_type", object_info.AssociationType);
  set_dict_int_item(result, "association_desc", object_info.AssociationDesc);
  set_dict_int_item(result, "sequence_number", object_info.SequenceNumber);
  if (object_info.Filename) {
    set_dict_string_item(result, "filename", object_info.Filename);
    // xxx this is a memory leak when set_dict_item_from_string() fails
    free(object_info.Filename);
  }
  if (object_info.Keywords) {
    set_dict_string_item(result, "keywords", object_info.Keywords);
    // xxx this is a memory leak when set_dict_item_from_string() fails
    free(object_info.Keywords);
  }
  if (NULL == (item = time_t_to_datetime(&object_info.CaptureDate))) {
    Py_DECREF(result);
    return NULL;
  }
  if (PyDict_SetItemString(result, "capture_date", item)) {
    Py_DECREF(item);
    Py_DECREF(result);
    return NULL;
  }
  Py_DECREF(item);
  if (NULL == (item = time_t_to_datetime(&object_info.ModificationDate))) {
    Py_DECREF(result);
    return NULL;
  }
  if (PyDict_SetItemString(result, "modification_date", item)) {
    Py_DECREF(item);
    Py_DECREF(result);
    return NULL;
  }
  Py_DECREF(item);
  return result;
}

static PyObject* getObject(PyObject* obj, PyObject* args) {
  PTPDevice *self = (PTPDevice*) obj;
  PTPObjectInfo object_info;
  uint32_t object_handle;
  uint16_t ptp_call_result;
  char *object_data = NULL;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "i", &object_handle))
    return NULL;

  // We need the size of the object. xxx should we cache PTPObjectInfo
  // instances??
  memset(&object_info, 0, sizeof(object_info));
  if (PTP_RC_OK != (ptp_call_result = ptp_getobjectinfo(&self->ptp_params,
                                                       object_handle,
                                                        &object_info))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  if (object_info.Filename)
    free(object_info.Filename);
  if (object_info.Keywords)
    free(object_info.Keywords);

  /* xxx from looking at callsites of ptp_getobject() in other applications
     and libraries, it seems that we don't need to free(object_data).
     Is this really correct?

     ptp_object() just calls ptp_transaction(), and the documentation
     of the latter function is somewhat enigmatic:

        The memory for a pointer should be preserved by the caller, if data are
        beeing retreived the appropriate amount of memory is beeing allocated

     ptp_transaction() itself does not do any memory management. In the
     case of a READ transaction, it calls params->getdata_func(). This
     is in turn defined here to be ptp_usb_getdata(). And that method
     allocates a new buffer for the data to read if passed a NULL pointer.

     The amount of memory allocated and the amount of data stored
     there is determined by usbdata.length, i.e., it comes ultimately
     from the device. Hence the idea to use the size information from
     object_info in PyString_FromStringAndSize() below is a call for
     trouble: If the device sends less data, we might get a nice
     segfault. Is this also a potential security problem?

     preliminary conclusion:
     - free() the memory
     - patch ptp_usb_getdata() to return the amount of data read too.
  */
  if (PTP_RC_OK != (ptp_call_result = ptp_getobject(&self->ptp_params,
                                                    object_handle,
                                                    &object_data))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  result = PyString_FromStringAndSize(object_data,
                                      object_info.ObjectCompressedSize);
  free(object_data);
  return result;
}

static PyObject* getThumbnail(PyObject* obj, PyObject* args) {
  PTPDevice *self = (PTPDevice*) obj;
  PTPObjectInfo object_info;
  uint32_t object_handle;
  uint16_t ptp_call_result;
  char *object_data = NULL;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "i", &object_handle))
    return NULL;

  // We need the size of the object. xxx should we cache PTPObjectInfo
  // instances??
  memset(&object_info, 0, sizeof(object_info));
  if (PTP_RC_OK != (ptp_call_result = ptp_getobjectinfo(&self->ptp_params,
                                                       object_handle,
                                                        &object_info))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  if (object_info.Filename)
    free(object_info.Filename);
  if (object_info.Keywords)
    free(object_info.Keywords);

  // xxx see getObject()
  if (PTP_RC_OK != (ptp_call_result = ptp_getthumb(&self->ptp_params,
                                                   object_handle,
                                                   &object_data))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  result = PyString_FromStringAndSize(object_data,
                                      object_info.ThumbCompressedSize);
  free(object_data);
  return result;
}

static PyObject* chdkUpload(PyObject* obj, PyObject* args, PyObject* kwargs) {
  PTPDevice *self = (PTPDevice*) obj;
  static char *kwnames[] = {"local_file", "remote_file", NULL};
  char *local_file, *remote_file;
  uint16_t ptp_call_result;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss", kwnames, &local_file,
                                   &remote_file))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_chdk_upload(
      local_file, remote_file,
      &self->ptp_params,
      &self->ptp_params.deviceinfo))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* chdkUploadString(PyObject* obj, PyObject* args,
                                  PyObject* kwargs) {
  PTPDevice *self = (PTPDevice*) obj;
  static char *kwnames[] = {"data", "remote_file", NULL};
  char *data, *remote_file;
  int data_size;
  uint16_t ptp_call_result;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#s", kwnames, &data,
                                   &data_size, &remote_file))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_chdk_upload_string(
      data, data_size, remote_file, &self->ptp_params,
      &self->ptp_params.deviceinfo))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* chdkDownloadString(PyObject* obj, PyObject* args,
                                    PyObject* kwargs) {
  PTPDevice *self = (PTPDevice*) obj;
  static char *kwnames[] = {"remote_file", NULL};
  char *remote_file, *data;
  uint16_t ptp_call_result;
  int data_size;
  PyObject *result;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s", kwnames, &remote_file))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_chdk_download_string(
      remote_file, &data, &data_size, &self->ptp_params,
      &self->ptp_params.deviceinfo))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  result = PyString_FromStringAndSize(data, data_size);
  free(data);

  return result;
}

static PyObject* chdkDownload(PyObject* obj, PyObject* args, PyObject* kwargs) {
  PTPDevice *self = (PTPDevice*) obj;
  static char *kwnames[] = {"remote_file", "local_file", NULL};
  char *local_file, *remote_file;
  uint16_t ptp_call_result;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss", kwnames, &remote_file,
                                   &local_file))
    return NULL;

  if (PTP_RC_OK != (ptp_call_result = ptp_chdk_download(
      remote_file, local_file,
      &self->ptp_params,
      &self->ptp_params.deviceinfo))) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* chdkExecLua(PyObject* obj, PyObject* args) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  char *script;
  uint32_t script_id;

  if (!PyArg_ParseTuple(args, "s", &script))
    return NULL;

  ptp_call_result = ptp_start_lua(script, &script_id, &self->ptp_params);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  return PyInt_FromLong(script_id);
}

static PyObject* chdkScriptStatus(PyObject* obj, PyObject* args) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  uint32_t script_id;
  int script_status;

  if (!PyArg_ParseTuple(args, "i", &script_id))
    return NULL;

  ptp_call_result = ptp_chdk_get_script_status(&self->ptp_params,
                                               &script_status);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  return PyInt_FromLong(script_status);
}

static PyObject* chdkScriptSupport(PyObject* obj) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  int script_support;

  ptp_call_result = ptp_chdk_get_script_support(&self->ptp_params,
                                                &script_support);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  return PyInt_FromLong(script_support);
}

static PyObject* chdkGetPTPVersion(PyObject* obj) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  int major, minor;
  PyObject *py_major, *py_minor;
  PyObject *result;

  ptp_call_result = ptp_chdk_get_version(&self->ptp_params, &major, &minor);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  if (NULL == (py_major = PyInt_FromLong(major)))
    return NULL;

  if (NULL == (py_minor = PyInt_FromLong(minor))) {
    Py_DECREF(py_major);
    return NULL;
  }

  result = PyTuple_Pack(2, py_major, py_minor);
  Py_DECREF(py_major);
  Py_DECREF(py_minor);
  return result;
}

static PyObject* chdkReadScriptMessage(PyObject* obj) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  ptp_chdk_script_msg* msg;
  PyObject *result, *result_value, *result_type, *script_id;

  ptp_call_result = ptp_chdk_read_script_msg(&self->ptp_params, &msg);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  result_type = PyInt_FromLong(msg->type);
  if (result_type == NULL) {
    free(msg);
    return NULL;
  }

  script_id = PyInt_FromLong(msg->script_id);
  if (script_id == NULL) {
    Py_DECREF(result_type);
    free(msg);
    return NULL;
  }

  switch (msg->type) {
    case PTP_CHDK_S_MSGTYPE_NONE:
      Py_INCREF(Py_None);
      result_value = Py_None;
      break;
    case PTP_CHDK_S_MSGTYPE_ERR: {
      static char runtime_error[] = "runtime error: ";
      static char syntax_error[] = "syntax error: ";
      char* errmsg = malloc(msg->size + 20);
      int errlen;
      if (errmsg == NULL) {
        free(msg);
        Py_DECREF(result_type);
        Py_DECREF(script_id);
        PyErr_SetString(PyExc_MemoryError, "malloc() failed.");
        return NULL;
      }

      if (msg->subtype == PTP_CHDK_S_ERRTYPE_RUN) {
        strcpy(errmsg, runtime_error);
        errlen = strlen(runtime_error);
      }
      else {
        strcpy(errmsg, syntax_error);
        errlen = strlen(syntax_error);
      }
      memcpy(&errmsg[errlen], msg->data, msg->size);
      result_value = PyString_FromStringAndSize(errmsg, errlen + msg->size);
      if (result_value == NULL) {
        Py_DECREF(result_type);
        Py_DECREF(script_id);
        free(msg);
        return NULL;
      }
      break;
    }
    case PTP_CHDK_S_MSGTYPE_RET:
    case PTP_CHDK_S_MSGTYPE_USER:
      switch (msg->subtype) {
        case PTP_CHDK_TYPE_NIL:
          Py_INCREF(Py_None);
          result_value = Py_None;
          break;

        case PTP_CHDK_TYPE_BOOLEAN:
          result_value = PyBool_FromLong(*(int32_t*)msg->data);
          break;

        case PTP_CHDK_TYPE_INTEGER:
          result_value = PyInt_FromLong(*(int32_t*)msg->data);
          break;

          // xxx PTP_CHDK_TYPE_UNSUPPORTED, PTP_CHDK_TYPE_TABLE should be
          // treated differently!
        case PTP_CHDK_TYPE_UNSUPPORTED:
        case PTP_CHDK_TYPE_TABLE:
        case PTP_CHDK_TYPE_STRING:
          result_value = PyString_FromStringAndSize(msg->data, msg->size);
          break;

        default:
          {
            PyErr_Format(PTPError, "Unknown message subtype: %i", msg->subtype);
            result_value = NULL;
          }
      }
      break;
    default:
      PyErr_Format(PTPError, "Unknown CHDK message type: %i", msg->type);
      result_value = NULL;
  }


  free(msg);
  if (result_value == NULL) {
    Py_DECREF(result_type);
    Py_DECREF(script_id);
    return NULL;
  }
  result = PyTuple_Pack(3, result_value, result_type, script_id);
  Py_DECREF(result_value);
  Py_DECREF(result_type);
  Py_DECREF(script_id);
  return result;
}

static PyObject* chdkWriteScriptMessage(PyObject* obj, PyObject* args) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  PyObject *py_data;
  char *data;
  int script_id, status;
  Py_ssize_t data_size;

  if (!PyArg_ParseTuple(args, "Oi", &py_data, &script_id))
    return NULL;
  if (!PyString_Check(py_data)) {
    PyErr_SetString(PyExc_TypeError,
                    "Only strings can be sent to a PTPDevice.");
    return NULL;
  }
  if (PyString_AsStringAndSize(py_data, &data, &data_size)) {
    return NULL;
  }

  ptp_call_result = ptp_chdk_write_script_msg(&self->ptp_params, data,
                                              data_size, script_id, &status);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  return PyInt_FromLong(status);
}

// The next three functions are modified variants of those from chdkptp.
static inline uint8_t yuv_to_r_2(int y, int v) {
  return clip_yuv((y + v + 2048)>>12);
}

static inline uint8_t yuv_to_g_2(int y, int u, int v) {
  return clip_yuv((y - u - v + 2048)>>12);
}

static inline uint8_t yuv_to_b_2(int y, int u) {
  return clip_yuv((y + u + 2048)>>12);
}

/* Process viewport data.
   On success: Returns a Python dictionary
   {'data': string_with_rgb_data,
    'height': int_height_of_image,
    'width': int_width_of_image}
   On error, a Python exception is set and NULL returned.
 */
static PyObject* get_vp_data(lv_data_header* data, unsigned data_size,
                             int flags) {
  PyObject *result = NULL, *temp = NULL;
  lv_framebuffer_desc *fb_info;
  int buffer_inc, x, y, rgb_size, bytes_per_line, image_width, image_height;
  char *rgb_img, *rgb_ptr, *rgb_line_start;
  signed char *yuv_img, *yuv_ptr;

  if (data->vp_desc_start + sizeof(lv_framebuffer_desc) > data_size) {
    PyErr_SetString(PTPError,
                    "viewport framebuffer description beyond end of "
                    "transferred data");
    return NULL;
  }
  fb_info = (lv_framebuffer_desc*)((char*)data + data->vp_desc_start);
  if (fb_info->fb_type != LV_FB_YUV8) {
    PyErr_Format(PTPError,
                 "Unknown or invalid viewport data type: %i (expected %i).",
                 fb_info->fb_type, LV_FB_YUV8);
    return NULL;
  }
  // XXX assert that buffer_width is indeed an even number?
  // We have 12 bit per pixel.
  buffer_inc = fb_info->buffer_width * 12 / 8;
  // We may have no viewport data at all, or it may be incomplete.
  if (fb_info->data_start <= 0 ||
      fb_info->data_start + buffer_inc * fb_info->visible_height > data_size) {
    PyErr_Format(PTPError,
                 "Incomplete viewport buffer: data_start %i buffer_inc %i "
                 "visible_height %i data_size %i.",
                 fb_info->data_start, buffer_inc, fb_info->visible_height,
                 data_size);
    return NULL;
  }
  if (fb_info->visible_width > fb_info->buffer_width) {
    PyErr_Format(PTPError,
                 "Viewport's visible width (%i) is larger than the "
                 "buffer_width (%i)",
                 fb_info->visible_width, fb_info->buffer_width);
    return NULL;
  }

  flags &= (LV_TFR_DOUBLE_VIEWPORT_LINES | LV_TFR_SHRINK_VIEWPORT_LINES);
  switch (flags) {
  case LV_TFR_DOUBLE_VIEWPORT_LINES:
    rgb_size = fb_info->visible_width * fb_info->visible_height * 6;
    bytes_per_line = fb_info->visible_width * 3;
    image_width = fb_info->visible_width;
    image_height = fb_info->visible_height * 2;
    break;
  case LV_TFR_SHRINK_VIEWPORT_LINES:
    // drop 2 of four input pixels.
    rgb_size = fb_info->visible_width * fb_info->visible_height * 3 / 2;
    bytes_per_line = fb_info->visible_width * 3 / 2;
    image_width = fb_info->visible_width / 2;
    image_height = fb_info->visible_height;
    break;
  case LV_TFR_DOUBLE_VIEWPORT_LINES | LV_TFR_SHRINK_VIEWPORT_LINES:
    // drop 2 of four input pixels and double each line.
    rgb_size = fb_info->visible_width * fb_info->visible_height * 3;
    bytes_per_line = fb_info->visible_width * 3 / 2;
    image_width = fb_info->visible_width / 2;
    image_height = fb_info->visible_height * 2;
    break;
  default:
    // no size changes
    rgb_size = fb_info->visible_width * fb_info->visible_height * 3;
    bytes_per_line = fb_info->visible_width * 3;
    image_width = fb_info->visible_width;
    image_height = fb_info->visible_height;
  }

  rgb_img = malloc(rgb_size);
  if (rgb_img == NULL) {
    PyErr_SetString(PyExc_MemoryError, "malloc() failed.");
    return NULL;
  }
  rgb_ptr = rgb_img;
  yuv_img = (char*) data + fb_info->data_start;

  // y << 12 only once.
  // v * 5743 only once -> 10000 loops: 5.13 sec
  // u * 1411 only once -> 10000 loops: 4.96 sec
  // v * 2925 only once -> 10000 loops: 4.86 sec
  // u * 7258 only once -> 10000 loops: 4.58 sec
  for (y = 0; y < fb_info->visible_height; y++) {
    yuv_ptr = yuv_img + y * buffer_inc;
    rgb_line_start = rgb_ptr;
    for (x = 0; x < fb_info->visible_width; x += 4) {
      int v_5743 = yuv_ptr[2] * 5743;
      int v_2925 = yuv_ptr[2] * 2925;
      int u_1411 = yuv_ptr[0] * 1411;
      int u_7258 = yuv_ptr[0] * 7258;
      int lum = ((uint8_t*)yuv_ptr)[1];
      lum = lum << 12;
      *rgb_ptr++ = yuv_to_r_2(lum, v_5743);
      *rgb_ptr++ = yuv_to_g_2(lum, u_1411, v_2925);
      *rgb_ptr++ = yuv_to_b_2(lum, u_7258);

      lum = ((uint8_t*)yuv_ptr)[3];
      lum = lum << 12;
      *rgb_ptr++ = yuv_to_r_2(lum, v_5743);
      *rgb_ptr++ = yuv_to_g_2(lum, u_1411, v_2925);
      *rgb_ptr++ = yuv_to_b_2(lum, u_7258);

      if ((flags & LV_TFR_SHRINK_VIEWPORT_LINES) == 0) {
        lum = ((uint8_t*)yuv_ptr)[4];
        lum = lum << 12;
        *rgb_ptr++ = yuv_to_r_2(lum, v_5743);
        *rgb_ptr++ = yuv_to_g_2(lum, u_1411, v_2925);
        *rgb_ptr++ = yuv_to_b_2(lum, u_7258);

        lum = ((uint8_t*)yuv_ptr)[5];
        lum = lum << 12;
        *rgb_ptr++ = yuv_to_r_2(lum, v_5743);
        *rgb_ptr++ = yuv_to_g_2(lum, u_1411, v_2925);
        *rgb_ptr++ = yuv_to_b_2(lum, u_7258);
      }
      yuv_ptr += 6;
    }
    if (flags & LV_TFR_DOUBLE_VIEWPORT_LINES) {
      memcpy(rgb_ptr, rgb_line_start, bytes_per_line);
      rgb_ptr += bytes_per_line;
    }
  }

  if (NULL == (result = PyDict_New())) {
    free(rgb_img);
    return NULL;
  }
  if (NULL == (temp = PyString_FromStringAndSize(rgb_img, rgb_size))) {
    Py_DECREF(result);
    free(rgb_img);
    return NULL;
  }
  if (PyDict_SetItemString(result, "data", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(rgb_img);
    return NULL;
  }
  Py_DECREF(temp);
  if (NULL == (temp = PyInt_FromLong(image_width))) {
    Py_DECREF(result);
    free(rgb_img);
    return NULL;
  }
  if (PyDict_SetItemString(result, "width", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(rgb_img);
    return NULL;
  }
  Py_DECREF(temp);
  if (NULL == (temp = PyInt_FromLong(image_height))) {
    Py_DECREF(result);
    free(rgb_img);
    return NULL;
  }
  if(PyDict_SetItemString(result, "height", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(rgb_img);
    return NULL;
  }
  Py_DECREF(temp);
  free(rgb_img);
  return result;
}

/* Process bitmap data.
   On success: Returns a Python dictionary
   {'data': string_with_rgb_data,
    'height': int_height_of_image,
    'width': int_width_of_image}
   On error, a Python exception is set and NULL returned.
 */
static PyObject* get_bm_data(PTPDevice *self, lv_data_header* data,
                             unsigned data_size, int flags) {
  PyObject *result = NULL, *temp = NULL;
  lv_framebuffer_desc *fb_info;
  unsigned char *rgba_img, *rgba_ptr, *rgba_line_start, *palette_img;
  int buffer_inc, rgba_size, x, y, bytes_per_line, image_width, image_height,
    x_incr;

  if (data->bm_desc_start + sizeof(lv_framebuffer_desc) > data_size) {
    PyErr_SetString(PTPError,
                    "bitmap framebuffer description beyond end of "
                    "transferred data");
    return NULL;
  }
  fb_info = (lv_framebuffer_desc*)((char*)data + data->bm_desc_start);
  if (fb_info->fb_type != LV_FB_PAL8) {
    PyErr_Format(PTPError,
                 "Unknown or invalid bitmap data type: %i (expected %i).",
                 fb_info->fb_type, LV_FB_PAL8);
    return NULL;
  }
  buffer_inc = fb_info->buffer_width;
  if (fb_info->data_start <= 0 ||
      fb_info->data_start + buffer_inc * fb_info->visible_height > data_size) {
    PyErr_Format(PTPError,
                 "Incomplete bitmap buffer: data_start %i buffer_inc %i "
                 "visible_height %i data_size %i.",
                 fb_info->data_start, buffer_inc, fb_info->visible_height,
                 data_size);
    return NULL;
  }
  if (fb_info->visible_width > fb_info->buffer_width) {
    PyErr_Format(PTPError,
                 "Bitmap's visible width (%i) is larger than the "
                 "buffer_width (%i)",
                 fb_info->visible_width, fb_info->buffer_width);
    return NULL;
  }

  if (self->palette == NULL) {
    // If the palette has not yet been generated, we need it now.
    self->palette = malloc(PALETTE_SIZE);
    if (self->palette == NULL) {
      PyErr_SetString(PyExc_MemoryError, "malloc() failed.");
      return NULL;
    }
    // If the camera did not send any palette data, a default palette will
    // be used.
    convert_palette(self->palette, data);
  }

  flags &= (LV_TFR_DOUBLE_BITMAP_LINES | LV_TFR_SHRINK_BITMAP_LINES);
  switch (flags) {
  case LV_TFR_DOUBLE_BITMAP_LINES:
    rgba_size = fb_info->visible_width * fb_info->visible_height * 4 * 2;
    bytes_per_line = fb_info->visible_width * 4;
    image_width = fb_info->visible_width;
    image_height = fb_info->visible_height * 2;
    x_incr = 1;
    break;
  case LV_TFR_SHRINK_BITMAP_LINES:
    // drop 2 of four input pixels.
    rgba_size = fb_info->visible_width * fb_info->visible_height * 4 / 2;
    bytes_per_line = fb_info->visible_width * 4 / 2;
    image_width = fb_info->visible_width / 2;
    image_height = fb_info->visible_height;
    x_incr = 2;
    break;
  case LV_TFR_DOUBLE_BITMAP_LINES | LV_TFR_SHRINK_BITMAP_LINES:
    // drop 2 of four input pixels and double each line.
    rgba_size = fb_info->visible_width * fb_info->visible_height * 4;
    bytes_per_line = fb_info->visible_width * 4 / 2;
    image_width = fb_info->visible_width / 2;
    image_height = fb_info->visible_height * 2;
    x_incr = 2;
    break;
  default:
    // no size changes
    rgba_size = fb_info->visible_width * fb_info->visible_height * 4;
    bytes_per_line = fb_info->visible_width * 4;
    image_width = fb_info->visible_width;
    image_height = fb_info->visible_height;
    x_incr = 1;
  }

  rgba_img = malloc(rgba_size);
  if (rgba_img == NULL) {
    PyErr_SetString(PyExc_MemoryError, "malloc() failed.");
    return NULL;
  }
  rgba_ptr = rgba_img;

  palette_img = (unsigned char*) data + fb_info->data_start;

  for (y = 0; y < fb_info->visible_height; y++) {
    rgba_line_start = rgba_ptr;
    for (x = 0; x < fb_info->visible_width; x += x_incr) {
      palette_entry_rgba_t *p_entry = &(self->palette[palette_img[x]]);
      *rgba_ptr++ = p_entry->r;
      *rgba_ptr++ = p_entry->g;
      *rgba_ptr++ = p_entry->b;
      *rgba_ptr++ = p_entry->a;
    }
    if (flags & LV_TFR_DOUBLE_BITMAP_LINES) {
      memcpy(rgba_ptr, rgba_line_start, bytes_per_line);
      rgba_ptr += bytes_per_line;
    }
    palette_img += fb_info->buffer_width;
  }

  if (NULL == (result = PyDict_New())) {
    free(rgba_img);
    return NULL;
  }
  if (NULL == (temp = PyString_FromStringAndSize((char*) rgba_img,
                                                 rgba_size))) {
    Py_DECREF(result);
    free(rgba_img);
    return NULL;
  }
  if (PyDict_SetItemString(result, "data", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(rgba_img);
    return NULL;
  }
  Py_DECREF(temp);
  if (NULL == (temp = PyInt_FromLong(image_width))) {
    Py_DECREF(result);
    free(rgba_img);
    return NULL;
  }
  if(PyDict_SetItemString(result, "width", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(rgba_img);
    return NULL;
  }
  Py_DECREF(temp);
  if (NULL == (temp = PyInt_FromLong(image_height))) {
    Py_DECREF(result);
    free(rgba_img);
    return NULL;
  }
  if (PyDict_SetItemString(result, "height", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(rgba_img);
    return NULL;
  }
  Py_DECREF(temp);
  free(rgba_img);
  return result;
}

static PyObject* chdkGetLiveData(PyObject* obj, PyObject* args) {
  PTPDevice *self = (PTPDevice*) obj;
  uint16_t ptp_call_result;
  int flags, palette_start, palette_end;
  lv_data_header *data;
  unsigned data_size;
  PyObject *result = NULL, *temp = NULL;

  if (!PyArg_ParseTuple(args, "i", &flags))
    return NULL;
  if (self->palette == NULL)
    flags |= LV_TFR_PALETTE;
  ptp_call_result = ptp_chdk_get_live_data(&self->ptp_params,
                                           &self->ptp_params.deviceinfo,
                                           flags, (char**) &data, &data_size);
  if (PTP_RC_OK != ptp_call_result) {
    set_python_error_from_PTP_RC(&self->ptp_info, ptp_call_result);
    return NULL;
  }

  // Note: The SX100 for example does not return any palette data.
  // (at least CHDK 1.1.0, build 2320)
  if ((flags & LV_TFR_PALETTE) &&
      (data->palette_data_start >= sizeof(lv_data_header))) {
    palette_start = data->palette_data_start;
    palette_end = palette_start + PALETTE_SIZE;
    if (palette_end > data_size) {
      PyErr_SetString(PTPError,
                      "palette buffer beyond end of transferred data");
        free(data);
        return NULL;
    }
    self->palette_type = data->palette_type;
    if (self->palette == NULL) {
      self->palette = malloc(PALETTE_SIZE);
      if (self->palette == NULL) {
        PyErr_SetString(PyExc_MemoryError, "malloc() failed.");
        free(data);
        return NULL;
      }
    }
    convert_palette(self->palette, data);
  }
  if (NULL == (result = PyDict_New())) {
    free(data);
    return NULL;
  }
  if (NULL == (temp = PyInt_FromLong(data->version_major))) {
    Py_DECREF(result);
    free(data);
    return NULL;
  }
  if (PyDict_SetItemString(result, "version_major", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(data);
    return NULL;
  }
  Py_DECREF(temp);
  if (NULL == (temp = PyInt_FromLong(data->version_minor))) {
    Py_DECREF(result);
    free(data);
    return NULL;
  }
  if (PyDict_SetItemString(result, "version_minor", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(data);
    return NULL;
  }
  Py_DECREF(temp);
  if (NULL == (temp = PyInt_FromLong(data->lcd_aspect_ratio))) {
    Py_DECREF(result);
    free(data);
    return NULL;
  }
  if (PyDict_SetItemString(result, "lcd_aspect_ratio", temp)) {
    Py_DECREF(temp);
    Py_DECREF(result);
    free(data);
    return NULL;
  }
  Py_DECREF(temp);

  if (flags & LV_TFR_VIEWPORT) {
    if (NULL == (temp = get_vp_data(data, data_size, flags))) {
      Py_DECREF(result);
      free(data);
      return NULL;
    }
    if (PyDict_SetItemString(result, "viewport", temp)) {
      Py_DECREF(temp);
      Py_DECREF(result);
      free(data);
      return NULL;
    }
    Py_DECREF(temp);
  }
  if (flags & LV_TFR_BITMAP) {
    if (NULL == (temp = get_bm_data(self, data, data_size, flags))) {
      Py_DECREF(result);
      free(data);
      return NULL;
    }
    if (PyDict_SetItemString(result, "bitmap", temp)) {
      Py_DECREF(temp);
      Py_DECREF(result);
      free(data);
      return NULL;
    }
    Py_DECREF(temp);
  }

  free(data);
  return result;
}


static PyMethodDef PTPDevice_methods[] = {
  {"getDeviceProperty", getDeviceProperty, METH_VARARGS,
   "Retrieve a device property. xxx describe params"},
  {"getStorageInfo", getStorageInfo, METH_VARARGS,
   "Return a dictionary with details about the storage with the given ID."},
  {"getObjectHandles", (PyCFunction)getObjectHandles,
   METH_VARARGS | METH_KEYWORDS,
   "Return a tuple of object IDs.\n\n"
   "  parameter storage: A storage ID.\n"
   "  parameter format_code (optional): ???\n"
   "  parameter association_handle (optional): ???"},
  {"getObjectInfo", getObjectInfo, METH_VARARGS,
   "Return a dictionary with details about the object with the given ID."},
  {"getObject", getObject, METH_VARARGS,
   "Return an object, represented as a string."},
  {"getThumbnail", getThumbnail, METH_VARARGS,
   "Return the thumbnail of an image."},
  {"chdkUpload", (PyCFunction)chdkUpload, METH_VARARGS | METH_KEYWORDS,
   "Upload a file to the device.\n\n"
   "  parameter local_file: The name of the local file.\n"
   "  parameter remote_file: The name of the remote file.\n"
   "  (Only usable on Canon cameras having CHDK installed.)"},
  {"chdkUploadString", (PyCFunction)chdkUploadString,
   METH_VARARGS | METH_KEYWORDS,
   "Upload a string to a file on the device.\n\n"
   "  parameter data: A string containing the data to be uploaded..\n"
   "  parameter remote_file: The name of the remote file.\n"
   "  (Only usable on Canon cameras having CHDK installed.)"},
  {"chdkDownload", (PyCFunction)chdkDownload, METH_VARARGS | METH_KEYWORDS,
   "Download a file from the device.\n\n"
   "  parameter remote_file: The name of the remote file.\n"
   "  parameter local_file: The name of the local file.\n"
   "  (Only usable on Canon cameras having CHDK installed.)"},
  {"chdkDownloadString", (PyCFunction)chdkDownloadString,
   METH_VARARGS | METH_KEYWORDS,
   "Download a file from the device.\n\n"
   "  parameter remote_file: The name of the remote file.\n\n"
   "  Returns a string with the file content.\n"
   "  (Only usable on Canon cameras having CHDK installed.)"},
  {"chdkExecLua", chdkExecLua, METH_VARARGS,
   "Execute a Lua script.\n\n"
   "Returns the script ID.\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {"chdkScriptStatus", (PyCFunction)chdkScriptStatus, METH_VARARGS,
   "Poll the script status.\n\n"
   "parameter script_id: The script ID (Ignored....)\n"
   "Return: xxx doc missing.\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {"chdkScriptSupport", (PyCFunction)chdkScriptSupport, METH_NOARGS,
   "The script support status of the camera.\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {"chdkGetPTPVersion", (PyCFunction)chdkGetPTPVersion, METH_NOARGS,
   "The version number of CHDK's PTP support (major, minor).\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {"chdkReadScriptMessage", (PyCFunction)chdkReadScriptMessage, METH_NOARGS,
   "Read a script message.\n\n"
   "Returns a tuple (data, type, script_id), where type is a message type\n"
   "as defined in ptp.CHDKMessageType.\n"
   "NOTE: Unsupported data types and Lua tables are silently returned as\n"
   " a string.\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {"chdkWriteScriptMessage", chdkWriteScriptMessage, METH_VARARGS,
   "Write a script message.\n\n"
   "Parameters: message, script_id.\n"
   "Only strings may be sent to the device.\n"
   "Returns a status code.\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {"chdkGetLiveData", chdkGetLiveData, METH_VARARGS,
   "Get preview data.\n\n"
   "Return: A dictionary with the keys version_major, version_minor,\n"
   "    lcd_aspect_ratio and optionally the keys viewport and bitmap.\n"
   "    result['viewport'], is a dictionary with the keys data, width,\n"
   "    height.\n"
   "Parameter: flags.\n"
   "flags should be a bitwise OR combination of constants defined in\n"
   "ptp.LiveViewFlags.\n"
   "(Only usable on Canon cameras having CHDK installed.)"},
  {NULL}
};

static PyTypeObject PTPDeviceType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "ptp.PTPDevice",           /*tp_name*/
  sizeof(PTPDevice),         /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  PTPDevice_dealloc,         /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT,        /*tp_flags*/
  "PTPDevice. xxx need doc", /* tp_doc */
  0,		             /* tp_traverse */
  0,		             /* tp_clear */
  0,		             /* tp_richcompare */
  0,		             /* tp_weaklistoffset */
  0,		             /* tp_iter */
  0,		             /* tp_iternext */
  PTPDevice_methods,         /* tp_methods */
  PTPDeviceMembers,          /* tp_members */
  PTPDevice_getsetters,      /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)PTPDevice_init,  /* tp_init */
  0,                         /* tp_alloc */
  PTPDevice_new,             /* tp_new */
};
