/* Copyright Abel Deuring 2012
   python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.
 */

#include <Python.h>
// Oddly, PyMemberDef is not defined via Python.h
#include <structmember.h>
#include <usb.h>

#include "ptp.h"
#include "ptp-chdk.h"
#include "chdk_headers/core/live_view.h"


#define PYPTP_MAX_ERRMSG_LEN 250

typedef struct PTP_INFO {
  usb_dev_handle* handle;
  int inep;
  int outep;
  int intep;
  PyObject *error_message;
} PTP_INFO;

static void ptp_device_error_va(void *data, const char *format, va_list args)
{
  PTP_INFO *ptp_info = (PTP_INFO*) data;
  Py_XDECREF(ptp_info->error_message);
  //xxx a bit adventurous: We can't be sure that the ptp library uses
  // only those format parameters that are supported by
  // PyString_FromFormatV. but it's very convenient...
  ptp_info->error_message = PyString_FromFormatV(format, args);
}

static void ptp_device_error(void *data, const char *format, ...)
{
  va_list args;
  va_start(args, format);
  ptp_device_error_va(data, format, args);
  va_end(args);
}

static PyObject *PTPError, *datetime_class, *logger;
static void set_python_error_from_PTP_RC(PTP_INFO* ptp_info, uint16_t error);

#include "pyptp-utils.c"
#include "pyptp-constants.c"
#include "libptp-glue.c"
#include "chdk-palette.c"
#include "pyptp-device.c"
#include "pyptp-device-property.c"

static PyObject* list_devices(PyObject *ignore, PyObject *args,
                              PyObject *kwargs) {
  PyObject *py_force = NULL, *result, *entry, *element, *log_result;
  int force = 0;
  struct usb_bus *bus;
  struct usb_device* dev;
  static char *kwnames[] = {"force", NULL};
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", kwnames, &py_force))
    return NULL;

  if (py_force != NULL)
    force = PyObject_IsTrue(py_force);

  if (NULL == (result = PyList_New(0)))
    return NULL;

  // Mostly stolen^Wcopied from ptpcam.c
  Py_UNBLOCK_THREADS;
  bus = init_usb();
  Py_BLOCK_THREADS;
  for (; bus; bus = bus->next) {
    for (dev = bus->devices; dev; dev = dev->next) {
      // We are interested in PTP devices only.
      if (dev->config &&
          (dev->config->interface->altsetting->bInterfaceClass == USB_CLASS_PTP
           || force) &&
          (dev->descriptor.bDeviceClass != USB_CLASS_HUB)) {
        PTPParams params;
        PTP_INFO ptp_usb;
        PTPDeviceInfo device_info;

        memset(&params, 0, sizeof(params));
        memset(&ptp_usb, 0, sizeof(ptp_usb));
        memset(&device_info, 0, sizeof(device_info));

        Py_UNBLOCK_THREADS;
        find_endpoints(dev, &ptp_usb.inep, &ptp_usb.outep, &ptp_usb.intep);
        Py_BLOCK_THREADS;
        if (init_ptp_usb(&params, &ptp_usb, dev)) {
          // xxx log an error?
          Py_CLEAR(ptp_usb.error_message);
          continue;
        }
        if (PTP_RC_OK != ptp_opensession(&params, 1)) {
          log_result = PyObject_CallMethod(logger, "info", "sss",
            "Could not open session for device %s:%s. Try to reset the "
            "camera.",
            bus->dirname, dev->filename);
          if (log_result == NULL) {
            Py_DECREF(result);
            return NULL;
          }
          Py_UNBLOCK_THREADS;
          usb_release_interface(
            ptp_usb.handle,
            dev->config->interface->altsetting->bInterfaceNumber);
          Py_BLOCK_THREADS;
          continue;
        }
        if (PTP_RC_OK != ptp_getdeviceinfo(&params, &device_info)) {
          log_result = PyObject_CallMethod(logger, "info", "sss",
            "Could not retrieve infos for device %s:%s. Try to reset the "
            "camera.",
            bus->dirname, dev->filename);
          if (log_result == NULL) {
            Py_DECREF(result);
            return NULL;
          }
          Py_UNBLOCK_THREADS;
          usb_release_interface(
            ptp_usb.handle,
            dev->config->interface->altsetting->bInterfaceNumber);
          Py_BLOCK_THREADS;
          continue;
        }
        if (NULL == (entry = PyTuple_New(5))) {
          Py_DECREF(result);
          return NULL;
        }
        if (-1 == PyList_Append(result, entry)) {
          Py_DECREF(result);
          Py_DECREF(entry);
          return NULL;
        }
        Py_DECREF(entry);

        if (NULL == (element = PyInt_FromString(bus->dirname, NULL, 10))) {
          Py_DECREF(result);
          return NULL;
        }
        PyTuple_SET_ITEM(entry, 0, element);

        if (NULL == (element = PyInt_FromString(dev->filename, NULL, 10))) {
          Py_DECREF(result);
          return NULL;
        }
        PyTuple_SET_ITEM(entry, 1, element);

        if (NULL == (element = PyInt_FromLong(dev->descriptor.idVendor))) {
          Py_DECREF(result);
          return NULL;
        }
        PyTuple_SET_ITEM(entry, 2, element);

        if (NULL == (element = PyInt_FromLong(dev->descriptor.idProduct))) {
          Py_DECREF(result);
          return NULL;
        }
        PyTuple_SET_ITEM(entry, 3, element);

        if (NULL == (element = PyString_FromString(device_info.Model))) {
          Py_DECREF(result);
          return NULL;
        }
        PyTuple_SET_ITEM(entry, 4, element);

        if (PTP_RC_OK != ptp_closesession(&params)) {
          log_result = PyObject_CallMethod(logger, "info", "sss",
            "Could not close session for device %s:%s.",
            bus->dirname, dev->filename);
          if (log_result == NULL) {
            Py_DECREF(result);
            return NULL;
          }
          Py_UNBLOCK_THREADS;
          usb_release_interface(
            ptp_usb.handle,
            dev->config->interface->altsetting->bInterfaceNumber);
          Py_BLOCK_THREADS;
          continue;
        }
        close_usb(&ptp_usb, dev);
      }
    }
  }

  return result;
}

static struct _ptp_err_map {
  uint16_t error_number; char* message;} ptp_error_map[] = {
  {PTP_RC_Undefined,             "Undefined PTP error (%04x)."},
  {PTP_RC_GeneralError,          "General PTP error (%04x)."},
  {PTP_RC_SessionNotOpen,        "PTP error: Session not open (%04x)."},
  {PTP_RC_InvalidTransactionID,  "PTP error: Invalid transaction ID (%04x)."},
  {PTP_RC_OperationNotSupported, "PTP error: Operation not supported (%04x)."},
  {PTP_RC_ParameterNotSupported, "PTP error: Parameter not supported (%04x)."},
  {PTP_RC_IncompleteTransfer,    "PTP error: Incomplete trasnfer (%04x)."},
  {PTP_RC_InvalidStorageId,      "PTP error: Invalid storage ID (%04x)."},
  {PTP_RC_InvalidObjectHandle,   "PTP error: Invalid object handle(%04x)."},
  {PTP_RC_DevicePropNotSupported,
      "PTP error: Device property not supported (%04x)."},
  {PTP_RC_InvalidObjectFormatCode,
      "PTP error: Invalid object format code(%04x)."},
  {PTP_RC_StoreFull,             "PTP error: Store full(%04x)."},
  {PTP_RC_ObjectWriteProtected,  "PTP error: Object write protected (%04x)."},
  {PTP_RC_StoreReadOnly,         "PTP error: Store read only (%04x)."},
  {PTP_RC_AccessDenied,          "PTP error: Access denied (%04x)."},
  {PTP_RC_NoThumbnailPresent,    "PTP error: No thumbnail present (%04x)."},
  {PTP_RC_SelfTestFailed,        "PTP error: Self test failed (%04x)."},
  {PTP_RC_PartialDeletion,       "PTP error: Partial deletion (%04x)."},
  {PTP_RC_SpecificationByFormatUnsupported,
      "PTP error: Specification by format unsupported (%04x)."},
  {PTP_RC_NoValidObjectInfo,     "PTP error: No valid object info (%04x)."},
  {PTP_RC_InvalidCodeFormat,     "PTP error: Invalid code format (%04x)."},
  {PTP_RC_UnknownVendorCode,     "PTP error: Unknown vendor code (%04x)."},
  {PTP_RC_CaptureAlreadyTerminated,
      "PTP error Capture already terminated: (%04x)."},
  {PTP_RC_DeviceBusy,            "PTP error: Device busy (%04x)."},
  {PTP_RC_InvalidParentObject,   "PTP error: Invalid parent object (%04x)."},
  {PTP_RC_InvalidDevicePropFormat,
      "PTP error: Invalid device property format (%04x)."},
  {PTP_RC_InvalidDevicePropValue,
      "PTP error: Invalid device property value (%04x)."},
  {PTP_RC_InvalidParameter, "PTP error: Invalid parameter (%04x)."},
  {PTP_RC_SessionAlreadyOpened,  "PTP error: Session already opened (%04x)."},
  {PTP_RC_TransactionCanceled,   "PTP error: Transaction canceled (%04x)."},
  {PTP_RC_SpecificationOfDestinationUnsupported,
      "PTP error: Specification of destination unsupported(%04x)."},
  // xxx we should check the camera vendor for the error codes below.
  {PTP_RC_EK_FilenameRequired,   "PTP error (EK): Filename required (%04x)."},
  {PTP_RC_EK_FilenameConflicts,  "PTP error (EK): Filename conflicts (%04x)."},
  {PTP_RC_EK_FilenameInvalid,    "PTP error (EK): Filename invalid (%04x)."},
  {PTP_RC_NIKON_PropertyReadOnly,
      "PTP error (Nikon): Property read only (%04x)."},
  {0, NULL}
};

static void set_python_error_from_PTP_RC(PTP_INFO* ptp_info, uint16_t error) {
  int i;
  PyObject *py_errno, *py_text, *py_value;

  // we may already have an error message from from ptp_device_error_va().
  if (ptp_info->error_message != NULL) {
    py_text = ptp_info->error_message;
    ptp_info->error_message = NULL;
  } else {
    py_text = NULL;
    for (i = 0; ptp_error_map[i].message != NULL; i++) {
      if (error == ptp_error_map[i].error_number) {
        py_text = PyString_FromFormat(ptp_error_map[i].message, error);
        if (py_text == 0)
          return;
      }
    }
    if (py_text == 0) {
      py_text = PyString_FromFormat("Unknown PTP call error: %04x",error);
      if (py_text == NULL)
        return;
    }
  }

  py_errno = PyInt_FromLong(error);
  if (py_errno == NULL) {
    Py_DECREF(py_text);
    return;
  }

  py_value = PyTuple_Pack(2, py_errno, py_text);
  if (py_value == NULL) {
    Py_DECREF(py_errno);
    Py_DECREF(py_text);
    return;
  }
  PyErr_SetObject(PTPError, py_value);
  Py_DECREF(py_value);
}

static PyMethodDef module_methods[] = {
  {"list_devices", (PyCFunction)list_devices, METH_VARARGS | METH_KEYWORDS,
   "Inspect all connected USB devices and list those that look like \n"
   "PTP cameras.\n\n"
   "returns a list of tuples \n"
   "  (bus_number, device_number, vendor_id, product_id, product_name)"},
  {NULL},
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initpyptpchdk(void) {
  PyObject *module, *datetime_module, *logger_module, *loghandler, *result;

  if (PyType_Ready(&PTPDeviceType) < 0)
    return;
  if (PyType_Ready(&PTPDevicePropertyType) < 0)
    return;

  module = Py_InitModule3(
    "pyptpchdk", module_methods,
    "A Picture Transfer protocol module.");

  if (init_all_constants(module)) {
    return;
  }

  PTPError = PyErr_NewException("pyptpchdk.PTPError", NULL, NULL);
  if (PTPError == NULL)
    return;
  Py_INCREF(PTPError);
  PyModule_AddObject(module, "PTPError", PTPError);

  Py_INCREF(&PTPDeviceType);
  PyModule_AddObject(module, "PTPDevice", (PyObject *)&PTPDeviceType);

  if (NULL == (datetime_module = PyImport_ImportModule("datetime"))) {
    return;
    }

  if (NULL == (datetime_class = PyObject_GetAttrString(datetime_module,
                                                       "datetime"))) {
    Py_DECREF(datetime_module);
    return;
  }
  Py_DECREF(datetime_module);

  if (NULL == (logger_module = PyImport_ImportModule("logging")))
    return;

  if (NULL == (logger = PyObject_CallMethod(logger_module, "getLogger",
                                            "s", "pyptpchdk"))) {
    Py_DECREF(logger_module);
    return;
  }
  if (NULL == (result = PyObject_CallMethod(logger, "setLevel",
                                            "s", "INFO"))) {
    return;
  }
  Py_DECREF(result);

  if (NULL == (loghandler = PyObject_CallMethod(logger_module,
                                                "StreamHandler", ""))) {
    Py_DECREF(logger);
    Py_DECREF(logger_module);
    return;
  }
  if (NULL == (result = PyObject_CallMethod(loghandler, "setLevel",
                                            "s", "INFO"))) {
    return;
  }
  Py_DECREF(result);

  if (NULL == (result = PyObject_CallMethod(logger, "addHandler",
                                            "O", loghandler))) {
    Py_DECREF(loghandler);
    Py_DECREF(logger);
    Py_DECREF(logger_module);
    return;
  }

  Py_DECREF(logger_module);
  Py_DECREF(loghandler);
  Py_DECREF(result);
}
