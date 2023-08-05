#!/usr/bin/env python

from Evtx import __version__
from setuptools import setup

long_description="""python-evtx is a pure Python parser for recent Windows Event Log files (those with the file extension ".evtx"). The module provides programmatic access to the File and Chunk headers, record templates, and event entries. For example, you can use python-evtx to review the event logs of Windows 7 systems from a Mac or Linux workstation. The structure definitions and parsing strategies were heavily inspired by the work of Andreas Schuster and his Perl implementation "Parse-Evtx"."""

setup(name="python-evtx",
      version=__version__,
      description="Pure Python parser for recent Windows event log files (.evtx).",
      long_description=long_description,
      author="Willi Ballenthin",
      author_email="willi.ballenthin@gmail.com",
      url="https://github.com/williballenthin/python-evtx",
      license="Apache 2.0 License",
      packages=["Evtx"])
