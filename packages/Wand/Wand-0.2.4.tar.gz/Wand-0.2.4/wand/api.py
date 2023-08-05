""":mod:`wand.api` --- Low-level interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionchanged:: 0.1.10
   Changed to throw :exc:`~exceptions.ImportError` instead of
   :exc:`~exceptions.AttributeError` when the shared library fails to load.

"""
import ctypes
import ctypes.util
import os
import os.path
import platform
import sys

__all__ = 'load_library', 'MagickPixelPacket', 'library', 'libmagick', 'libc'


def find_library(suffix=''):
    """Finds library path to try loading.  The result paths are not
    guarenteed that they exist.

    :param suffix: optional suffix e.g. ``'-Q16'``
    :type suffix: :class:`basestring`
    :returns: a pair of libwand and libmagick paths.  they can be the same.
              path can be ``None`` as well
    :rtype: :class:`tuple`

    """
    libwand = None
    system = platform.system()
    magick_home = os.environ.get('MAGICK_HOME')
    if magick_home:
        if system == 'Windows':
            libwand = 'CORE_RL_wand_{0}.dll'.format(suffix),
        elif system == 'Darwin':
            libwand = 'lib', 'libMagickWand{0}.dylib'.format(suffix),
        else:
            libwand = 'lib', 'libMagickWand{0}.so'.format(suffix),
        libwand = os.path.join(magick_home, *libwand)
    else:
        if system == 'Windows':
            libwand = ctypes.util.find_library('CORE_RL_wand_' + suffix)
        else:
            libwand = ctypes.util.find_library('MagickWand' + suffix)
    if system == 'Windows':
        # On Windows, the API is split between two libs. On other platforms,
        # it's all contained in one.
        libmagick_filename = 'CORE_RL_magick_' + suffix
        if magick_home:
            libmagick = os.path.join(magick_home, libmagick_filename + '.dll')
        else:
            libmagick = ctypes.util.find_library(libmagick_filename)
        return libwand, libmagick
    return libwand, libwand


def load_library():
    """Loads the MagickWand library.

    :returns: the MagickWand library and the ImageMagick library
    :rtype: :class:`ctypes.CDLL`

    """
    tried_paths = []
    for suffix in '', '-Q16', '-Q8', '-6.Q16':
        libwand_path, libmagick_path = find_library(suffix)
        if libwand_path is None or libmagick_path is None:
            continue
        tried_paths.append(libwand_path)
        try:
            libwand = ctypes.CDLL(libwand_path)
            if libwand_path == libmagick_path:
                libmagick = libwand
            else:
                tried_paths.append(libmagick_path)
                libmagick = ctypes.CDLL(libmagick_path)
        except (IOError, OSError):
            continue
        return libwand, libmagick
    raise IOError('cannot find library; tried paths: ' + repr(tried_paths))


if not hasattr(ctypes, 'c_ssize_t'):
    if ctypes.sizeof(ctypes.c_uint) == ctypes.sizeof(ctypes.c_void_p):
        ctypes.c_ssize_t = ctypes.c_int
    elif ctypes.sizeof(ctypes.c_ulong) == ctypes.sizeof(ctypes.c_void_p):
        ctypes.c_ssize_t = ctypes.c_long
    elif ctypes.sizeof(ctypes.c_ulonglong) == ctypes.sizeof(ctypes.c_void_p):
        ctypes.c_ssize_t = ctypes.c_longlong


class MagickPixelPacket(ctypes.Structure):

    _fields_ = [('storage_class', ctypes.c_int),
                ('colorspace', ctypes.c_int),
                ('matte', ctypes.c_int),
                ('fuzz', ctypes.c_double),
                ('depth', ctypes.c_size_t),
                ('red', ctypes.c_double),
                ('green', ctypes.c_double),
                ('blue', ctypes.c_double),
                ('opacity', ctypes.c_double),
                ('index', ctypes.c_double)]


# Preserve the module itself even if it fails to import
sys.modules['wand._api'] = sys.modules['wand.api']

try:
    libraries = load_library()
except (OSError, IOError):
    raise ImportError('MagickWand shared library not found')

#: (:class:`ctypes.CDLL`) The MagickWand library.
library = libraries[0]

#: (:class:`ctypes.CDLL`) The ImageMagick library.  It is the same with
#: :data:`library` on platforms other than Windows.
#:
#: .. versionadded:: 0.1.10
libmagick = libraries[1]

try:
    library.MagickWandGenesis.argtypes = []
    library.MagickWandTerminus.argtypes = []

    library.NewMagickWand.argtypes = []
    library.NewMagickWand.restype = ctypes.c_void_p

    library.MagickNewImage.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_void_p]

    library.DestroyMagickWand.argtypes = [ctypes.c_void_p]
    library.DestroyMagickWand.restype = ctypes.c_void_p

    library.CloneMagickWand.argtypes = [ctypes.c_void_p]
    library.CloneMagickWand.restype = ctypes.c_void_p

    library.IsMagickWand.argtypes = [ctypes.c_void_p]

    library.MagickGetException.argtypes = [ctypes.c_void_p,
                                           ctypes.POINTER(ctypes.c_int)]
    library.MagickGetException.restype = ctypes.c_char_p

    library.MagickClearException.argtypes = [ctypes.c_void_p]

    library.MagickSetFilename.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    library.MagickReadImageBlob.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                            ctypes.c_size_t]

    library.MagickReadImage.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    library.MagickReadImageFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    library.MagickGetImageFormat.argtypes = [ctypes.c_void_p]
    library.MagickGetImageFormat.restype = ctypes.c_char_p

    library.MagickSetImageFormat.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    libmagick.MagickToMime.argtypes = [ctypes.c_char_p]
    libmagick.MagickToMime.restype = ctypes.POINTER(ctypes.c_char)

    library.MagickGetImageSignature.argtypes = [ctypes.c_void_p]
    library.MagickGetImageSignature.restype = ctypes.c_char_p

    library.MagickGetImageBackgroundColor.argtypes = [ctypes.c_void_p,
                                                      ctypes.c_void_p]

    library.MagickSetImageBackgroundColor.argtypes = [ctypes.c_void_p,
                                                      ctypes.c_void_p]

    library.MagickGetImageAlphaChannel.argtypes = [ctypes.c_void_p]
    library.MagickGetImageAlphaChannel.restype = ctypes.c_size_t

    library.MagickSetImageAlphaChannel.argtypes = [ctypes.c_void_p,
                                                   ctypes.c_int]

    library.MagickGetImageBlob.argtypes = [ctypes.c_void_p,
                                           ctypes.POINTER(ctypes.c_size_t)]
    library.MagickGetImageBlob.restype = ctypes.POINTER(ctypes.c_ubyte)

    library.MagickWriteImage.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    library.MagickWriteImageFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    library.MagickGetImageWidth.argtypes = [ctypes.c_void_p]
    library.MagickGetImageWidth.restype = ctypes.c_size_t

    library.MagickGetImageHeight.argtypes = [ctypes.c_void_p]
    library.MagickGetImageHeight.restype = ctypes.c_size_t

    library.MagickGetImageUnits.argtypes = [ctypes.c_void_p]

    library.MagickSetImageUnits.argtypes = [ctypes.c_void_p, ctypes.c_int]

    library.MagickGetImageDepth.argtypes = [ctypes.c_void_p]
    library.MagickGetImageDepth.restype = ctypes.c_size_t

    library.MagickSetImageDepth.argtypes = [ctypes.c_void_p]

    library.MagickCropImage.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                        ctypes.c_size_t, ctypes.c_ssize_t,
                                        ctypes.c_ssize_t]

    library.MagickResetImagePage.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    library.MagickResizeImage.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                          ctypes.c_size_t, ctypes.c_int,
                                          ctypes.c_double]

    library.MagickTransformImage.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                             ctypes.c_char_p]
    library.MagickTransformImage.restype = ctypes.c_void_p

    library.MagickRotateImage.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                          ctypes.c_double]

    library.MagickResetIterator.argtypes = [ctypes.c_void_p]

    library.MagickIdentifyImage.argtypes = [ctypes.c_void_p]
    library.MagickIdentifyImage.restype = ctypes.c_char_p

    library.MagickRelinquishMemory.argtypes = [ctypes.c_void_p]
    library.MagickRelinquishMemory.restype = ctypes.c_void_p

    library.NewPixelIterator.argtypes = [ctypes.c_void_p]
    library.NewPixelIterator.restype = ctypes.c_void_p

    library.DestroyPixelIterator.argtypes = [ctypes.c_void_p]
    library.DestroyPixelIterator.restype = ctypes.c_void_p

    library.ClonePixelIterator.argtypes = [ctypes.c_void_p]
    library.ClonePixelIterator.restype = ctypes.c_void_p

    library.IsPixelIterator.argtypes = [ctypes.c_void_p]

    library.PixelGetIteratorException.argtypes = [ctypes.c_void_p,
                                                  ctypes.POINTER(ctypes.c_int)]
    library.PixelGetIteratorException.restype = ctypes.c_char_p

    library.PixelClearIteratorException.argtypes = [ctypes.c_void_p]

    library.PixelSetFirstIteratorRow.argtypes = [ctypes.c_void_p]

    library.PixelSetIteratorRow.argtypes = [ctypes.c_void_p, ctypes.c_ssize_t]

    library.PixelGetNextIteratorRow.argtypes = [ctypes.c_void_p,
                                                ctypes.POINTER(ctypes.c_size_t)]
    library.PixelGetNextIteratorRow.restype = ctypes.POINTER(ctypes.c_void_p)

    library.NewPixelWand.restype = ctypes.c_void_p

    library.DestroyPixelWand.argtypes = [ctypes.c_void_p]
    library.DestroyPixelWand.restype = ctypes.c_void_p

    library.IsPixelWand.argtypes = [ctypes.c_void_p]

    library.PixelGetException.argtypes = [ctypes.c_void_p,
                                          ctypes.POINTER(ctypes.c_int)]
    library.PixelGetException.restype = ctypes.c_char_p

    library.PixelClearException.argtypes = [ctypes.c_void_p]

    library.IsPixelWandSimilar.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                           ctypes.c_double]

    library.PixelGetMagickColor.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    library.PixelSetMagickColor.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    library.PixelSetColor.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    library.PixelGetColorAsString.argtypes = [ctypes.c_void_p]
    library.PixelGetColorAsString.restype = ctypes.c_char_p

    library.PixelGetRed.argtypes = [ctypes.c_void_p]
    library.PixelGetRed.restype = ctypes.c_double

    library.PixelGetGreen.argtypes = [ctypes.c_void_p]
    library.PixelGetGreen.restype = ctypes.c_double

    library.PixelGetBlue.argtypes = [ctypes.c_void_p]
    library.PixelGetBlue.restype = ctypes.c_double

    library.PixelGetAlpha.argtypes = [ctypes.c_void_p]
    library.PixelGetAlpha.restype = ctypes.c_double

    library.MagickGetQuantumRange.argtypes = [ctypes.POINTER(ctypes.c_size_t)]

    library.MagickSetIteratorIndex.argtypes = [ctypes.c_void_p,
                                               ctypes.c_ssize_t]

    library.MagickGetImageType.argtypes = [ctypes.c_void_p]
    
    library.MagickSetImageType.argtypes = [ctypes.c_void_p, ctypes.c_int]

    library.MagickEvaluateImageChannel.argtypes = [ctypes.c_void_p,
                                                   ctypes.c_int,
                                                   ctypes.c_int,
                                                   ctypes.c_double]

    library.MagickCompositeImage.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                             ctypes.c_int, ctypes.c_ssize_t,
                                             ctypes.c_ssize_t]

    library.MagickGetImageCompressionQuality.argtypes = [ctypes.c_void_p]
    library.MagickGetImageCompressionQuality.restype = ctypes.c_ssize_t

    library.MagickSetImageCompressionQuality.argtypes = [ctypes.c_void_p,
                                                         ctypes.c_ssize_t]

    library.MagickStripImage.argtypes = [ctypes.c_void_p]

    library.MagickTrimImage.argtypes = [ctypes.c_void_p]

    libmagick.GetMagickVersion.argtypes = [ctypes.POINTER(ctypes.c_size_t)]
    libmagick.GetMagickVersion.restype = ctypes.c_char_p

    libmagick.GetMagickReleaseDate.argtypes = []
    libmagick.GetMagickReleaseDate.restype = ctypes.c_char_p
except AttributeError:
    raise ImportError('MagickWand shared library not found or incompatible')

#: (:class:`ctypes.CDLL`) The C standard library.
libc = None

if platform.system() == 'Windows':
    libc = ctypes.CDLL(ctypes.util.find_msvcrt())
else:
    if platform.system() == 'Darwin':
        libc = ctypes.cdll.LoadLibrary('libc.dylib')
    elif platform.system() == 'FreeBSD':
        libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
    else:
        libc = ctypes.cdll.LoadLibrary('libc.so.6')
    libc.fdopen.argtypes = [ctypes.c_int, ctypes.c_char_p]
    libc.fdopen.restype = ctypes.c_void_p

libc.free.argtypes = [ctypes.c_void_p]

