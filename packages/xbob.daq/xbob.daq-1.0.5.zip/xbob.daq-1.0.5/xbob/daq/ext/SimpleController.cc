/**
 * @file daq/cxx/SimpleController.cc
 * @date Thu Feb 2 11:22:57 2012 +0100
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "bob/core/logging.h"
#include "SimpleController.h"
#include <pthread.h>
#include <sys/time.h>

#include <cstdio>
#include <cstring>

#include <jpeglib.h>
#include <jerror.h>

namespace xbob { namespace daq {
  
SimpleController::SimpleController() : firstFrameTimestamp(-1), recording(false),
  buffer(NULL), bufferSize(0) {
  
}

SimpleController::~SimpleController() {
  delete buffer;
}

void SimpleController::keyPressed(int key) {
  if ((char)key == 'q') {
    stop();
  }
}

void SimpleController::stop() {
  pthread_mutex_lock(&stoppables_mutex);
  for(std::vector<Stoppable*>::iterator it = stoppables.begin(); it != stoppables.end(); it++) {
    (*it)->stop();
  }
  pthread_mutex_unlock(&stoppables_mutex);
  
  pthread_mutex_lock(&callbacks_mutex);
  for(std::vector<ControllerCallback*>::iterator it = callbacks.begin(); it != callbacks.end(); it++) {
    (*it)->stop();
  }
  pthread_mutex_unlock(&callbacks_mutex);

  firstFrameTimestamp = -1;
  recording = false;
}

// Not sure where this code comes from but here is one of the possible sources:
// http://opentouch.googlecode.com/svn-history/r3/trunk/src/PortVideo/linux/ccvt/ccvt_misc.c
#define SAT(c) if (c & (~255)) { if (c < 0) c = 0; else c = 255; }
static void yuyvToRgb24(unsigned char* dst , const unsigned char* src , const int width, const int height) {
  unsigned char* s;
  unsigned char* d;
  int l, c;
  int r, g, b, cr, cg, cb, y1, y2;
  
  l = height;
  s = (unsigned char*) src;
  d = (unsigned char*) dst;
  while (l--) {
    c = width >> 1;
    while (c--) {
      y1 = *s++;
      cb = ( ( *s - 128 ) * 454 ) >> 8;
      cg = ( *s++ - 128 ) * 88;
      y2 = *s++;
      cr = ( ( *s - 128 ) * 359 ) >> 8;
      cg = ( cg + ( *s++ - 128 ) * 183 ) >> 8;
      
      r = y1 + cr;
      b = y1 + cb;
      g = y1 - cg;
      SAT(r);
      SAT(g);
      SAT(b);
      
      *d++ = r;
      *d++ = g;
      *d++ = b;
      
      r = y2 + cr;
      b = y2 + cb;
      g = y2 - cg;
      SAT(r);
      SAT(g);
      SAT(b);
      
      *d++ = r;
      *d++ = g;
      *d++ = b;
    }
  }
}

/**
 * This method is currently unused, so it was commented out of the code
 */
/**
static void yuyvToBgr24(unsigned char* dst , const unsigned char* src , const int width, const int height) {
  unsigned char *s;
  unsigned char *d;
  int l, c;
  int r, g, b, cr, cg, cb, y1, y2;
  
  l = height;
  s = (unsigned char*) src;
  d = (unsigned char*) dst;
  while (l--) {
    c = width >> 1;
    while (c--) {
      y1 = *s++;
      cb = ( ( *s - 128 ) * 454 ) >> 8;
      cg = ( *s++ - 128 ) * 88;
      y2 = *s++;
      cr = ( ( *s - 128 ) * 359 ) >> 8;
      cg = ( cg + ( *s++ - 128 ) * 183 ) >> 8;
      
      r = y1 + cr;
      b = y1 + cb;
      g = y1 - cg;
      SAT(r);
      SAT(g);
      SAT(b);
      
      *d++ = b;
      *d++ = g;
      *d++ = r;
      
      r = y2 + cr;
      b = y2 + cb;
      g = y2 - cg;
      SAT(r);
      SAT(g);
      SAT(b);
      
      *d++ = b;
      *d++ = g;
      *d++ = r;
    }
  }
}
**/

// JPEG Header to convert MJPEG to JPEG
// See http://alexmogurenko.com/blog/programming/mjpeg-to-jpeg-cpp-csharp-delphi/
static unsigned char MJPGDHTSeg[20 + 0x1A4] = {
  0xff, 0xd8,                   // SOI
  0xff, 0xe0,                   // APP0
  0x00, 0x10,                   // APP0 Hdr size
  0x4a, 0x46, 0x49, 0x46, 0x00, // ID string
  0x01, 0x01,                   // Version
  0x00,                         // Bits per type
  0x00, 0x00,                   // X density
  0x00, 0x00,                   // Y density
  0x00,                         // X Thumbnail size
  0x00,                         // Y Thumbnail size
  /* JPEG DHT Segment for YCrCb omitted from MJPG data */
  0xFF, 0xC4, 0x01, 0xA2,
  0x00, 0x00, 0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x01, 0x00, 0x03, 0x01, 0x01, 0x01, 0x01,
  0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
  0x08, 0x09, 0x0A, 0x0B, 0x10, 0x00, 0x02, 0x01, 0x03, 0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00,
  0x00, 0x01, 0x7D, 0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61,
  0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08, 0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24,
  0x33, 0x62, 0x72, 0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x34,
  0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56,
  0x57, 0x58, 0x59, 0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78,
  0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99,
  0x9A, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0xB8, 0xB9,
  0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9,
  0xDA, 0xE1, 0xE2, 0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7,
  0xF8, 0xF9, 0xFA, 0x11, 0x00, 0x02, 0x01, 0x02, 0x04, 0x04, 0x03, 0x04, 0x07, 0x05, 0x04, 0x04, 0x00, 0x01,
  0x02, 0x77, 0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06, 0x12, 0x41, 0x51, 0x07, 0x61, 0x71,
  0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91, 0xA1, 0xB1, 0xC1, 0x09, 0x23, 0x33, 0x52, 0xF0, 0x15, 0x62,
  0x72, 0xD1, 0x0A, 0x16, 0x24, 0x34, 0xE1, 0x25, 0xF1, 0x17, 0x18, 0x19, 0x1A, 0x26, 0x27, 0x28, 0x29, 0x2A,
  0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56,
  0x57, 0x58, 0x59, 0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78,
  0x79, 0x7A, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98,
  0x99, 0x9A, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0xB8,
  0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8,
  0xD9, 0xDA, 0xE2, 0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8,
  0xF9, 0xFA
};

//////////////////////////////////////////////////////////////////////////////
// Read JPEG compressed data directly from memory (not natively available in libjpeg 6b)
// (copied from http://stackoverflow.com/questions/5280756/libjpeg-ver-6b-jpeg-stdio-src-vs-jpeg-mem-src)
static void init_source(j_decompress_ptr cinfo) 
{
}

static boolean fill_input_buffer(j_decompress_ptr cinfo)
{
  ERREXIT(cinfo, JERR_INPUT_EMPTY);
  return TRUE;
}

static void skip_input_data(j_decompress_ptr cinfo, long num_bytes)
{
  struct jpeg_source_mgr* src = (struct jpeg_source_mgr*)cinfo->src;

  if(num_bytes > 0) {
    src->next_input_byte += (size_t) num_bytes;
    src->bytes_in_buffer -= (size_t) num_bytes;
  }
}
static void term_source(j_decompress_ptr cinfo) 
{
}

static void jpeg_mem_src(j_decompress_ptr cinfo, void* buffer, long nbytes)
{
  struct jpeg_source_mgr* src;

  if(cinfo->src == NULL) {   // first time for this JPEG object?
    cinfo->src = (struct jpeg_source_mgr *)
      (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_PERMANENT,
          sizeof(struct jpeg_source_mgr));
  }

  src = (struct jpeg_source_mgr*) cinfo->src;
  src->init_source = init_source;
  src->fill_input_buffer = fill_input_buffer;
  src->skip_input_data = skip_input_data;
  src->resync_to_restart = jpeg_resync_to_restart; // use default method
  src->term_source = term_source;
  src->bytes_in_buffer = nbytes;
  src->next_input_byte = (JOCTET*)buffer;
}
//////////////////////////////////////////////////////////////////////////////

void SimpleController::imageReceived(unsigned char* image, Camera::CamPixFormat pixelFormat,
                                    int width, int height, int stride, int size, int frameNb, double timestamp) {
  ControllerCallback::CaptureStatus status;
  status.totalSessionTime = length + recordingDelay;
  status.recordingDelay = recordingDelay;
  status.frameNb = frameNb;

  // Store the first timestamp so we can provide a timestamp that begins with 0
  if (firstFrameTimestamp < 0) {
    firstFrameTimestamp = timestamp;
  }

  double elapsed_time = timestamp - firstFrameTimestamp;
  if (!recording && elapsed_time > recordingDelay) {
    recording = true;
    firstRecordingFrameNumber = frameNb;
    firstRecordingFrameTimestamp = elapsed_time;
  }

  if (elapsed_time > recordingDelay+length) {
    recording = false;
    stop();
    return;
  }

  status.isRecording = recording;
  status.elapsedTime = elapsed_time;

  blitz::Array<unsigned char, 2> rgbimage;
  
  if (pixelFormat == Camera::YUYV) {
    if (2*width*sizeof(char) != (unsigned int)stride) {
      bob::core::error << "SimpleController: stride not supported" << std::endl;
      return;
    }
    
    rgbimage.resize(height, width*3);
    yuyvToRgb24(rgbimage.data(), image, width, height);
  }
  else if(pixelFormat == Camera::MJPEG) {
    // Compute the avi header size
    // See http://alexmogurenko.com/blog/programming/mjpeg-to-jpeg-cpp-csharp-delphi/
    int offset = (int(*(image + 4)) << 8) + (*(image + 5) + 4);

    // Image without avi header
    unsigned char* image_ = image + offset;
    size -= offset;

    // (Re)allocate the buffer if it is not big enough
    if (buffer == NULL || bufferSize < int(sizeof(MJPGDHTSeg) + size)) {
      delete buffer;
      bufferSize = sizeof(MJPGDHTSeg) + size;
      buffer = new unsigned char[bufferSize];

      // Copy once for all the JPEG header
      memcpy(buffer, MJPGDHTSeg, sizeof(MJPGDHTSeg));
    }
    
    // Copy image content to buffer
    memcpy(buffer + sizeof(MJPGDHTSeg), image_, size);

    // Resize output buffer
    rgbimage.resize(height, width*3);

    // Step 1: allocate and initialize JPEG decompression object
    struct jpeg_decompress_struct cinfo;
    // We set up the normal JPEG error routines.
    struct jpeg_error_mgr jerr;
    cinfo.err = jpeg_std_error(&jerr);
    // Now we can initialize the JPEG decompression object.
    jpeg_create_decompress(&cinfo);

    // Step 2: specify data source buffer
    jpeg_mem_src(&cinfo, buffer, sizeof(MJPGDHTSeg) + size);

    // Step 3: read file parameters with jpeg_read_header()
    (void) jpeg_read_header(&cinfo, TRUE);

    // Step 4: set parameters for decompression (here, use default ones)

    // Step 5: Start decompressor
    (void) jpeg_start_decompress(&cinfo);

    // Step 6: while (scan lines remain to be read)
    //           jpeg_read_scanlines(...);
    JSAMPROW obuffer[1];
    unsigned char* data_ptr = rgbimage.data();
    const int data_stride = width*3;
    while(cinfo.output_scanline < cinfo.output_height) {
      obuffer[0] = data_ptr;
      (void) jpeg_read_scanlines(&cinfo, obuffer, 1);
      data_ptr += data_stride;
    }

    // Step 7: Finish decompression
    (void) jpeg_finish_decompress(&cinfo);

    // Step 8: Release JPEG decompression object
    jpeg_destroy_decompress(&cinfo);
  }
  else if(pixelFormat == Camera::RGB24) {
    rgbimage.resize(height, width*3);
    rgbimage = blitz::Array<unsigned char, 2>(image, blitz::shape(height, width*3), blitz::neverDeleteData);
  }
  else {
    bob::core::error << "SimpleController: unsupported pixel format" << std::endl;
    return;
  }

  if (recording && outputWriter != NULL) {
    outputWriter->writeFrame(rgbimage, frameNb - firstRecordingFrameNumber, elapsed_time - firstRecordingFrameTimestamp);
  }

  pthread_mutex_lock(&callbacks_mutex);
  for(std::vector<ControllerCallback*>::iterator it = callbacks.begin(); it != callbacks.end(); it++) {
    (*it)->imageReceived(rgbimage, status);
  }
  pthread_mutex_unlock(&callbacks_mutex);
}

}}
