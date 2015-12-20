from ctypes import *


# define AO_FMT_LITTLE 1
# define AO_FMT_BIG    2
# define AO_FMT_NATIVE 4

class ao_sample_format(Structure):
    _fields_ = [("bits", c_int),
                ("rate", c_int),
                ("channels", c_int),
                ("byte_format", c_int),
                ("matrix", c_char_p)]


class ao_option(Structure):
    pass


ao_option._fields_ = [("key", c_char_p),
                      ("value", c_char_p),
                      ("next", POINTER(ao_option))]


def ao_initialize():
    lib.ao_initialize()


def ao_default_driver_id():
    """
    calls ao_default_driver_id()
    :return: -1 = error; >= 0 valid driver id
    """
    return lib.ao_default_driver_id()


def ao_open_live(driver_id, fmt, options):
    options_ref = None if options is None else byref(options)
    return lib.ao_open_live(driver_id, byref(fmt), options_ref)


def ao_play(device, output_samples, num_bytes):
    arr = (c_char * len(output_samples))(*output_samples)
    return lib.ao_play(device, arr, c_uint32(num_bytes))


def ao_close(device):
    """
    Close the device
    :param device: The device returned by ao_open_live() or ao_open_file()
    :return: 1 indicates remaining data written correctly and device closed;
    0 indicates an error while the device was being closed. If this device was writing to a file, the file may be corrupted.
    """
    return lib.ao_close(device)


def ao_shutdown():
    lib.ao_shutdown()


lib = CDLL("libao.so.4")
