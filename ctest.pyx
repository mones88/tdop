cimport cao
from cflac cimport *
from libc.stdlib cimport malloc, free
from libc.math cimport sin


cdef FLAC__StreamDecoderWriteStatus write(const FLAC__StreamDecoder *decoder, const FLAC__Frame *frame, const FLAC__int32 *const buffer[], void *client_data):
    cdef FLAC__FrameHeader header = frame[0].header
    cdef int decoded_size = header.blocksize * header.channels * (header.bits_per_sample / 8)
    cdef char *aobuffer = <char *>malloc(sizeof(char) * decoded_size)
    cdef FLAC__int32 left_channel = 0
    cdef FLAC__int32 right_channel = 0
    cdef size_t i = 0
    for i in range(0, header.blocksize):
        left_channel = buffer[0][i]
        right_channel = buffer[1][i]
        aobuffer[4 * i] = left_channel & 0xff
        aobuffer[4 * i + 1] = ((left_channel >> 8) & 0xff)
        aobuffer[4 * i + 2] = (right_channel & 0xff)
        aobuffer[4 * i + 3] = ((right_channel >> 8) & 0xff)

    print("buffer created")
    print("device", "NULL" if device == NULL else "OK")
    cdef int res = cao.ao_play(device, aobuffer, decoded_size)
    print("res", str(res))
    return FLAC__STREAM_DECODER_WRITE_STATUS_CONTINUE


cdef void metadata(const FLAC__StreamDecoder *decoder, const FLAC__StreamMetadata *metadata, void *client_data):
    global device
    cdef FLAC__StreamMetadata info = metadata[0]
    cdef cao.ao_sample_format fmt
    fmt.bits = info.data.stream_info.bits_per_sample
    fmt.channels = info.data.stream_info.channels
    fmt.rate = info.data.stream_info.sample_rate
    fmt.byte_format = 1
    fmt.matrix = ""
    print("format", fmt)
    device = cao.ao_open_live(default_driver, &fmt, NULL)
    print("device", "NULL" if device == NULL else "OK")
    pass

cdef void error(const FLAC__StreamDecoder *decoder, FLAC__StreamDecoderErrorStatus status, void *client_data):
    print("ERROR")
    pass

cdef cao.ao_device *device = NULL
cao.ao_initialize()
cdef int default_driver = cao.ao_default_driver_id()
print("default driver", default_driver)

cdef FLAC__StreamDecoder *decoder = FLAC__stream_decoder_new()
print("decoder instance:", "NULL" if decoder == NULL else "OK")
cdef FLAC__StreamDecoderInitStatus status = FLAC__stream_decoder_init_file(decoder, "/home/mones/test.flac", write, metadata, error, NULL)
cdef FLAC__bool result = 0
if status == FLAC__STREAM_DECODER_INIT_STATUS_OK:
    print("decoder initialized")
    result = FLAC__stream_decoder_process_until_end_of_stream(decoder)
else:
    print("decoder failed to initialize")

cao.ao_close(device)
cao.ao_shutdown()