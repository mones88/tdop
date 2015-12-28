cdef extern from "ao/ao.h":
    ctypedef struct ao_sample_format:
        int  bits
        int  rate
        int  channels
        int  byte_format
        char *matrix
        pass

    ctypedef struct ao_option:
        char *key
        char *value
        ao_option *next
        pass

    ctypedef struct ao_device:
        pass


    void ao_initialize()
    void ao_shutdown()

    int ao_default_driver_id()
    ao_device* ao_open_live(int driver_id, ao_sample_format *format, ao_option *options)
    int ao_play(ao_device *device, char *output_samples, unsigned num_bytes)
    int ao_close(ao_device *device)