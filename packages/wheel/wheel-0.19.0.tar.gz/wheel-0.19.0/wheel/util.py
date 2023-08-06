"""Utility functions."""

import sys
import os
import base64
import json
import hashlib

from .pep425tags import (get_abbr_impl, get_impl_ver, get_supported,
                         get_supported as generate_supported) # b/c

try:
    from pkg_resources import Distribution, Requirement, parse_version
    have_pkgresources = True
except ImportError:
    from distutils.version import LooseVersion as parse_version
    have_pkgresources = False

__all__ = ['urlsafe_b64encode', 'urlsafe_b64decode', 'utf8', 'to_json',
           'from_json', 'generate_supported', 'get_abbr_impl', 'get_impl_ver',
           'parse_version', 'matches_requirement',
           'have_pkgresources']


def urlsafe_b64encode(data):
    """urlsafe_b64encode without padding"""
    return base64.urlsafe_b64encode(data).rstrip(binary('='))


def urlsafe_b64decode(data):
    """urlsafe_b64decode without padding"""
    pad = b'=' * (4 - (len(data) & 3))
    return base64.urlsafe_b64decode(data + pad)


def to_json(o):
    '''Convert given data to JSON.'''
    return json.dumps(o, sort_keys=True)


def from_json(j):
    '''Decode a JSON payload.'''
    return json.loads(j)

def open_for_csv(name, mode):
    if sys.version_info[0] < 3:
        nl = {}
        bin = 'b'
    else:
        nl = { 'newline': '' }
        bin = ''
    return open(name, mode + bin, **nl)

try:
    unicode

    def utf8(data):
        '''Utf-8 encode data.'''
        if isinstance(data, unicode):
            return data.encode('utf-8')
        return data
except NameError:
    def utf8(data):
        '''Utf-8 encode data.'''
        if isinstance(data, str):
            return data.encode('utf-8')
        return data


try:
    # For encoding ascii back and forth between bytestrings, as is repeatedly
    # necessary in JSON-based crypto under Python 3
    unicode
    def native(s):
        return s
    def binary(s):
        if isinstance(s, unicode):
            return s.encode('ascii')
        return s
except NameError:
    def native(s):
        if isinstance(s, bytes):
            return s.decode('ascii')
        return s
    def binary(s):
        if isinstance(s, str):
            return s.encode('ascii')

class HashingFile(object):
    def __init__(self, fd, hashtype='sha256'):
        self.fd = fd
        self.hashtype = hashtype
        self.hash = hashlib.new(hashtype)
        self.length = 0
    def write(self, data):
        self.hash.update(data)
        self.length += len(data)
        self.fd.write(data)
    def close(self):
        self.fd.close()
    def digest(self):
        if self.hashtype == 'md5':
            return self.hash.hexdigest()
        digest = self.hash.digest()
        return self.hashtype + '=' + native(urlsafe_b64encode(digest))

if sys.platform == 'win32':
    import ctypes.wintypes
    # CSIDL_APPDATA for reference - not used here for compatibility with
    # dirspec, which uses LOCAL_APPDATA and COMMON_APPDATA in that order
    csidl = dict(CSIDL_APPDATA=26, CSIDL_LOCAL_APPDATA=28,
            CSIDL_COMMON_APPDATA=35)
    def get_path(name):
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, csidl[name], 0, SHGFP_TYPE_CURRENT, buf)
        return buf.value

    def save_config_path(*resource):
        appdata = get_path("CSIDL_LOCAL_APPDATA")
        path = os.path.join(appdata, *resource)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path
    def load_config_paths(*resource):
        ids = ["CSIDL_LOCAL_APPDATA", "CSIDL_COMMON_APPDATA"]
        for id in ids:
            base = get_path(id)
            path = os.path.join(base, *resource)
            if os.path.exists(path):
                yield path
else:
    def save_config_path(*resource):
        import dirspec.basedir
        return dirspec.basedir.save_config_path(*resource)
    def load_config_paths(*resource):
        import dirspec.basedir
        return dirspec.basedir.load_config_paths(*resource)

if have_pkgresources:
    def matches_requirement(req, wheels):
        """List of wheels matching a requirement.

        :param req: The requirement to satisfy
        :param wheels: List of wheels to search.
        """
        # If we don't have pkg_resources, raise an error
        req = Requirement.parse(req)

        selected =  []
        for wf in wheels:
            f = wf.parsed_filename
            dist = Distribution(project_name=f.group("name"), version=f.group("ver"))
            if dist in req:
                selected.append(wf)
        return selected
else:
    def matches_requirement(req, wheels):
        raise RuntimeError("Cannot use requirements without pkg_resources")
