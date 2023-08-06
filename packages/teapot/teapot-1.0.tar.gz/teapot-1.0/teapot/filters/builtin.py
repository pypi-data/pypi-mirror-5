"""
The built-in filters.
"""

import os
import sys
import distutils

from teapot.filters.decorators import named_filter


@named_filter('windows')
def windows():
    """
    Check if the platform is windows.
    """

    return sys.platform.startswith('win32')

@named_filter('linux')
def linux():
    """
    Check if the platform is windows.
    """

    return sys.platform.startswith('linux')

@named_filter('darwin')
def darwin():
    """
    Check if the platform is darwin.
    """

    return sys.platform.startswith('darwin')

@named_filter('unix')
def unix():
    """
    Check if the platform is unix.
    """

    return linux() or darwin()

@named_filter('msvc', depends='windows')
def msvc():
    """
    Check if MSVC is available.
    """

    return 'VCINSTALLDIR' in os.environ

@named_filter('mingw', depends='windows')
def mingw():
    """
    Check if MinGW is available.
    """

    return bool(distutils.spawn.find_executable('gcc'))
