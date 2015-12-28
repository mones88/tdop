cdef extern from "FLAC/all.h":
    ctypedef struct FLAC__StreamDecoder:
        pass

    cdef enum FLAC__StreamDecoderInitStatus:
        pass

    cdef enum FLAC__StreamDecoderWriteStatus:
        pass

    ctypedef union number:
        FLAC__uint32 frame_number
        FLAC__uint64 sample_number
        pass

    ctypedef struct FLAC__FrameHeader:
        unsigned blocksize
        unsigned sample_rate
        unsigned channels
        int channel_assignment
        unsigned bits_per_sample
        int number_type
        number number
        FLAC__uint8 crc
        pass

    ctypedef struct FLAC__Frame:
        FLAC__FrameHeader header
        # FLAC__Subframe subframes[FLAC__MAX_CHANNELS]
        # FLAC__FrameFooter footer
        pass

    ctypedef FLAC__StreamDecoderWriteStatus(* FLAC__StreamDecoderWriteCallback)(const FLAC__StreamDecoder *decoder, const FLAC__Frame *frame, const FLAC__int32 *const buffer[], void *client_data)
    ctypedef void(* FLAC__StreamDecoderErrorCallback )(const FLAC__StreamDecoder *decoder, FLAC__StreamDecoderErrorStatus status, void *client_data)

    FLAC__StreamDecoder * 	FLAC__stream_decoder_new()
    FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_file(FLAC__StreamDecoder * 	decoder, const char * 	filename, FLAC__StreamDecoderWriteCallback 	write_callback, FLAC__StreamDecoderMetadataCallback metadata_callback, FLAC__StreamDecoderErrorCallback error_callback, void * client_data)