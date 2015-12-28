from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

ext_modules = [
    Extension("ctest",
              sources=["ctest.pyx"],
              libraries=["ao", "m", "FLAC"]
              )
]

setup(
        name='tdop',
        ext_modules=cythonize(ext_modules)
)
