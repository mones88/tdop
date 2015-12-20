import math
import ctypes

import libao

format = libao.ao_sample_format()
format.bits = 16
format.channels = 2
format.rate = 44100
format.byte_format = 1

libao.ao_initialize()
default_driver = libao.ao_default_driver_id()
device = libao.ao_open_live(default_driver, format, None)

'''
/* -- Play some stuff -- */
	buf_size = format.bits/8 * format.channels * format.rate;
	buffer = calloc(buf_size,
			sizeof(char));

	for (i = 0; i < format.rate; i++) {
		sample = (int)(0.75 * 32768.0 *
			sin(2 * M_PI * freq * ((float) i/format.rate)));

		/* Put the same stuff in left and right channel */
		buffer[4*i] = buffer[4*i+2] = sample & 0xff;
		buffer[4*i+1] = buffer[4*i+3] = (sample >> 8) & 0xff;
	}
	ao_play(device, buffer, buf_size);
'''
size = int(format.bits / 8 * format.channels * format.rate)
buffer = []
for i in range(0, format.rate * 5 - 1):
    sample = int((0.75 * 32768.0 * math.sin(2 * math.pi * 440.0 * i / format.rate)))
    buffer.append(sample & 0xff)
    buffer.append((sample >> 8) & 0xff)
    buffer.append(sample & 0xff)
    buffer.append((sample >> 8) & 0xff)

res = libao.ao_play(device, buffer, size)

libao.ao_close(device)
libao.ao_shutdown()
