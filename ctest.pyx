cimport cao
from libc.stdlib cimport malloc, free
from libc.math cimport sin

cao.ao_initialize()

cdef cao.ao_sample_format fmt
fmt.bits = 16
fmt.channels = 2
fmt.rate = 44100
fmt.byte_format = 1
fmt.matrix = ""
print("format", fmt)

cdef int default_driver = cao.ao_default_driver_id()
print("default driver", default_driver)
cdef cao.ao_device *device = cao.ao_open_live(default_driver, &fmt, NULL)
print("device", "NULL" if device == NULL else "OK")

cdef int size = fmt.bits / 8 * fmt.channels * fmt.rate
cdef char *buffer = <char *>malloc(sizeof(char) * size) # 176 400
print("buffer addr", buffer)
cdef int i
cdef int sample
for i in range(0, fmt.rate):
    sample = <int>(0.75 * 32768.0 * sin(2 * 3.14 * 440.0 * i / fmt.rate))
    buffer[4 * i] = sample & 0xff
    buffer[4 * i + 1] = ((sample >> 8) & 0xff)
    buffer[4 * i + 2] = (sample & 0xff)
    buffer[4 * i + 3] = ((sample >> 8) & 0xff)

print("buffer created")
cdef int res = cao.ao_play(device, buffer, size)
print("res", res)
cao.ao_close(device)
cao.ao_shutdown()


