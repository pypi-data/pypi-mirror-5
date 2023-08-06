#
# This file is part of gruvi. Gruvi is free software available under the
# terms of the MIT license. See the file "LICENSE" that was provided
# together with this source file for the licensing terms.
#
# Copyright (c) 2012-2013 the gruvi authors. See the file "AUTHORS" for a
# complete list.

from __future__ import absolute_import, print_function

import os
import sys
import shutil
import tempfile
import logging
import subprocess

import pyuv
import gruvi


def assert_raises(exc, func, *args, **kwargs):
    """Like nose.tools.assert_raises but returns the exception."""
    try:
        func(*args, **kwargs)
    except Exception as e:
        if not isinstance(e, exc):
            print(e)
        assert isinstance(e, exc)
        return e
    raise AssertionError('no exception raised')


def create_ssl_certificate(fname):
    """Create a new SSL private key and self-signed certificate, and store
    them both in the file *fname*."""
    if os.access(fname, os.R_OK):
        return
    try:
        openssl = subprocess.Popen(['openssl', 'req', '-new',
                        '-newkey', 'rsa:1024', '-x509', '-subj', '/CN=test/',
                        '-days', '365', '-nodes', '-batch',
                        '-out', fname, '-keyout', fname],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        sys.stderr.write('Error: openssl not found. SSL tests disabled.\n')
        return
    stdout, stderr = openssl.communicate()
    if openssl.returncode:
        sys.stderr.write('Error: key generation failed\n')
        sys.stderr.write('openssl stdout: {0}\n'.format(stdout))
        sys.stderr.write('openssl stderr: {0}\n'.format(stderr))


def setup():
    """Package-level setup."""
    dirname, fname = os.path.split(__file__)
    certname = os.path.join(dirname, 'server.pem')
    create_ssl_certificate(certname)


def setup_logger(logger):
    """Configure a logger to output to stdout."""
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    template = '%(levelname)s %(name)s: %(message)s'
    handler.setFormatter(logging.Formatter(template))
    logger.addHandler(handler)


_close_objects = []

def closign(obj):
    """Call obj.close() in test teardown."""
    _close_objects.append(obj)

def close_all():
    """Close all objects referenced by ``closing()``."""
    for obj in _close_objects:
        try:
            obj.close()
        except IOError:
            pass
    del _close_objects[:]


class UnitTest(object):
    """Base class for unit tests."""

    @classmethod
    def setup_class(cls):
        cls.__tmpdir = tempfile.mkdtemp('gruvi-test')
        logger = logging.getLogger('gruvi')
        if not logger.handlers:
            setup_logger(logger)
        testdir = os.path.abspath(os.path.split(__file__)[0])
        os.chdir(testdir)
        if os.access('server.pem', os.R_OK):
            cls.certname = 'server.pem'
        else:
            cls.certname = None

    @classmethod
    def teardown_class(cls):
        # Some paranoia checks to make me feel better when calling
        # shutil.rmtree()..
        assert '/..' not in cls.__tmpdir and '\\..' not in cls.__tmpdir
        if '/tmp/' not in cls.__tmpdir and '\\temp\\' not in cls.__tmpdir:
            return
        try:
            shutil.rmtree(cls.__tmpdir)
        except OSError:
            # On Windows a WindowsError is raised when files are
            # still open (WindowsError inherits from OSError).
            pass
        cls.__tmpdir = None

    @classmethod
    def tempname(cls, name):
        return os.path.join(cls.__tmpdir, name)

    def teardown(self):
        # Close all handlers so that we don't run out of file handlers when
        # running the entire suite. Also this prevents stray handles from
        # changing the behavior of a subsequent Hub.switch().
        hub = gruvi.get_hub()
        def close_handle(h):
            try:
                h.close()
            except pyuv.error.UVError:
                pass
        hub.loop.walk(close_handle)
