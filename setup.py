from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

ext_modules = [
    Extension("flac_player",
              sources=["flac_player.pyx"],
              libraries=["ao", "m", "FLAC"]
              )
]

setup(
        name='tdop',
        ext_modules=cythonize(ext_modules)
)
