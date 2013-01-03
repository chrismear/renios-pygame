"""Config for iOS w/ frameworks"""

import os, sys, string
from glob import glob
from distutils.sysconfig import get_python_inc

class Dependency:
    libext = '.a'
    def __init__(self, name, checkhead, checklib, libs):
        self.name = name
        self.inc_dir = None
        self.lib_dir = None
        self.libs = libs
        self.found = 0
        self.checklib = checklib + self.libext
        self.checkhead = checkhead
        self.cflags = ''

    def configure(self, incdirs, libdirs):
        incname = self.checkhead
        libnames = self.checklib, self.name.lower()
        for dir in incdirs:
            path = os.path.join(dir, incname)
            if os.path.isfile(path):
                self.inc_dir = dir
                break
        for dir in libdirs:
            for name in libnames:
                path = os.path.join(dir, name)
                if os.path.isfile(path):
                    self.lib_dir = dir
                    break
        if self.lib_dir and self.inc_dir:
            print (self.name + '        '[len(self.name):] + ': found')
            self.found = 1
        else:
            print (self.name + '        '[len(self.name):] + ': not found')

class FrameworkDependency(Dependency):
    def configure(self, incdirs, libdirs):
        # Only search for frameworks found in the iOS SDK
        BASE_DIRS = [os.environ['SDKROOT'] + '/System/']
        for n in BASE_DIRS:
            n += 'Library/Frameworks/'
            # iOS frameworks store libs directly inside the .framework directory.
            fmwk = n + self.libs + '.framework/'
            if os.path.isfile(fmwk + self.libs):
                print ('Framework ' + self.libs + ' found')
                self.found = 1
                self.inc_dir = fmwk + 'Headers'
                self.cflags = (
                    '-Xlinker "-framework" -Xlinker "' + self.libs + '"' +
                    ' -Xlinker "-F' + n + '"')
                self.origlib = self.libs
                self.libs = ''
                return
        print ('Framework ' + self.libs + ' not found')


class DependencyPython:
    def __init__(self, name, module, header):
        self.name = name
        self.lib_dir = ''
        self.inc_dir = ''
        self.libs = []
        self.cflags = ''
        self.found = 0
        self.ver = '0'
        self.module = module
        self.header = header

    def configure(self, incdirs, libdirs):
        self.found = 1
        if self.module:
            try:
                self.ver = __import__(self.module).__version__
            except ImportError:
                self.found = 0
        if self.found and self.header:
            fullpath = os.path.join(get_python_inc(0), self.header)
            if not os.path.isfile(fullpath):
                found = 0
            else:
                self.inc_dir = os.path.split(fullpath)[0]
        if self.found:
            print (self.name + '        '[len(self.name):] + ': found', self.ver)
        else:
            print (self.name + '        '[len(self.name):] + ': not found')

DEPS = [
    Dependency('SDL', 'SDL.h', 'libSDL', ['SDL']),
    Dependency('FONT', 'SDL_ttf.h', 'libSDL2_ttf', ['SDL2_ttf']),
    Dependency('IMAGE', 'SDL_image.h', 'libSDL2_image', ['SDL2_image']),
    Dependency('MIXER', 'SDL_mixer.h', 'libSDL_mixer', ['SDL_mixer']),
    Dependency('SMPEG', 'smpeg.h', 'libsmpeg', ['smpeg']),
    Dependency('PNG', 'png.h', 'libpng', ['png']),
    Dependency('JPEG', 'jpeglib.h', 'libjpeg', ['jpeg']),
    Dependency('SCRAP', '', '', []),
    Dependency('PORTMIDI', 'portmidi.h', 'libportmidi', ['portmidi']),
    FrameworkDependency('PORTTIME', 'CoreMIDI.h', 'CoreMIDI', 'CoreMIDI'),
]


def main():
    global DEPS

    print ('Hunting dependencies...')

    # Look for dependencies among the ReniOS dependency build products,
    # and in the iOS SDK.
    incdirs = [
               os.environ['BUILDROOT'] + '/include',
               os.environ['BUILDROOT'] + '/include/SDL',
               os.environ['SDKROOT'] + '/usr/include'
              ]
    print incdirs
    libdirs = [
               os.environ['BUILDROOT'] + '/lib',
               os.environ['SDKROOT'] + '/usr/lib'
              ]
    print libdirs

    newconfig = []
    for d in DEPS:
        d.configure(incdirs, libdirs)
    DEPS[0].cflags = '-Ddarwin ' + DEPS[0].cflags
    return DEPS


if __name__ == '__main__':
    print ("""This is the configuration subscript for iOS.
             Please run "config.py" for full configuration.""")
