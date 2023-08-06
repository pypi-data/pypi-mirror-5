#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' A cross-platform multi-screen shot module in pure python using ctypes.

    This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.
    If you find problems, please submit bug reports/patches via the
    GitHub issue tracker (https://github.com/BoboTiG/python-mss/issues).

    Note: please keep this module compatible to Python 2.6.

    Still needed:
    * support for additional systems

    Many thanks to all those who helped (in no particular order):

      Oros, Eownis

    History:

    <see Git checkin messages for history>

    0.0.1 - first release
    0.0.2 - add support for python 3 on Windows and GNU/Linux
    0.0.3 - MSSImage: remove PNG filters
          - MSSImage: remove 'ext' argument, using only PNG
          - MSSImage: do not overwrite existing image files
          - MSSImage: few optimizations into png()
          - MSSLinux: few optimizations into get_pixels()
    0.0.4 - MSSLinux: use of memoization => huge time/operations gains
    0.0.5 - MSSWindows: few optimizations into _arrange()
          - MSSImage: code simplified

    You can always get the latest version of this module at:

            https://raw.github.com/BoboTiG/python-mss/master/mss.py

    If that URL should fail, try contacting the author.
'''

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

__version__ = '0.0.5'
__author__ = "Mickaël 'Tiger-222' Schoentgen"
__copyright__ = '''
    Copyright (c) 2013, Mickaël 'Tiger-222' Schoentgen

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee or royalty is hereby
    granted, provided that the above copyright notice appear in all copies
    and that both that copyright notice and this permission notice appear
    in supporting documentation or portions thereof, including
    modifications, that you make.
'''
__all__ = ['MSSImage', 'MSSLinux', 'MSSMac', 'MSSWindows']


from ctypes.util import find_library
from struct import pack
from os.path import isfile
from platform import system
import sys
import zlib

if system() == 'Darwin':
    from Quartz import *
    from LaunchServices import kUTTypePNG

elif system() == 'Linux':
    from os import environ
    from os.path import expanduser
    import xml.etree.ElementTree as ET
    from ctypes import byref, cast, cdll
    from ctypes import (
        c_char_p, c_int, c_int32, c_uint, c_uint32,
        c_ulong, c_void_p, POINTER, Structure
    )

    class Display(Structure):
        pass

    class XWindowAttributes(Structure):
        _fields_ = [
            ('x',                     c_int32),
            ('y',                     c_int32),
            ('width',                 c_int32),
            ('height',                c_int32),
            ('border_width',          c_int32),
            ('depth',                 c_int32),
            ('visual',                c_ulong),
            ('root',                  c_ulong),
            ('class',                 c_int32),
            ('bit_gravity',           c_int32),
            ('win_gravity',           c_int32),
            ('backing_store',         c_int32),
            ('backing_planes',        c_ulong),
            ('backing_pixel',         c_ulong),
            ('save_under',            c_int32),
            ('colourmap',             c_ulong),
            ('mapinstalled',          c_uint32),
            ('map_state',             c_uint32),
            ('all_event_masks',       c_ulong),
            ('your_event_mask',       c_ulong),
            ('do_not_propagate_mask', c_ulong),
            ('override_redirect',     c_int32),
            ('screen',                c_ulong)
        ]

    class XImage(Structure):
        _fields_ = [
            ('width'            , c_int),
            ('height'           , c_int),
            ('xoffset'          , c_int),
            ('format'           , c_int),
            ('data'             , c_char_p),
            ('byte_order'       , c_int),
            ('bitmap_unit'      , c_int),
            ('bitmap_bit_order' , c_int),
            ('bitmap_pad'       , c_int),
            ('depth'            , c_int),
            ('bytes_per_line'   , c_int),
            ('bits_per_pixel'   , c_int),
            ('red_mask'         , c_ulong),
            ('green_mask'       , c_ulong),
            ('blue_mask'        , c_ulong)
        ]

    def b(x):
        return pack(b'<B', x)

elif system() == 'Windows':
    from ctypes import (
        byref, memset, pointer, sizeof, windll,
        c_void_p as LPRECT,
        c_void_p as LPVOID,
        create_string_buffer,
        Structure,
        POINTER,
        WINFUNCTYPE,
    )
    from ctypes.wintypes import (
        BOOL, DOUBLE, DWORD, HANDLE, HBITMAP, HDC, HGDIOBJ,
        HWND, INT, LPARAM, LONG,RECT,SHORT, UINT, WORD
    )

    class BITMAPINFOHEADER(Structure):
        _fields_ = [
            ('biSize',          DWORD),
            ('biWidth',         LONG),
            ('biHeight',        LONG),
            ('biPlanes',        WORD),
            ('biBitCount',      WORD),
            ('biCompression',   DWORD),
            ('biSizeImage',     DWORD),
            ('biXPelsPerMeter', LONG),
            ('biYPelsPerMeter', LONG),
            ('biClrUsed',       DWORD),
            ('biClrImportant',  DWORD)
        ]

    class BITMAPINFO(Structure):
        _fields_ = [
            ('bmiHeader', BITMAPINFOHEADER),
            ('bmiColors', DWORD * 3)
        ]

    if sys.version < '3':
        def b(x):
            return x
    else:
        def b(x):
            return pack(b'<B', x)



# ----------------------------------------------------------------------
# --- [ C'est parti mon kiki ! ] ---------------------------------------
# ----------------------------------------------------------------------

class MSS(object):
    ''' This class will be overloaded by a system specific one.
        It checkes if there is a class available for the current system.
        Raise an exception if no one found.
    '''

    DEBUG = False

    def __init__(self, debug=False):
        ''' Global vars and class overload. '''

        self.DEBUG = debug
        self.monitors = []
        self.oneshot = False

        self.init()

    def debug(self, method='', scalar=None, value=None):
        ''' Simple debug output. '''

        if self.DEBUG:
            if scalar is None:
                print(':: ' + method + '()')
            else:
                print(method + '()', scalar, type(value).__name__, value)

    def save(self, output='mss', oneshot=False):
        ''' For each monitor, grab a screen shot and save it to a file.

            Parameters:
             - output - string - the output filename without extension
             - oneshot - boolean - grab only one screen shot of all monitors

            This is a generator which returns created files:
                'output-1.png',
                'output-2.png',
                ...,
                'output-NN.png'
                or
                'output-full.png'
        '''

        self.debug('save')

        self.oneshot = oneshot
        self.monitors = self.enum_display_monitors() or []

        self.debug('save', 'oneshot', self.oneshot)

        if len(self.monitors) < 1:
            raise ValueError('MSS: no monitor found.')

        # Monitors screen shots!
        i = 1
        for monitor in self.monitors:
            self.debug('save', 'monitor', monitor)

            if self.oneshot:
                filename = output + '-full'
            else:
                filename = output + '-' + str(i)
                i += 1
            filename += '.png'

            if not isfile(filename):
                pixels = self.get_pixels(monitor)
                if pixels is None:
                    raise ValueError('MSS: no data to process.')

                if hasattr(self, 'save_'):
                    img_out = self.save_(output=filename)
                else:
                    img = MSSImage(pixels, monitor[b'width'], monitor[b'height'])
                    img_out = img.dump(filename)
                self.debug('save', 'img_out', img_out)
                if img_out:
                    yield img_out
            else:
                yield filename + ' (already exists)'

    def enum_display_monitors(self):
        ''' Get positions of all monitors.

            If self.oneshot is True, this function has to return a dict
            with dimensions of all monitors at the same time.
            If the monitor has rotation, you have to deal with inside this method.

            Must returns a dict with a minima:
            {
                'left':   the x-coordinate of the upper-left corner,
                'top':    the y-coordinate of the upper-left corner,
                'width':  the width,
                'height': the height
            }
        '''
        pass

    def get_pixels(self, monitor_infos):
        ''' Retrieve screen pixels for a given monitor.

            monitor_infos should contain at least:
            {
                'left':   the x-coordinate of the upper-left corner,
                'top':    the y-coordinate of the upper-left corner,
                'width':  the width,
                'heigth': the height
            }

            Returns a dict with pixels.
        '''
        pass


class MSSMac(MSS):
    ''' Mutli-screen shot implementation for Mac OSX.
        It uses intensively the Quartz.
    '''

    def init(self):
        ''' Mac OSX initialisations '''
        self.debug('init')
        pass

    def enum_display_monitors(self):
        ''' Get positions of one or more monitors.
            Returns a dict with minimal requirements (see MSS class).
        '''

        self.debug('enum_display_monitors')

        results = []
        if self.oneshot:
            rect = CGRectInfinite
            results.append({
                b'left'  : int(rect.origin.x),
                b'top'   : int(rect.origin.y),
                b'width' : int(rect.size.width),
                b'height': int(rect.size.height)
            })
        else:
            max_displays = 32  # Peut-être augmenté, si besoin...
            rotations = {0.0: 'normal', 90.0: 'right', -90.0: 'left'}
            res, ids, count = CGGetActiveDisplayList(max_displays, None, None)
            for display in ids:
                rect = CGRectStandardize(CGDisplayBounds(display))
                left, top = rect.origin.x, rect.origin.y
                width, height = rect.size.width, rect.size.height
                rot = CGDisplayRotation(display)
                rotation = rotations[rot]
                if rotation in ['left', 'right']:
                    width, height = height, width
                results.append({
                    b'left'    : int(left),
                    b'top'     : int(top),
                    b'width'   : int(width),
                    b'height'  : int(height),
                    b'rotation': rotation
                })
        return results

    def get_pixels(self, monitor):
        ''' Retreive all pixels from a monitor. Pixels have to be RGB.
        '''

        self.debug('get_pixels')

        width, height = monitor[b'width'], monitor[b'height']
        left, top = monitor[b'left'], monitor[b'top']
        rect = CGRect((left, top), (width, height))
        self.image = CGWindowListCreateImage(
                    rect, kCGWindowListOptionOnScreenOnly,
                    kCGNullWindowID, kCGWindowImageDefault)
        return 1

    def save_(self, output):
        ''' Special method to not use MSSImage class. '''

        self.debug('save_')

        dpi = 72
        url = NSURL.fileURLWithPath_(output)
        dest = CGImageDestinationCreateWithURL(url, kUTTypePNG, 1, None)
        properties = {
            kCGImagePropertyDPIWidth: dpi,
            kCGImagePropertyDPIHeight: dpi,
        }
        CGImageDestinationAddImage(dest, self.image, properties)
        if not CGImageDestinationFinalize(dest):
            output = None
        return output


class MSSLinux(MSS):
    ''' Mutli-screen shot implementation for GNU/Linux.
        It uses intensively the Xlib.
    '''

    def __del__(self):
        ''' Disconnect from X server '''

        self.debug('__del__')

        if self.display:
            self.XCloseDisplay(self.display)

    def init(self):
        ''' GNU/Linux initialisations '''

        self.debug('init')

        x11 = find_library('X11')
        if x11 is None:
            raise OSError('MSSLinux: no X11 library found.')
        else:
            xlib = cdll.LoadLibrary(x11)

        self.debug('init', 'xlib', xlib)

        self.XOpenDisplay = xlib.XOpenDisplay
        self.XDefaultScreen = xlib.XDefaultScreen
        self.XDefaultRootWindow = xlib.XDefaultRootWindow
        self.XGetWindowAttributes = xlib.XGetWindowAttributes
        self.XAllPlanes = xlib.XAllPlanes
        self.XGetImage = xlib.XGetImage
        self.XGetPixel = xlib.XGetPixel
        self.XFree = xlib.XFree
        self.XCloseDisplay = xlib.XCloseDisplay

        self._set_argtypes()
        self._set_restypes()

        display = None
        self.display = None
        try:
            if sys.version > '3':
                display = bytes(environ['DISPLAY'], 'utf-8')
            else:
                display = environ['DISPLAY']
        except KeyError:
            err = 'MSSLinux: $DISPLAY not set. Stopping to prevent segfault.'
            raise ValueError(err)
        self.debug('init', '$DISPLAY', display)

        # At this point, if there is no running server, it could end on
        # a segmentation fault. And we cannot catch it.
        self.display = self.XOpenDisplay(display)
        self.debug('init', 'display', self.display)
        self.screen = self.XDefaultScreen(self.display)
        self.debug('init', 'screen', self.screen)
        self.root = self.XDefaultRootWindow(self.display, self.screen)
        self.debug('init', 'root', self.root)

    def _set_argtypes(self):
        ''' Functions arguments '''

        self.debug('_set_argtypes')

        self.XOpenDisplay.argtypes = [c_char_p]
        self.XDefaultScreen.argtypes = [POINTER(Display)]
        self.XDefaultRootWindow.argtypes = [POINTER(Display), c_int]
        self.XGetWindowAttributes.argtypes = [POINTER(Display),
            POINTER(XWindowAttributes), POINTER(XWindowAttributes)]
        self.XAllPlanes.argtypes = []
        self.XGetImage.argtypes = [POINTER(Display), POINTER(Display),
            c_int, c_int, c_uint, c_uint, c_ulong, c_int]
        self.XGetPixel.argtypes = [POINTER(XImage), c_int, c_int]
        self.XFree.argtypes = [POINTER(XImage)]
        self.XCloseDisplay.argtypes = [POINTER(Display)]

    def _set_restypes(self):
        ''' Functions return type '''

        self.debug('_set_restypes')

        self.XOpenDisplay.restype = POINTER(Display)
        self.XDefaultScreen.restype = c_int
        self.XDefaultRootWindow.restype = POINTER(XWindowAttributes)
        self.XGetWindowAttributes.restype = c_int
        self.XAllPlanes.restype = c_ulong
        self.XGetImage.restype = POINTER(XImage)
        self.XGetPixel.restype = c_ulong
        self.XFree.restype = c_void_p
        self.XCloseDisplay.restype = c_void_p

    def enum_display_monitors(self):
        ''' Get positions of one or more monitors.
            Returns a dict with minimal requirements (see MSS class).
        '''

        self.debug('enum_display_monitors')

        results = []
        if self.oneshot:
            gwa = XWindowAttributes()
            self.XGetWindowAttributes(self.display, self.root, byref(gwa))
            results.append({
                b'left'  : int(gwa.x),
                b'top'   : int(gwa.y),
                b'width' : int(gwa.width),
                b'height': int(gwa.height)
            })
        else:
            # It is a little more complicated, we have to guess all stuff
            # from ~/.config/monitors.xml, if present.
            monitors = expanduser('~/.config/monitors.xml')
            if not isfile(monitors):
                self.debug('ERROR', 'MSSLinux: enum_display_monitors() failed (no monitors.xml).')
                self.oneshot = True
                return self.enum_display_monitors()
            tree = ET.parse(monitors)
            root = tree.getroot()
            config = root.findall('configuration')[-1]
            conf = []
            for output in config.findall('output'):
                name = output.get('name')
                if name != 'default':
                    x = output.find('x')
                    y = output.find('y')
                    width = output.find('width')
                    height = output.find('height')
                    rotation = output.find('rotation')
                    if None not in [x, y, width, height] and name not in conf:
                        conf.append(name)
                        if rotation.text in ['left', 'right']:
                            width, height = height, width
                        results.append({
                            b'left'    : int(x.text),
                            b'top'     : int(y.text),
                            b'width'   : int(width.text),
                            b'height'  : int(height.text),
                            b'rotation': rotation.text
                        })
        return results

    def get_pixels(self, monitor):
        ''' Retreive all pixels from a monitor. Pixels have to be RGB.
        '''

        self.debug('get_pixels')

        width, height = monitor[b'width'], monitor[b'height']
        left, top = monitor[b'left'], monitor[b'top']
        ZPixmap = 2

        allplanes = self.XAllPlanes()
        self.debug('get_pixels', 'allplanes', allplanes)

        # Fix for XGetImage: expected LP_Display instance instead of LP_XWindowAttributes
        root = cast(self.root, POINTER(Display))

        image = self.XGetImage(self.display, root, left, top, width,
            height, allplanes, ZPixmap)
        if image is None:
            raise ValueError('MSSLinux: XGetImage() failed.')

        def pix(pixel, _resultats={}):
            ''' Apply shifts to a pixel to get the RGB values.
                This method uses of memoization.
            '''
            if not pixel in _resultats:
                _resultats[pixel] = b((pixel & 16711680) >> 16) + b((pixel & 65280) >> 8) + b(pixel & 255)
            return _resultats[pixel]

        get_pix = self.XGetPixel
        pixels = [pix(get_pix(image, x, y)) for y in range(height) for x in range(width)]

        self.XFree(image)
        return b''.join(pixels)


class MSSWindows(MSS):
    ''' Mutli-screen shot implementation for Microsoft Windows. '''

    def init(self):
        ''' Windows initialisations '''

        self.debug('init')

        self.GetSystemMetrics = windll.user32.GetSystemMetrics
        self.EnumDisplayMonitors = windll.user32.EnumDisplayMonitors
        self.GetWindowDC = windll.user32.GetWindowDC
        self.CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
        self.CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
        self.SelectObject = windll.gdi32.SelectObject
        self.BitBlt = windll.gdi32.BitBlt
        self.GetDIBits = windll.gdi32.GetDIBits
        self.DeleteObject = windll.gdi32.DeleteObject

        self._set_argtypes()
        self._set_restypes()

    def _set_argtypes(self):
        ''' Functions arguments '''

        self.debug('_set_argtypes')

        self.MONITORENUMPROC = WINFUNCTYPE(INT, DWORD, DWORD,
            POINTER(RECT), DOUBLE)
        self.GetSystemMetrics.argtypes = [INT]
        self.EnumDisplayMonitors.argtypes = [HDC, LPRECT,
            self.MONITORENUMPROC, LPARAM]
        self.GetWindowDC.argtypes = [HWND]
        self.CreateCompatibleDC.argtypes = [HDC]
        self.CreateCompatibleBitmap.argtypes = [HDC, INT, INT]
        self.SelectObject.argtypes = [HDC, HGDIOBJ]
        self.BitBlt.argtypes = [HDC, INT, INT, INT, INT, HDC, INT, INT, DWORD]
        self.DeleteObject.argtypes = [HGDIOBJ]
        self.GetDIBits.argtypes = [HDC, HBITMAP, UINT, UINT, LPVOID,
            POINTER(BITMAPINFO), UINT]

    def _set_restypes(self):
        ''' Functions return type '''

        self.debug('_set_restypes')

        self.GetSystemMetrics.restypes = INT
        self.EnumDisplayMonitors.restypes = BOOL
        self.GetWindowDC.restypes = HDC
        self.CreateCompatibleDC.restypes = HDC
        self.CreateCompatibleBitmap.restypes = HBITMAP
        self.SelectObject.restypes = HGDIOBJ
        self.BitBlt.restypes =  BOOL
        self.GetDIBits.restypes = INT
        self.DeleteObject.restypes = BOOL

    def enum_display_monitors(self):
        ''' Get positions of one or more monitors.
            Returns a dict with minimal requirements (see MSS class).
        '''

        self.debug('enum_display_monitors')

        def _callback(monitor, dc, rect, data):
            rct = rect.contents
            results.append({
                b'left'  : int(rct.left),
                b'top'   : int(rct.top),
                b'width' : int(rct.right - rct.left),
                b'height': int(rct.bottom -rct.top)
            })
            return 1

        results = []
        if self.oneshot:
            SM_XVIRTUALSCREEN = 76
            SM_YVIRTUALSCREEN = 77
            SM_CXVIRTUALSCREEN = 78
            SM_CYVIRTUALSCREEN = 79
            left = self.GetSystemMetrics(SM_XVIRTUALSCREEN)
            right = self.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            top = self.GetSystemMetrics(SM_YVIRTUALSCREEN)
            bottom = self.GetSystemMetrics(SM_CYVIRTUALSCREEN)
            results.append({
                b'left'  : int(left),
                b'top'   : int(top),
                b'width' : int(right - left),
                b'height': int(bottom - top)
            })
        else:
            callback = self.MONITORENUMPROC(_callback)
            self.EnumDisplayMonitors(0, 0, callback, 0)
        return results

    def get_pixels(self, monitor):
        ''' Retreive all pixels from a monitor. Pixels have to be RGB. '''

        self.debug('get_pixels')

        width, height = monitor[b'width'], monitor[b'height']
        left, top = monitor[b'left'], monitor[b'top']
        good_width = (width * 3 + 3) & -4
        SRCCOPY = 0xCC0020
        DIB_RGB_COLORS = 0

        srcdc = self.GetWindowDC(0)
        memdc = self.CreateCompatibleDC(srcdc)
        bmp = self.CreateCompatibleBitmap(srcdc, width, height)
        self.SelectObject(memdc, bmp)
        self.BitBlt(memdc, 0, 0, width, height, srcdc, left, top, SRCCOPY)
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = width
        bmi.bmiHeader.biHeight = height
        bmi.bmiHeader.biBitCount = 24
        bmi.bmiHeader.biPlanes = 1
        buffer_len = height * good_width
        pixels = create_string_buffer(buffer_len)
        bits = self.GetDIBits(memdc, bmp, 0, height, byref(pixels),
            pointer(bmi), DIB_RGB_COLORS)

        self.debug('get_pixels', 'srcdc', srcdc)
        self.debug('get_pixels', 'memdc', memdc)
        self.debug('get_pixels', 'bmp', bmp)
        self.debug('get_pixels', 'buffer_len', buffer_len)
        self.debug('get_pixels', 'bits', bits)
        self.debug('get_pixels', 'len(pixels.raw)', len(pixels.raw))

        # Clean up
        self.DeleteObject(srcdc)
        self.DeleteObject(memdc)
        self.DeleteObject(bmp)

        if bits != height or len(pixels.raw) != buffer_len:
            raise ValueError('MSSWindows: GetDIBits() failed.')

        # Note that the origin of the returned image is in the
        # bottom-left corner, 32-bit aligned. And it is BGR.
        # Need to "arrange" that.
        return self._arrange(pixels.raw, good_width, height)

    def _arrange(self, data, width, height):
        ''' Reorganises data when the origin of the image is in the
            bottom-left corner and converts BGR triple to RGB. '''

        self.debug('_arrange')

        total = width * height
        scanlines = [b'0'] * total
        for y in range(height):
            off = width * (y + 1)
            offset = total - off
            for x in range(0, width - 2, 3):
                scanlines[off+x:off+x+3] = b(data[offset+x+2]), b(data[offset+x+1]), b(data[offset+x])
        return b''.join(scanlines)


class MSSImage(object):
    ''' This is a class to save data (raw pixels) to a picture file.
    '''

    def __init__(self, data=None, width=1, height=1):
        if data is None:
            raise ValueError('MSSImage: no data to process.')
        elif width < 1 or height < 1:
            raise ValueError('MSSImage: width or height must be positive.')

        self.data = data
        self.width = int(width)
        self.height = int(height)

    def dump(self, output):
        ''' Dump data to the image file.
            Pure python PNG implementation.
            Image represented as RGB tuples, no interlacing.
            http://inaps.org/journal/comment-fonctionne-le-png
        '''

        with open(output, 'wb') as fileh:
            to_take = (self.width * 3 + 3) & -4
            padding = 0 if to_take % 8 == 0 else (to_take % 8) // 2
            height, data = self.height, self.data
            scanlines = [b''.join([b'0', data[to_take*y:to_take*y+to_take-padding]]) for y in range(height)]

            magic = pack(b'>8B', 137, 80, 78, 71, 13, 10, 26, 10)

            # Header: size, marker, data, CRC32
            ihdr = [b'', b'IHDR', b'', b'']
            ihdr[2] = pack(b'>2I5B', self.width, self.height, 8, 2, 0, 0, 0)
            ihdr[3] = pack(b'>I', zlib.crc32(b''.join(ihdr[1:3])) & 0xffffffff)
            ihdr[0] = pack(b'>I', len(ihdr[2]))

            # Data: size, marker, data, CRC32
            idat = [b'', b'IDAT', b'', b'']
            idat[2] = zlib.compress(b''.join(scanlines), 9)
            idat[3] = pack(b'>I', zlib.crc32(b''.join(idat[1:3])) & 0xffffffff)
            idat[0] = pack(b'>I', len(idat[2]))

            # Footer: size, marker, None, CRC32
            iend = [b'', b'IEND', b'', b'']
            iend[3] = pack(b'>I', zlib.crc32(iend[1]) & 0xffffffff)
            iend[0] = pack(b'>I', len(iend[2]))

            fileh.write(magic + b''.join(ihdr) + b''.join(idat) + b''.join(iend))
            return output
        return None


if __name__ == '__main__':

    systems = {
        'Darwin' : MSSMac,
        'Linux'  : MSSLinux,
        'Windows': MSSWindows
    }
    try:
        MSS = systems[system()]
    except KeyError:
        err = 'System "{0}" not implemented.'.format(system())
        raise NotImplementedError(err)

    try:
        mss = MSS(debug=False)

        # One screen shot per monitor
        for filename in mss.save():
            print('File "{0}" created.'.format(filename))

        # A shot to grab them all :)
        for filename in mss.save(oneshot=True):
            print('File "{0}" created.'.format(filename))
    except Exception as ex:
        print(ex)
        raise
