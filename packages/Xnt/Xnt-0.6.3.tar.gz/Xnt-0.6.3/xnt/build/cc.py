#!/usr/bin/env python
"""Common Compilers

Definition of commonly used compilers
"""

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2013  Kenny Ballou

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging
from xnt.tasks import call, which

LOGGER = logging.getLogger(__name__)

def gcc(src, flags=None):
    """gcc compiler, non-named output file

    :param src: C source file to compile with default `gcc`
    :param flags: List of flags to pass onto the compiler
    """
    assert which("gcc")
    return _gcc(src, flags)

def gpp(src, flags=None):
    """g++ compiler, non-named output file

    :param src: C++ source file to compile with default `g++`
    :param flags: List of flags to pass onto the compiler
    """
    assert which("g++")
    return _gcc(src, flags, "g++")

def gcc_o(src, output, flags=None):
    """gcc compiler, with output file

    :param src: C source file to compile with default `gcc`
    :param output: Name of resulting object or executable
    :param flags: List of flags to pass onto the compiler
    """
    assert which("gcc")
    return _gcc_o(src, output, flags)

def gpp_o(src, output, flags=None):
    """g++ compiler, with output file

    :param src: C++ source file to compile with default `g++`
    :param output: Name of resulting object or executable
    :param flags: List of flags to pass onto the compiler
    """
    assert which("g++")
    return _gcc_o(src, output, flags, "g++")

def javac(src, flags=None):
    """Javac: compile Java programs

    :param src: Java source file to compile with default `javac`
    :param flags: List of flags to pass onto the compiler
    """
    assert which("javac")
    LOGGER.info("Compiling %s", src)
    cmd = __generate_command(src, flags, "javac")
    return __compile(cmd)

def nvcc(src, flags=None):
    """NVCC: compile CUDA C/C++ programs

    :param src: CUDA source file to compile with default `nvcc`
    :param flags: List of flags to pass onto the compiler
    """
    assert which('nvcc')
    return _gcc(src, flags, compiler='nvcc')

def nvcc_o(src, output, flags=None):
    """NVCC: compile with named output

    :param src: CUDA source file to compile with default `nvcc`
    :param output: Name of resulting object or executable
    :param flags: List of flags to pass onto the compiler
    """
    assert which('nvcc')
    return _gcc_o(src, output, flags, compiler='nvcc')

def _gcc(src, flags=None, compiler="gcc"):
    """Compile using gcc"""
    LOGGER.info("Compiling %s", src)
    return __compile(__generate_command(src, flags, compiler))

def _gcc_o(src, output, flags=None, compiler="gcc"):
    """Compile with gcc specifying output file name"""
    LOGGER.info("Compiling %s to %s", src, output)
    cmd = __generate_command(src, flags, compiler)
    cmd.append("-o")
    cmd.append(output)
    return __compile(cmd)

def __generate_command(src, flags=None, compiler="gcc"):
    """Generate cmd list for call"""
    cmd = [compiler, src]
    if flags:
        for flag in flags:
            cmd.append(flag)
    return cmd

def __compile(cmd):
    """Run Compile, using `xnt.tasks.call`"""
    return call(cmd)

def __is_newer(file_a, file_b):
    """Compare mmtimes of files
    Return True if `file_a` is modified later than `file_b`
    """
    return os.path.getmtime(file_a) > os.path.getmtime(file_b)
