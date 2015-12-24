from ctypes import *
from multiprocessing import Manager, Process
from time import sleep

import libao
import os

# main process
__player_process = None
__manager = Manager()

# shared
__stop = None
__pause = None

# player process
__aoformat = None
__device = None
__default_driver = None


def flac_player_init():
    global __player_process, __stop, __pause
    __stop = __manager.Value(c_bool, False)
    __pause = __manager.Value(c_bool, False)
    __player_process = Process(target=__flac_process_init, args=(__stop, __pause,))
    __player_process.start()


def flac_player_dispose():
    __player_process.terminate()
    __manager.shutdown()


def flac_player_stop():
    __stop.set(True)
    __pause.set(False)


def flac_player_toggle_pause():
    __pause.set(not __pause.get())


def __flac_process_init(stop_proxy, pause_proxy):
    global __default_driver, __stop, __pause
    __stop = stop_proxy
    __pause = pause_proxy
    libao.ao_initialize()
    __default_driver = libao.ao_default_driver_id()

    while not os.path.exists("/tmp/tdop_current_track.flac"):
        sleep(0.5)

    libflac = CDLL("libFLAC.so.8")
    decoder = libflac.FLAC__stream_decoder_new()
    flac_path = c_char_p("/tmp/tdop_current_track.flac".encode()) # c_char_p(os.path.expanduser("~/test.flac").encode())

    wc = WRITE_CALLBACK(write_callback)
    mc = META_CALLBACK(metadata_callback)
    ec = ERROR_CALLBACK(error_callback)
    init_status = libflac.FLAC__stream_decoder_init_file(decoder, flac_path, wc, mc, ec, None)
    if init_status == 0:
        res = libflac.FLAC__stream_decoder_process_until_end_of_stream(decoder)
        print("res =", res)
    libao.ao_close(__device)
    libao.ao_shutdown()

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

    while __pause.get():
        sleep(0.5)
        pass

    if __stop.get():
        return 1

    blocksize = frame[0].header.blocksize
    channels = frame[0].header.channels
    decoded_size = int(blocksize * channels * (__aoformat.bits / 8))
    aobuffer = []
    for i in range(0, blocksize):
        left_channel = buffer[0][i]
        right_channel = buffer[1][i]
        aobuffer.append(left_channel & 0xff)
        aobuffer.append((left_channel >> 8) & 0xff)
        # aobuffer.append((left_channel >> 16) & 0xff)
        aobuffer.append(right_channel & 0xff)
        aobuffer.append((right_channel >> 8) & 0xff)
        #  aobuffer.append((right_channel >> 16) & 0xff)

    res = libao.ao_play(__device, aobuffer, decoded_size)
    if res == 0:
        print("ao fail")
    return 0


def metadata_callback(decoder, metadata, client_data):
    global __aoformat, __device
    print("metadata")
    __aoformat = libao.ao_sample_format()
    __aoformat.bits = metadata[0].data.stream_info.bits_per_sample
    __aoformat.channels = metadata[0].data.stream_info.channels
    __aoformat.rate = metadata[0].data.stream_info.sample_rate
    __aoformat.byte_format = 1
    print("format", __aoformat.bits, __aoformat.channels, __aoformat.rate)
    __device = libao.ao_open_live(__default_driver, __aoformat, None)
    pass


def error_callback(decoder, status, client_data):
    print("error")
    pass
