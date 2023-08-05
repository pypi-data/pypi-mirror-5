/* python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.

   Most contents of this file is copied from CHDK sources,
   http://subversion.assembla.com/svn/chdkptp/trunk/chdk_headers/core/ptp.h
 */
#ifndef __PTP_CHDK_H__
#define __PTP_CHDK_H__

#include "chdk_headers/core/ptp.h"

// python-ptp-chdk error code extensions.
#define PTP_RC_CHDK_LOCAL_FILE_NOT_FOUND 0xB000
#define PTP_RC_CHDK_LOCAL_FILE_OPEN_ERROR 0xB001


typedef struct {
    unsigned size;
    unsigned script_id; // id of script message is to/from
    unsigned type;
    unsigned subtype;
    char data[];
} ptp_chdk_script_msg;

uint16_t ptp_chdk_upload_string(char *data, int data_len, char *remote_fn,
                                PTPParams* params, PTPDeviceInfo* deviceinfo);
uint16_t ptp_chdk_upload(char *local_fn, char *remote_fn, PTPParams* params,
                         PTPDeviceInfo* deviceinfo);
uint16_t ptp_chdk_download_string(char *remote_fn, char **dest, int* data_size,
                                  PTPParams* params, PTPDeviceInfo* deviceinfo);
uint16_t ptp_chdk_download(char *remote_fn, char *local_fn, PTPParams* params,
                           PTPDeviceInfo* deviceinfo);
uint16_t ptp_start_lua(char *script, uint32_t *script_id, PTPParams* params);
uint16_t ptp_chdk_get_script_status(PTPParams* params, int *status);
uint16_t ptp_chdk_get_script_support(PTPParams* params, int *status);
uint16_t ptp_chdk_get_version(PTPParams* params, int *major, int *minor);
uint16_t ptp_chdk_read_script_msg(PTPParams* params, ptp_chdk_script_msg **msg);
uint16_t ptp_chdk_write_script_msg(PTPParams* params, char *data,
                                   unsigned size, int script_id, int *status);
uint16_t ptp_chdk_get_live_data(PTPParams* params, PTPDeviceInfo* deviceinfo,
                           unsigned flags, char **data, unsigned *data_size);

#define LV_TFR_DOUBLE_VIEWPORT_LINES 0x1000
#define LV_TFR_SHRINK_VIEWPORT_LINES 0x2000
#define LV_TFR_DOUBLE_BITMAP_LINES 0x4000
#define LV_TFR_SHRINK_BITMAP_LINES 0x8000

#endif // __PTP_CHDK_H__
