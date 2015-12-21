from ctypes import *

import math

import libao
import os

aoformat = None


class FLAC__StreamMetadata_StreamInfo(Structure):
    _fields_ = [("min_blocksize", c_uint),
                ("max_blocksize", c_uint),
                ("min_framesize", c_uint),
                ("max_framesize", c_uint),
                ("sample_rate", c_uint),
                ("channels", c_uint),
                ("bits_per_sample", c_uint),
                ("total_samples", c_uint64),
                ("md5sum", c_byte * 16)]


class FLAC_data(Union):
    _fields_ = [("stream_info", FLAC__StreamMetadata_StreamInfo)]


class FLAC__StreamMetadata(Structure):
    _fields_ = [("type", c_int),
                ("is_last", c_int),
                ("length", c_uint),
                ("data", FLAC_data)]


class FLAC__FrameHeader(Structure):
    _fields_ = [("blocksize", c_uint),
                ("sample_rate", c_uint),
                ("channels", c_uint),
                ("channel_assignment", c_int),
                ("bits_per_sample", c_uint),
                ("number_type", c_int),
                ("number", c_uint64),
                ("crc", c_uint8)]


class FLAC__Frame(Structure):
    _fields_ = [("header", FLAC__FrameHeader)]


META_CALLBACK = CFUNCTYPE(None, POINTER(c_void_p), POINTER(FLAC__StreamMetadata), POINTER(c_void_p))
WRITE_CALLBACK = CFUNCTYPE(c_int, POINTER(c_void_p), POINTER(FLAC__Frame), POINTER(POINTER(c_int32)), POINTER(c_void_p))
ERROR_CALLBACK = CFUNCTYPE(None, POINTER(c_void_p), c_int, POINTER(c_void_p))


def write_callback(decoder, frame, buffer, client_data):
    print("write callback")
    '''
    for(i = 0; i < frame->header.blocksize; i++) {
		if(
			!write_little_endian_int16(f, (FLAC__int16)buffer[0][i]) ||  /* left channel */
			!write_little_endian_int16(f, (FLAC__int16)buffer[1][i])     /* right channel */
		) {
			fprintf(stderr, "ERROR: write error\n");
			return FLAC__STREAM_DECODER_WRITE_STATUS_ABORT;
		}
	}
    '''
    blocksize = frame[0].header.blocksize
    channels = frame[0].header.channels
    decoded_size = int(blocksize * channels * (aoformat.bits / 8))
    aobuffer = []
    for i in range(0, blocksize):
        left_channel = buffer[0][i]
        right_channel = buffer[1][i]
        aobuffer.append(left_channel & 0xff)
        aobuffer.append((left_channel >> 8) & 0xff)
        aobuffer.append((left_channel >> 16) & 0xff)
        aobuffer.append(right_channel & 0xff)
        aobuffer.append((right_channel >> 8) & 0xff)
        aobuffer.append((right_channel >> 16) & 0xff)

    res = libao.ao_play(device, aobuffer, decoded_size)
    if res == 0:
        print("ao fail")

    return 0


def metadata_callback(decoder, metadata, client_data):
    global aoformat
    global device
    print("metadata")
    aoformat = libao.ao_sample_format()
    aoformat.bits = metadata[0].data.stream_info.bits_per_sample
    aoformat.channels = metadata[0].data.stream_info.channels
    aoformat.rate = metadata[0].data.stream_info.sample_rate
    aoformat.byte_format = 1
    print("format", aoformat.bits, aoformat.channels, aoformat.rate)
    device = libao.ao_open_live(default_driver, aoformat, None)
    pass


def error_callback(decoder, status, client_data):
    print("error")
    pass


libao.ao_initialize()
default_driver = libao.ao_default_driver_id()
device = None

libflac = CDLL("libFLAC.so.8")
# file = open(os.path.expanduser("~/test.flac"), mode="r")
decoder = libflac.FLAC__stream_decoder_new()
flac_path = c_char_p(os.path.expanduser("~/test24bit.flac").encode())

wc = WRITE_CALLBACK(write_callback)
mc = META_CALLBACK(metadata_callback)
ec = ERROR_CALLBACK(error_callback)
init_status = libflac.FLAC__stream_decoder_init_file(decoder, flac_path, wc, mc, ec, None)
if init_status == 0:
    res = libflac.FLAC__stream_decoder_process_until_end_of_stream(decoder)
    print(res)

libao.ao_close(device)
libao.ao_shutdown()