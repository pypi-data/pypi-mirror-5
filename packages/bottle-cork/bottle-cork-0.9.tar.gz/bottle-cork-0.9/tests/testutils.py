# Cork - Authentication module for tyyhe Bottle web framework
# Copyright (C) 2013 Federico Ceratto and others, see AUTHORS file.
# Released under GPLv3+ license, see LICENSE.txt
#
# Unit testing - utility functions.
#
import bottle
import os
import shutil
import sys
import tempfile


def pick_temp_directory():
    """Select a temporary directory for the test files.
    Set the tmproot global variable.
    """
    if os.environ.get('TRAVIS', False):
        return tempfile.mkdtemp()

    if sys.platform == 'linux2':
        # In-memory filesystem allows faster testing.
        return "/dev/shm"

    return tempfile.mkdtemp()


def purge_temp_directory(test_dir):
    """Remove the test directory"""
    assert test_dir
    shutil.rmtree(test_dir)

def assert_is_redirect(e, path):
    """Check if an HTTPResponse is a redirect.

    :param path: relative path without leading slash.
    :type path: str
    """
    assert isinstance(e, bottle.HTTPResponse), "Incorrect exception type passed to assert_is_redirect"
    assert e.status_code == 302, "HTTPResponse status should be 302 but is '%s'" % e.status
    redir_location = e.headers['Location'].rsplit('/', 1)[1]
    assert redir_location == path, "Redirected to %s instead of %s" % (redir_location, path)



