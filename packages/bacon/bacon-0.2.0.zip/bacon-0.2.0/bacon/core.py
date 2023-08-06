from bacon import native
from ctypes import *
import collections
import os
import logging

logger = logging.getLogger(__name__)

# Convert return codes into exceptions.
class BaconError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code

    def __repr__(self):
        return '%s(%d)' % (self.__class__.__name__, self.error_code)

    _error_classes = {}

    @classmethod
    def _register_error_class(cls, error_code, error_class):
        cls._error_classes[error_code] = error_class

    @classmethod
    def _from_error_code(cls, error_code):
        try:
            error_class = cls._error_classes[error_code]
        except KeyError:
            error_class = BaconError
        return error_class(error_code)

def error_code(error_code):
    def wrap(cls):
        BaconError._register_error_class(error_code, cls)
        return cls
    return wrap

@error_code(native.ErrorCodes.unknown)
class UnknownError(BaconError):
    pass

@error_code(native.ErrorCodes.invalid_argument)
class InvalidArgumentError(BaconError):
    pass

@error_code(native.ErrorCodes.invalid_handle)
class InvalidHandleError(BaconError):
    pass

@error_code(native.ErrorCodes.stack_underflow)
class StackUnderflowError(BaconError):
    pass

@error_code(native.ErrorCodes.unsupported_format)
class UnsupportedFormatError(BaconError):
    pass

@error_code(native.ErrorCodes.shader_compile_error)
class ShaderCompileError(BaconError):
    pass

@error_code(native.ErrorCodes.shader_link_error)
class ShaderLinkError(BaconError):
    pass

@error_code(native.ErrorCodes.not_rendering)
class NotRenderingError(BaconError):
    pass

@error_code(native.ErrorCodes.invalid_font_size)
class InvalidFontSizeError(BaconError):
    pass

@error_code(native.ErrorCodes.not_looping)
class NotLoopingError(BaconError):
    pass

def _error_wrapper(fn):
    def f(*args):
        result = fn(*args)
        if result != native.ErrorCodes.none:
            raise BaconError._from_error_code(result)
    return f

lib = native.load(function_wrapper = _error_wrapper)

_log_level_map = {
    native.LogLevels.trace: logging.DEBUG,
    native.LogLevels.info: logging.INFO,
    native.LogLevels.warning: logging.WARNING,
    native.LogLevels.error: logging.ERROR,
    native.LogLevels.fatal: logging.FATAL,
}

def _log_callback(level, message):
    try:
        level = _log_level_map[level]
    except KeyError:
        level = logging.ERROR
    logger.log(level, message.decode('utf-8'))

# Initialize library now
if not native._mock_native:
    _log_callback_handle = lib.LogCallback(_log_callback)
    lib.SetLogCallback(_log_callback_handle)
    lib.Init()

    # Expose library version
    major_version = c_int()
    minor_version = c_int()
    patch_version = c_int()
    lib.GetVersion(byref(major_version), byref(minor_version), byref(patch_version))
    major_version = major_version.value     #: Major version number of the Bacon dynamic library that was loaded, as an integer.
    minor_version = minor_version.value     #: Minor version number of the Bacon dynamic library that was loaded, as an integer.
    patch_version = patch_version.value     #: Patch version number of the Bacon dynamic library that was loaded, as an integer.
else:
    major_version, minor_version, patch_version = (0, 1, 0)

#: Version of the Bacon dynamic library that was loaded, in the form ``"major.minor.patch"``.
version = '%d.%d.%d' % (major_version, minor_version, patch_version)

