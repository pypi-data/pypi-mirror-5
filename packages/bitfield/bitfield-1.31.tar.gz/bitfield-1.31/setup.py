#!/usr/bin/python

import sys

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


ext_modules = [
    Extension("bitfield",
              ["cimpl/field.pyx"],
              extra_compile_args=["-g"],
              extra_link_args=["-g"],
              depends=["cimpl/field.h"]
              )
]

setup(
    name = "bitfield",
    version = "1.31",
    license = "BSD",

    description = "A Cython fast compressed number set",
    author = "Steve Stagg",
    author_email = "stestagg@gmail.com",

    url = "http://github.com/stestagg/bitfield",

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    package_data = {"Cython": ["cimpl/*.pyx"]},

    cmdclass = {"build_ext": build_ext},
    ext_modules = ext_modules,
)
