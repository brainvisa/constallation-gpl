#!/usr/bin/env python

from __future__ import print_function
import urllib2
from optparse import OptionParser
import sys
import tempfile
import os
import zipfile
import socket


class Context(object):

    '''simulate Axon context for code reusability'''

    def write(self, *args):
        nargs = [str(arg) for arg in args]
        print(' '.join(nargs))

    def progress(self, progress, num):
        sys.stdout.write('\r%02d ' % int(float(progress * 100) / num) + '%')
        sys.stdout.flush()

    def temporary(self, filetype):
        tfile = tempfile.mkstemp(suffix='.zip')
        filename = tfile[1]
        os.close(tfile[0])
        return filename

download_url = 'ftp://ftp.cea.fr/pub/dsv/anatomist/data'
atlasversion = '1.0'

parser = OptionParser(
    'get and unzip Constellation atlas in a given directory')
parser.add_option('-o', '--output',
                  help='output directory (should be something/share/constellation-<version>')
parser.add_option('-i', '--input',
                  help='input URL, default: %s' % download_url)
parser.add_option('-v', '--version',
                  help='atlas version, default: %s' % atlasversion)
parser.add_option('-t', '--timeout', type='float',
                  help='ftp timeout (in seconds), default: 15', default=15)
parser.add_option('-s', '--silent', action='store_true',
                  help='do not raise an error when the timeout fails')

options, args = parser.parse_args(sys.argv)
if options.output is None:
    print('option -o is mandatory', file=sys.stderr)
    parser.parse_args(['-h'])
if options.input is not None:
    download_url = options.input
if options.version is not None:
    atlasversion = options.version
timeout = options.timeout
silent = options.silent
print('timeout:', timeout)

context = Context()

destdir = options.output
if not os.path.exists(destdir):
    os.makedirs(destdir)
context.write('install in dir:', destdir)

if download_url.startswith('ftp://'):
    local_files = False
else:
    local_files = True

files = []
files.append('constellation_atlas_hcp_200s-' + atlasversion + '.zip')

# taken from spam_install_model process in morphologist-gpl

pnum = len(files) * 100 + 10
pgs = 0
for fname in files:
    context.write('downloading', fname, '...')
    context.progress(pgs, pnum)
    if local_files:
        tzf = os.path.join(download_url, fname)
        context.write('file %s is local' % tzf)
    else:
        try:
            ftp = urllib2.urlopen(download_url + '/' + fname, timeout=timeout)
        except (urllib2.URLError, socket.timeout):
            if silent:
                print('warning: operation timed out')
                sys.exit(0)
            raise
        tzf = context.temporary('zip file')
        f = open(tzf, 'wb')
        fsize = long(ftp.headers.get('content-length'))
        chunksize = 100000
        fread = 0
        while fread < fsize:
            pg = fread * 80 / fsize
            context.progress(pgs + pg, pnum)
            f.write(ftp.read(chunksize))
            fread += chunksize
        context.write('download done')
        f.close()
    pgs += 80
    context.progress(pgs, pnum)
    context.write('installing', fname, '...')
    f = open(tzf, 'rb')
    zf = zipfile.ZipFile(f, 'r')
    # extract zip files one by one
    # extractall() is not an option since on Mac at least it tries to
    # re-make directories even if they exist
    namelist = zf.namelist()
    fnlist = []
    for name in namelist:
        dname = os.path.join(destdir, name)
        if os.path.exists(dname):
            if os.path.isdir(dname):
                pass  # skip existing dirs
            else:  # existing file: remove it first
                os.unlink(dname)
                fnlist.append(name)
        else:
            fnlist.append(name)
    del namelist
    zf.extractall(destdir, fnlist)
    zf.close()
    zf = None
    f.close()
    f = None
    pgs += 20
    if not local_files:
        os.unlink(tzf)
context.progress(pgs, pnum)
context.progress(100, 100)
print()
