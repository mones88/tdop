import math
import ctypes
import multiprocessing
import os
from threading import Thread

import libao


def play_440A():
    info("fff")
    libao.ao_initialize()
    fmt = libao.ao_sample_format()
    fmt.bits = 16
    fmt.channels = 2
    fmt.rate = 44100
    fmt.byte_format = 1

    default_driver = libao.ao_default_driver_id()
    device = libao.ao_open_live(default_driver, fmt, None)

    size = int(fmt.bits / 8 * fmt.channels * fmt.rate)
    buffer = []
    for i in range(0, fmt.rate * 5 - 1):
        sample = int((0.75 * 32768.0 * math.sin(2 * math.pi * 440.0 * i / fmt.rate)))
        buffer.append(sample & 0xff)
        buffer.append((sample >> 8) & 0xff)
        buffer.append(sample & 0xff)
        buffer.append((sample >> 8) & 0xff)

    res = libao.ao_play(device, buffer, size)

    libao.ao_close(device)
    libao.ao_shutdown()
    print("ended")


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', str(multiprocessing.current_process().pid))


if __name__ == '__main__':
    info("main line")
    p = multiprocessing.Process(target=play_440A)
    p.start()
    print("started")
    p.join()
