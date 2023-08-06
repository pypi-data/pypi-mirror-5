import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="Pebble",
    version="0.1.1",
    author="Matteo Cafasso",
    author_email="noxdafox@gmail.com",
    description=("Threading and multiprocessing eye-candy."),
    license="LGPL",
    keywords="threading mutltiprocessing pool decorators",
    url="https://github.com/noxdafox/pebble",
    packages=['pebble', 'tests'],
    long_description=read('README.txt'),
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)"
    ],
)
