from libc.stdint cimport *

cdef extern from "FLAC/all.h":
    ctypedef int8_t FLAC__int8
    ctypedef uint8_t FLAC__uint8
    ctypedef int16_t FLAC__int16
    ctypedef int32_t FLAC__int32
    ctypedef int64_t FLAC__int64
    ctypedef uint16_t FLAC__uint16
    ctypedef uint32_t FLAC__uint32
    ctypedef uint64_t FLAC__uint64
    ctypedef int FLAC__bool;
    ctypedef FLAC__uint8 FLAC__byte;

    ctypedef struct FLAC__StreamDecoder:
        pass

    ctypedef enum FLAC__StreamDecoderInitStatus:
        FLAC__STREAM_DECODER_INIT_STATUS_OK = 0,
        FLAC__STREAM_DECODER_INIT_STATUS_UNSUPPORTED_CONTAINER,
        FLAC__STREAM_DECODER_INIT_STATUS_INVALID_CALLBACKS,
        FLAC__STREAM_DECODER_INIT_STATUS_MEMORY_ALLOCATION_ERROR,
        FLAC__STREAM_DECODER_INIT_STATUS_ERROR_OPENING_FILE,
        FLAC__STREAM_DECODER_INIT_STATUS_ALREADY_INITIALIZED
        pass

    ctypedef enum FLAC__StreamDecoderWriteStatus:
        FLAC__STREAM_DECODER_WRITE_STATUS_CONTINUE,
        FLAC__STREAM_DECODER_WRITE_STATUS_ABORT
        pass

    ctypedef enum FLAC__StreamDecoderErrorStatus:
        FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC,
        FLAC__STREAM_DECODER_ERROR_STATUS_BAD_HEADER,
        FLAC__STREAM_DECODER_ERROR_STATUS_FRAME_CRC_MISMATCH,
        FLAC__STREAM_DECODER_ERROR_STATUS_UNPARSEABLE_STREAM
        pass

    ctypedef enum FLAC__MetadataType:
        FLAC__METADATA_TYPE_STREAMINFO = 0,
        FLAC__METADATA_TYPE_PADDING = 1,
        FLAC__METADATA_TYPE_APPLICATION = 2,
        FLAC__METADATA_TYPE_SEEKTABLE = 3,
        FLAC__METADATA_TYPE_VORBIS_COMMENT = 4,
        FLAC__METADATA_TYPE_CUESHEET = 5,
        FLAC__METADATA_TYPE_PICTURE = 6,
        FLAC__METADATA_TYPE_UNDEFINED = 7,
        FLAC__MAX_METADATA_TYPE = 126u
        pass

    #ctypedef union number:
     #   FLAC__uint32 frame_number
     #   FLAC__uint64 sample_number
     #   pass

    ctypedef struct FLAC__FrameHeader:
        unsigned blocksize
        unsigned sample_rate
        unsigned channels
        int channel_assignment
        unsigned bits_per_sample
        int number_type
        # number number
        FLAC__uint8 crc
        pass

    ctypedef struct FLAC__Frame:
        FLAC__FrameHeader header
        # FLAC__Subframe subframes[FLAC__MAX_CHANNELS]
        # FLAC__FrameFooter footer
        pass

    ctypedef struct FLAC__StreamMetadata_StreamInfo:
        unsigned min_blocksize
        unsigned max_blocksize
        unsigned min_framesize
        unsigned max_framesize
        unsigned sample_rate
        unsigned channels
        unsigned bits_per_sample
        FLAC__uint64 total_samples
        FLAC__byte md5sum[16]

    ctypedef union data:
        FLAC__StreamMetadata_StreamInfo stream_info
        pass

    ctypedef struct FLAC__StreamMetadata:
        FLAC__MetadataType type
        FLAC__bool is_last
        unsigned length
        data data
        pass

    ctypedef FLAC__StreamDecoderWriteStatus(* FLAC__StreamDecoderWriteCallback)(const FLAC__StreamDecoder *decoder, const FLAC__Frame *frame, const FLAC__int32 *const buffer[], void *client_data)
    ctypedef void(* FLAC__StreamDecoderErrorCallback )(const FLAC__StreamDecoder *decoder, FLAC__StreamDecoderErrorStatus status, void *client_data)
    ctypedef void (*FLAC__StreamDecoderMetadataCallback)(const FLAC__StreamDecoder *decoder, const FLAC__StreamMetadata *metadata, void *client_data)

    FLAC__StreamDecoder * 	FLAC__stream_decoder_new()
    FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_file(FLAC__StreamDecoder * 	decoder, const char * 	filename, FLAC__StreamDecoderWriteCallback 	write_callback, FLAC__StreamDecoderMetadataCallback metadata_callback, FLAC__StreamDecoderErrorCallback error_callback, void * client_data)
    FLAC__bool FLAC__stream_decoder_process_until_end_of_stream(FLAC__StreamDecoder *decoder)