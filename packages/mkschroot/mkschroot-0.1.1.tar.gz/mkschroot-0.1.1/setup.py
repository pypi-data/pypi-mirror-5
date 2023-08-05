import os
from setuptools import setup

def read(fname1, fname2):
    if os.path.exists(fname1):
        fname = fname1
    else:
        fname = fname2
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mkschroot",
    version = "0.1.1",
    author = "Kirit Saelensminde",
    author_email = "kirit@felspar.com",
    url='https://github.com/KayEss/mkschroot',
    description = ("A simple script for making schroot environments from a JSON configuration file"),
    long_description = read('README','README.md'),
    license = "Boost Software License - Version 1.0 - August 17th, 2003",
    keywords = "chroot debian devops",
    scripts = ['bin/mkschroot'],
    packages = [],
    install_requires = ['simplejson'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved",
    ],
)
