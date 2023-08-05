/*
 *
 * Copyright (C) 2010-2012 <reyalp (at) gmail dot com>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

// Palette related functions. Plain copy from chdkptp, file liveimg.c

typedef struct {
  uint8_t r;
  uint8_t g;
  uint8_t b;
  uint8_t a;
} palette_entry_rgba_t;

typedef struct {
  uint8_t a;
  uint8_t y;
  int8_t u;
  int8_t v;
} palette_entry_ayuv_t;

typedef struct {
  int8_t v;
  int8_t u;
  uint8_t y;
  uint8_t a;
} palette_entry_vuya_t;

typedef void (*yuv_palette_to_rgba_fn)(const char *pal_yuv, uint8_t pixel,
                                       palette_entry_rgba_t *pal_rgb);

static uint8_t clamp_uint8(unsigned v) {
  return (v>255)?255:v;
}

static int8_t clamp_int8(int v) {
  if(v > 127) {
    return 127;
  }
  if(v < -128) {
    return -128;
  }
  return v;
}

static uint8_t clip_yuv(int v) {
  if (v < 0) return 0;
  if (v > 255) return 255;
  return v;
}

static uint8_t yuv_to_r(uint8_t y, int8_t v) {
  return clip_yuv(((y<<12) +          v*5743 + 2048)>>12);
}

static uint8_t yuv_to_g(uint8_t y, int8_t u, int8_t v) {
  return clip_yuv(((y<<12) - u*1411 - v*2925 + 2048)>>12);
}

static uint8_t yuv_to_b(uint8_t y, int8_t u) {
  return clip_yuv(((y<<12) + u*7258          + 2048)>>12);
}

void palette_type1_to_rgba(const char *palette, uint8_t pixel,
                           palette_entry_rgba_t *pal_rgb) {
  const palette_entry_ayuv_t *pal = (const palette_entry_ayuv_t *)palette;
  unsigned i1 = pixel & 0xF;
  unsigned i2 = (pixel & 0xF0)>>4;
  int8_t u,v;
  uint8_t y;
  pal_rgb->a = (pal[i1].a + pal[i2].a)>>1;
  // TODO not clear if combined should be /2 or not
  // special case in canon firmware, if lower 4 bits 0, grays
  if(i1 == 0) {
          u = v = 0;
  } else {
          u = clamp_int8(pal[i1].u + pal[i2].u);
          v = clamp_int8(pal[i1].v + pal[i2].v);
  }
  y = clamp_uint8(pal[i1].y + pal[i2].y);
  pal_rgb->r = yuv_to_r(y,v);
  pal_rgb->g = yuv_to_g(y,u,v);
  pal_rgb->b = yuv_to_b(y,u);
}

static const uint8_t alpha2_lookup[] = {128,171,214,255};
// like above, but with alpha lookup
// TODO this is untested an probably wrong
void palette_type2_to_rgba(const char *palette, uint8_t pixel,
                           palette_entry_rgba_t *pal_rgb) {
  const palette_entry_ayuv_t *pal = (const palette_entry_ayuv_t *)palette;
  unsigned i1 = pixel & 0xF;
  unsigned i2 = (pixel & 0xF0)>>4;
  int8_t u,v;
  uint8_t y;
  uint8_t a = (pal[i1].a + pal[i2].a)>>1;
  pal_rgb->a = alpha2_lookup[a&3];
  // TODO not clear if these should be /2 or not
  y = clamp_uint8(pal[i1].y + pal[i2].y);
  u = clamp_int8(pal[i1].u + pal[i2].u);
  v = clamp_int8(pal[i1].v + pal[i2].v);
  pal_rgb->r = yuv_to_r(y,v);
  pal_rgb->g = yuv_to_g(y,u,v);
  pal_rgb->b = yuv_to_b(y,u);
}

void palette_type3_to_rgba(const char *palette, uint8_t pixel,
                           palette_entry_rgba_t *pal_rgb) {
  const palette_entry_vuya_t *pal = (const palette_entry_vuya_t *)palette;
  // special case for index 0
  if(pixel == 0) {
    pal_rgb->a = pal_rgb->r = pal_rgb->g = pal_rgb->b = 0;
    return;
  }
  pal_rgb->a = alpha2_lookup[pal[pixel].a&3];
  pal_rgb->r = yuv_to_r(pal[pixel].y,pal[pixel].v);
  pal_rgb->g = yuv_to_g(pal[pixel].y,pal[pixel].u,pal[pixel].v);
  pal_rgb->b = yuv_to_b(pal[pixel].y,pal[pixel].u);
}

// like 2, but vuya
void palette_type4_to_rgba(const char *palette, uint8_t pixel,
                           palette_entry_rgba_t *pal_rgb) {
  const palette_entry_vuya_t *pal = (const palette_entry_vuya_t *)palette;
  unsigned i1 = pixel & 0xF;
  unsigned i2 = (pixel & 0xF0)>>4;
  int8_t u,v;
  uint8_t y;
  // special case for index 0
  if(pixel == 0) {
    pal_rgb->a = pal_rgb->r = pal_rgb->g = pal_rgb->b = 0;
    return;
  }

  // TODO this isn't right for sx110
  uint8_t a = (pal[i1].a + pal[i2].a)>>1;
  pal_rgb->a = alpha2_lookup[a&3];
  // TODO not clear if these should be /2 or not
  y = clamp_uint8(pal[i1].y + pal[i2].y);
  u = clamp_int8(pal[i1].u + pal[i2].u);
  v = clamp_int8(pal[i1].v + pal[i2].v);
  pal_rgb->r = yuv_to_r(y,v);
  pal_rgb->g = yuv_to_g(y,u,v);
  pal_rgb->b = yuv_to_b(y,u);
}

// from a540, playback mode
static const char palette_type1_default[]={
0x00, 0x00, 0x00, 0x00, 0xff, 0xe0, 0x00, 0x00, 0xff, 0x60, 0xee, 0x62, 0xff, 0xb9, 0x00, 0x00,
0x7f, 0x00, 0x00, 0x00, 0xff, 0x7e, 0xa1, 0xb3, 0xff, 0xcc, 0xb8, 0x5e, 0xff, 0x5f, 0x00, 0x00,
0xff, 0x94, 0xc5, 0x5d, 0xff, 0x8a, 0x50, 0xb0, 0xff, 0x4b, 0x3d, 0xd4, 0x7f, 0x28, 0x00, 0x00,
0x7f, 0x00, 0x7b, 0xe2, 0xff, 0x30, 0x00, 0x00, 0xff, 0x69, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00,
};

typedef struct {
  yuv_palette_to_rgba_fn to_rgba;
  unsigned num_entries;
} palette_convert_t;

// type implied from index
// TODO only one function for now
palette_convert_t palette_funcs[] = {
  {NULL,0},                    // type 0 - no palette, we could have a
                               // default func here
  {palette_type1_to_rgba,16},  // type 1 - ayuv, 16 entries double 4 bit index
  {palette_type2_to_rgba,16},  // type 2 - like type 1, but with 2 bit
                               // alpha lookup - UNTESTED
  {palette_type3_to_rgba,256}, // type 3 - vuya, 256 entries, 2 bit alpha
                               // lookup
  {palette_type4_to_rgba,16},  // type 4 - with 2 bit alpha lookup like 2
};

#define N_PALETTE_FUNCS (sizeof(palette_funcs)/sizeof(palette_funcs[0]))

static palette_convert_t* get_palette_convert(unsigned type) {
  if(type<N_PALETTE_FUNCS) {
    return &(palette_funcs[type]);
  }
  return NULL;
}

static void convert_palette(palette_entry_rgba_t *pal_rgba,
                            lv_data_header *frame) {
  const char *pal=NULL;
  palette_convert_t *convert=get_palette_convert(frame->palette_type);
  if(!convert || !frame->palette_data_start) {
    convert = get_palette_convert(1);
    pal = palette_type1_default;
  } else {
    pal = ((char *)frame + frame->palette_data_start);
  }
  yuv_palette_to_rgba_fn fn = convert->to_rgba;
  int i;
  for(i=0;i<256;i++) {
    fn(pal,i,&pal_rgba[i]);
  }
}
