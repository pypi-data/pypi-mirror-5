/* python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.

   Most contents of this file is copied from CHDK-DE sources,
   http://subversion.assembla.com/svn/chdkde/trunk/tools/ptpcam/ptpcam.c

 * Copyright (C) 2001-2005 Mariusz Woloszyn <emsi@ipartners.pl>

   Glue to ptp library
*/

#define USB_BULK_READ usb_bulk_read
#define USB_BULK_WRITE usb_bulk_write

#define MAXCONNRETRIES 10


/* OUR APPLICATION USB URB (2MB) ;) */
#define PTPCAM_USB_URB          2097152

#define USB_TIMEOUT             5000
#define USB_CAPTURE_TIMEOUT     20000

/* one global variable (yes, I know it sucks) */
short verbose = 0;
/* the other one, it sucks definitely ;) */
int ptpcam_usb_timeout = USB_TIMEOUT;

static void close_usb(PTP_INFO* ptp_usb, struct usb_device* dev)
{
  //clear_stall(ptp_usb);
  usb_release_interface(ptp_usb->handle,
                        dev->config->interface->altsetting->bInterfaceNumber);
  usb_reset(ptp_usb->handle);
  usb_close(ptp_usb->handle);
}

static struct usb_bus* init_usb(void)
{
  usb_init();
  usb_find_busses();
  usb_find_devices();
  return (usb_get_busses());
}

/*
   find_device() returns the pointer to a usb_device structure matching
   given busn, devicen numbers. If any or both of arguments are 0 then the
   first matching PTP device structure is returned.
*/
static struct usb_device* find_device (int busn, int devn, short force)
{
  struct usb_bus *bus;
  struct usb_device *dev;

  bus = init_usb();
  for (; bus; bus = bus->next)
    for (dev = bus->devices; dev; dev = dev->next)
      if (dev->config)
	if ((dev->config->interface->altsetting->bInterfaceClass ==
             USB_CLASS_PTP)||force)
          if (dev->descriptor.bDeviceClass != USB_CLASS_HUB)
            {
              int curbusn, curdevn;

              curbusn = strtol(bus->dirname,NULL,10);
#ifdef WIN32
              curdevn = strtol(strchr(dev->filename,'-')+1,NULL,10);
#else
              curdevn = strtol(dev->filename,NULL,10);
#endif

              if (devn == 0) {
                if (busn == 0) return dev;
                if (curbusn == busn) return dev;
              } else {
                if ((busn == 0) && (curdevn == devn)) return dev;
                if ((curbusn == busn) && (curdevn == devn)) return dev;
              }
            }
  return NULL;
}

static void find_endpoints(struct usb_device *dev, int* inep, int* outep,
                           int* intep)
{
  int i, n;
  struct usb_endpoint_descriptor *ep;

  ep = dev->config->interface->altsetting->endpoint;
  n=dev->config->interface->altsetting->bNumEndpoints;

  for (i = 0; i < n; i++) {
    if (ep[i].bmAttributes == USB_ENDPOINT_TYPE_BULK) {
      if ((ep[i].bEndpointAddress & USB_ENDPOINT_DIR_MASK) ==
          USB_ENDPOINT_DIR_MASK) {
        *inep=ep[i].bEndpointAddress;
        if (verbose>1)
          fprintf(stderr, "Found inep: 0x%02x\n",*inep);
      }
      if ((ep[i].bEndpointAddress&USB_ENDPOINT_DIR_MASK) == 0)
        {
          *outep=ep[i].bEndpointAddress;
          if (verbose>1)
            fprintf(stderr, "Found outep: 0x%02x\n",*outep);
        }
    } else if ((ep[i].bmAttributes == USB_ENDPOINT_TYPE_INTERRUPT) &&
               ((ep[i].bEndpointAddress&USB_ENDPOINT_DIR_MASK) ==
                USB_ENDPOINT_DIR_MASK))
      {
        *intep=ep[i].bEndpointAddress;
        if (verbose>1)
          fprintf(stderr, "Found intep: 0x%02x\n",*intep);
      }
  }
}

static short ptp_read_func (unsigned char *bytes, unsigned int size,
                            void *data)
{
  int result = -1;
  PTP_INFO *ptp_usb = (PTP_INFO *)data;
  int toread = 0;
  signed long int rbytes = size;
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif

  Py_UNBLOCK_THREADS;
  do {
    bytes += toread;
    if (rbytes > PTPCAM_USB_URB)
      toread = PTPCAM_USB_URB;
    else
      toread = rbytes;
    result = USB_BULK_READ(ptp_usb->handle, ptp_usb->inep, (char *)bytes,
                           toread, ptpcam_usb_timeout);
    /* sometimes retry might help */
    if (result == 0)
      result = USB_BULK_READ(ptp_usb->handle, ptp_usb->inep, (char *)bytes,
                             toread, ptpcam_usb_timeout);
    if (result < 0)
      break;
    rbytes -= PTPCAM_USB_URB;
  } while (rbytes > 0);

  if (result >= 0) {
    Py_BLOCK_THREADS;
    return (PTP_RC_OK);
  }
  else {
    Py_BLOCK_THREADS;
    ptp_device_error(data, "usb_bulk_read error");
    return PTP_ERROR_IO;
  }
}

static short ptp_write_func (unsigned char *bytes, unsigned int size,
                             void *data)
{
  int result;
  PTP_INFO *ptp_usb = (PTP_INFO *)data;
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif

  Py_UNBLOCK_THREADS;
  result = USB_BULK_WRITE(ptp_usb->handle, ptp_usb->outep, (char *)bytes, size,
                          ptpcam_usb_timeout);
  Py_BLOCK_THREADS;
  if (result >= 0)
    return (PTP_RC_OK);
  else {
    ptp_device_error(data, "usb_bulk_write error");
    return PTP_ERROR_IO;
  }
}

/* XXX this one is suposed to return the number of bytes read!!! */
static short
ptp_check_int (unsigned char *bytes, unsigned int size, void *data)
{
  int result;
  PTP_INFO *ptp_usb=(PTP_INFO *)data;
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif

  Py_UNBLOCK_THREADS;
  result = USB_BULK_READ(ptp_usb->handle, ptp_usb->intep, (char *)bytes, size,
                         ptpcam_usb_timeout);
  if (result == 0)
    result = USB_BULK_READ(ptp_usb->handle, ptp_usb->intep, (char *)bytes,
                           size, ptpcam_usb_timeout);
  Py_BLOCK_THREADS;
  if (verbose>2)
    fprintf (stderr, "USB_BULK_READ returned %i, size=%i\n",
             result, size);

  if (result >= 0) {
    return result;
  } else {
    ptp_device_error(data, "ptp_check_int: usb_bulb_read error");
    return result;
  }
}


static void ptpcam_debug (void *data, const char *format, va_list args)
{
  if (verbose<2) return;
  vfprintf (stderr, format, args);
  fprintf (stderr,"\n");
  fflush(stderr);
}

static int init_ptp_usb (PTPParams* params, PTP_INFO* ptp_usb,
                          struct usb_device* dev)
{
  usb_dev_handle *device_handle;
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif

  Py_UNBLOCK_THREADS;
  params->write_func = ptp_write_func;
  params->read_func = ptp_read_func;
  params->check_int_func = ptp_check_int;
  params->check_int_fast_func = ptp_check_int;
  params->error_func = ptp_device_error_va;
  params->debug_func = ptpcam_debug;
  params->sendreq_func = ptp_usb_sendreq;
  params->senddata_func = ptp_usb_senddata;
  params->getresp_func = ptp_usb_getresp;
  params->getdata_func = ptp_usb_getdata;
  params->data = ptp_usb;
  params->transaction_id = 0;
  params->byteorder = PTP_DL_LE;

  device_handle = usb_open(dev);
  Py_BLOCK_THREADS;
  if (!device_handle) {
    ptp_device_error(ptp_usb, "USB error: Cannot open device.");
    return -1;
  }
  Py_UNBLOCK_THREADS;
  ptp_usb->handle = device_handle;
  // xxx error checks needed.
  usb_set_configuration(device_handle, dev->config->bConfigurationValue);
  usb_claim_interface(device_handle,
                      dev->config->interface->altsetting->bInterfaceNumber);
  Py_BLOCK_THREADS;
  return 0;
}


static int open_camera (int busn, int devn, short force, PTP_INFO *ptp_usb,
                        PTPParams *params, struct usb_device **dev)
{
  int retrycnt = 0;
  uint16_t ret = 0;
  PyObject *log_result;
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif

#ifdef DEBUG
  printf("dev %i\tbus %i\n",devn,busn);
#endif

  Py_UNBLOCK_THREADS;
  // retry device find for a while (in case the user just powered it on
  //or called restart)
  while ((retrycnt++ < MAXCONNRETRIES) && !ret) {
    *dev = find_device(busn, devn, force);
    if (*dev != NULL)
      ret = 1;
    else {
      Py_BLOCK_THREADS;
      log_result = PyObject_CallMethod(logger, "info", "s",
        "Could not find any device matching given bus/dev numbers, "
        "retrying in 1 s...");
      if (log_result == NULL) {
        return -1;
      }
      Py_DECREF(log_result);
      Py_UNBLOCK_THREADS;
      sleep(1);
    }
  }

  if (*dev == NULL) {
    Py_BLOCK_THREADS;
    ptp_device_error(ptp_usb,
                     "Could not find any device matching given "
                     "bus/dev numbers");
    return -1;
  }
  find_endpoints(*dev, &ptp_usb->inep, &ptp_usb->outep, &ptp_usb->intep);
  Py_BLOCK_THREADS;
  if (init_ptp_usb(params, ptp_usb, *dev)) {
    return -1;
  };

  // first connection attempt often fails if some other app or driver has
  // accessed the camera, retry for a while
  retrycnt = 0;
  while ((retrycnt++ < MAXCONNRETRIES) &&
         ((ret=ptp_opensession(params,1)) != PTP_RC_OK)) {
    log_result = PyObject_CallMethod(logger, "info", "si",
      "Failed to connect (attempt %d), retrying in 1 s...", retrycnt);
    if (log_result == NULL) {
      return -1;
    }
    Py_DECREF(log_result);
    Py_UNBLOCK_THREADS;
    close_usb(ptp_usb, *dev);
    sleep(1);
    find_endpoints(*dev, &ptp_usb->inep, &ptp_usb->outep, &ptp_usb->intep);
    Py_BLOCK_THREADS;
    if (init_ptp_usb(params, ptp_usb, *dev)) {
      return -1;
    }
  }
  if (ret != PTP_RC_OK) {
    ptp_device_error(ptp_usb, "Could not open session");
    close_usb(ptp_usb, *dev);
    return -1;
  }

  ret = ptp_getdeviceinfo(params, &params->deviceinfo);
  if (ret != PTP_RC_OK) {
    ptp_device_error(ptp_usb, "Could not get device info");
    Py_UNBLOCK_THREADS;
    close_usb(ptp_usb, *dev);
    Py_BLOCK_THREADS;
    return -1;
  }
  return 0;
}

static int close_camera (PTP_INFO *ptp_usb, PTPParams *params,
                          struct usb_device *dev)
{
  PyObject *log_result;
#ifdef WITH_THREAD
  PyThreadState *_save;
#endif

  if (ptp_closesession(params) != PTP_RC_OK) {
    log_result = PyObject_CallMethod(logger, "error", "s",
                                     "Could not close session!");
    if (log_result == NULL) {
      Py_UNBLOCK_THREADS;
      close_usb(ptp_usb, dev);
      Py_BLOCK_THREADS;
      return -1;
    }
    Py_DECREF(log_result);
  }
  Py_UNBLOCK_THREADS;
  close_usb(ptp_usb, dev);
  Py_BLOCK_THREADS;
  return 0;
}
