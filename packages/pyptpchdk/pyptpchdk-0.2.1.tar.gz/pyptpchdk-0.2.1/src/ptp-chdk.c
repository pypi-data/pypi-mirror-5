/* python-ptp-chdk is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, version 2 of the License.

   Most code in this file is copied from CHDK sources:
   http://subversion.assembla.com/svn/chdkde/trunk/tools/ptpcam/ptpcam.c
   http://subversion.assembla.com/svn/chdkde/trunk/tools/ptpcam/ptp.c
   http://subversion.assembla.com/svn/chdkptp/

 * Copyright (C) 2001-2005 Mariusz Woloszyn <emsi@ipartners.pl>
 * Copyright (C) <reyalp (at) gmail dot com> and other CHDK contributors
 */

#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include "ptp.h"
#include "ptp-chdk.h"

/* Transaction data phase description */
#define PTP_DP_NODATA           0x0000  /* no data phase */
#define PTP_DP_SENDDATA         0x0001  /* sending data */
#define PTP_DP_GETDATA          0x0002  /* receiving data */
#define PTP_DP_DATA_MASK        0x00ff  /* data phase mask */

#define PTP_CNT_INIT(cnt) {memset(&cnt,0,sizeof(cnt));}


static char* ptp_chdk_upload_prepare_ptp_buf(const char *remote_fn,
                                             int payload_len,
                                             char **payload_start,
                                             int *ptp_buffer_len) {
  char *result;
  int fn_len;

  fn_len = strlen(remote_fn);
  *ptp_buffer_len = 4 + fn_len + payload_len;
  result = malloc(*ptp_buffer_len);
  if (result == NULL)
    return NULL;
  ((int*) result)[0] = fn_len;
  memcpy(result + 4, remote_fn, fn_len);
  *payload_start = result + 4 + fn_len;
  return result;
}

static uint16_t ptp_chdk_do_upload(char *buf, int buf_len,
                                   PTPParams* params,
                                   PTPDeviceInfo* deviceinfo)
{
  uint16_t ret;
  PTPContainer ptp;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=1;
  ptp.Param1=PTP_CHDK_UploadFile;


  ret=ptp_transaction(params, &ptp, PTP_DP_SENDDATA, buf_len, &buf);

  free(buf);

  if (ret != PTP_RC_OK)
    ptp_error(params ,"unexpected return code 0x%x",ret);
  return ret;
}

uint16_t ptp_chdk_upload_string(char *data, int data_len, char *remote_fn,
                                PTPParams* params, PTPDeviceInfo* deviceinfo)
{
  uint16_t ret;
  int ptp_buffer_len;
  char *ptp_payload_start;
  char *ptp_buf = ptp_chdk_upload_prepare_ptp_buf(remote_fn, data_len,
                                                  &ptp_payload_start,
                                                  &ptp_buffer_len);

  if (ptp_buf == NULL) {
    ptp_error(params, "Cannot allocate buffer");
    return PTP_RC_GeneralError;
  }

  memcpy(ptp_payload_start, data, data_len);

  ret = ptp_chdk_do_upload(ptp_buf, ptp_buffer_len, params, deviceinfo);

  if (ret != PTP_RC_OK)
    ptp_error(params ,"unexpected return code 0x%x",ret);
  return ret;
}

uint16_t ptp_chdk_upload(char *local_fn, char *remote_fn, PTPParams* params,
                         PTPDeviceInfo* deviceinfo)
{
  uint16_t ret;
  int ptp_buffer_len, ptp_payload_len;
  char *ptp_payload_start;
  char *ptp_buf;
  FILE *f;

  f = fopen(local_fn,"rb");
  if ( f == NULL )
  {
    ptp_error(params, "could not open file \'%s\'", local_fn);
    return PTP_RC_CHDK_LOCAL_FILE_NOT_FOUND;
  }

  fseek(f,0,SEEK_END);
  ptp_payload_len = ftell(f);
  fseek(f,0,SEEK_SET);

  ptp_buf = ptp_chdk_upload_prepare_ptp_buf(remote_fn, ptp_payload_len,
                                            &ptp_payload_start,
                                            &ptp_buffer_len);

  if (ptp_buf == NULL) {
    ptp_error(params, "Cannot allocate buffer");
    return PTP_RC_GeneralError;
  }

  if (ptp_payload_len != fread(ptp_payload_start, 1, ptp_payload_len, f)) {
    ptp_error(params, "Error reading file %s", local_fn);
    free(ptp_buf);
    return PTP_RC_GeneralError;
  }

  ret = ptp_chdk_do_upload(ptp_buf, ptp_buffer_len, params, deviceinfo);

  if (ret != PTP_RC_OK)
    ptp_error(params ,"unexpected return code 0x%x",ret);
  return ret;
}

uint16_t ptp_chdk_download_string(char *remote_fn, char **dest, int* data_size,
                                  PTPParams* params, PTPDeviceInfo* deviceinfo)
{
  uint16_t ret;
  PTPContainer ptp;
  char *buf = NULL;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=2;
  ptp.Param1=PTP_CHDK_TempData;
  ptp.Param2=0;
  ret=ptp_transaction(params, &ptp, PTP_DP_SENDDATA, strlen(remote_fn),
                      &remote_fn);
  if (ret != PTP_RC_OK)
  {
    ptp_error(params, "unexpected return code 0x%x", ret);
    return ret;
  }

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=1;
  ptp.Param1=PTP_CHDK_DownloadFile;

  ret=ptp_transaction(params, &ptp, PTP_DP_GETDATA, 0, &buf);
  if (ret != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",ret);
    if (buf != NULL) free(buf);
    return ret;
  }

  *dest = buf;
  *data_size = ptp.Param1;
  return PTP_RC_OK;
}

uint16_t ptp_chdk_download(char *remote_fn, char *local_fn, PTPParams* params,
                           PTPDeviceInfo* deviceinfo)
{
  uint16_t ret;
  char *buf = NULL;
  FILE *f;
  int data_size;

  ret = ptp_chdk_download_string(remote_fn, &buf, &data_size, params,
                                 deviceinfo);
  if (ret != PTP_RC_OK) {
    return ret;
  }

  f = fopen(local_fn,"wb");
  if ( f == NULL )
  {
    ptp_error(params,"could not open file \'%s\'",local_fn);
    free(buf);
    return PTP_RC_CHDK_LOCAL_FILE_OPEN_ERROR;
  }

  fwrite(buf, 1, data_size, f);
  fclose(f);

  free(buf);

  return PTP_RC_OK;
}

uint16_t ptp_start_lua(char *script, uint32_t *script_id, PTPParams* params) {
  uint16_t call_result;
  PTPContainer ptp;

  memset(&ptp, 0, sizeof(ptp));
  ptp.Code = PTP_OC_CHDK;
  ptp.Nparam = 2;
  ptp.Param1 = PTP_CHDK_ExecuteScript;
  ptp.Param2 = PTP_CHDK_SL_LUA;

  call_result = ptp_transaction(params, &ptp, PTP_DP_SENDDATA,
                                strlen(script) + 1, &script);
  // Note that the script_id is valid only if the call was successful
  *script_id = ptp.Param1;
  return call_result;
}

uint16_t ptp_chdk_get_script_status(PTPParams* params, int *status)
{
  uint16_t r;
  PTPContainer ptp;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=1;
  ptp.Param1=PTP_CHDK_ScriptStatus;
  r=ptp_transaction(params, &ptp, PTP_DP_NODATA, 0, NULL);
  if (r != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",r);
    return r;
  }
  *status = ptp.Param1;
  return r;
}

uint16_t ptp_chdk_get_script_support(PTPParams* params, int *status)
{
  uint16_t r;
  PTPContainer ptp;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=1;
  ptp.Param1=PTP_CHDK_ScriptSupport;
  r=ptp_transaction(params, &ptp, PTP_DP_NODATA, 0, NULL);
  if (r != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",r);
    return r;
  }
  *status = ptp.Param1;
  return r;
}

uint16_t ptp_chdk_get_version(PTPParams* params, int *major, int *minor)
{
  uint16_t r;
  PTPContainer ptp;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=1;
  ptp.Param1=PTP_CHDK_Version;
  r=ptp_transaction(params, &ptp, PTP_DP_NODATA, 0, NULL);
  if (r != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",r);
    return r;
  }
  *major = ptp.Param1;
  *minor = ptp.Param2;
  return r;
}

uint16_t ptp_chdk_read_script_msg(PTPParams* params, ptp_chdk_script_msg **msg)
{
  uint16_t r;
  PTPContainer ptp;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=1;
  ptp.Param1=PTP_CHDK_ReadScriptMsg;
  char *data = NULL;

  // camera will always send data, otherwise getdata will cause problems
  r=ptp_transaction(params, &ptp, PTP_DP_GETDATA, 0, &data);
  if (r != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",r);
    if (data != NULL) free(data);
    *msg = NULL;
    return r;
  }
  *msg = malloc(sizeof(ptp_chdk_script_msg) + ptp.Param4);
  (*msg)->type = ptp.Param1;
  (*msg)->subtype = ptp.Param2;
  (*msg)->script_id = ptp.Param3;
  (*msg)->size = ptp.Param4;
  memcpy((*msg)->data,data,(*msg)->size);
  free(data);
  return r;
}
uint16_t ptp_chdk_write_script_msg(PTPParams* params, char *data,
                                   unsigned size, int script_id, int *status)
{
  uint16_t r;
  PTPContainer ptp;

  // a zero length data phase appears to do bad things, camera stops responding to PTP
  if(!size) {
    ptp_error(params, "zero length message not allowed");
    *status = 0;
        return PTP_RC_GeneralError;
  }
  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=2;
  ptp.Param1=PTP_CHDK_WriteScriptMsg;
  ptp.Param2=script_id; // TODO test don't care ?
//  ptp.Param3=size;

  r=ptp_transaction(params, &ptp, PTP_DP_SENDDATA, size, &data);
  if (r != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",r);
    *status = 0;
    return r;
  }
  *status = ptp.Param1;
  return PTP_RC_OK;
}

uint16_t ptp_chdk_get_live_data(PTPParams* params, PTPDeviceInfo* deviceinfo,
                           unsigned flags, char **data, unsigned *data_size) {
  uint16_t r;
  PTPContainer ptp;

  PTP_CNT_INIT(ptp);
  ptp.Code=PTP_OC_CHDK;
  ptp.Nparam=2;
  ptp.Param1=PTP_CHDK_GetDisplayData;
  ptp.Param2=flags;
  *data = NULL;
  *data_size = 0;

  r=ptp_transaction(params, &ptp, PTP_DP_GETDATA, 0, data);
  if (r != PTP_RC_OK)
  {
    ptp_error(params,"unexpected return code 0x%x",r);
    if (data != NULL) free(*data);
    *data = NULL;
    return r;
  }
  *data_size = ptp.Param1;
  return r;

}
