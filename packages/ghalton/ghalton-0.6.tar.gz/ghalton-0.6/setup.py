#!/usr/bin/env python

from distutils.core import setup, Extension

ghalton_module = Extension("_ghalton", sources=["src/Halton_wrap.cxx", "src/Halton.cpp"])

version = "0.6"

setup (name = "ghalton",
       version = version,
       author = "Francois-Michel De Rainville",
       author_email = "f.derainville@gmail.com",
       license = "LICENSE.txt",
       description = "Generalized Halton number generator",
       long_description = open("README.md").read(),
       url='https://github.com/fmder/ghalton',
       download_url = "https://github.com/fmder/ghalton/tarball/%s" % version,
       classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Scientific/Engineering',
        ],
       ext_modules = [ghalton_module],
       py_modules = ["ghalton"],
       )
