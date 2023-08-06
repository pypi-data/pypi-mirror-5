"""
Various common functions

Copyright 2011 Red Hat, Inc.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__autor__ = """
jzupka@redhat.com (Jiri Zupka)
"""
import logging
import time
import re
import os
import hashlib
import tempfile
import subprocess
from lnst.Common.ExecCmd import exec_cmd

def die_when_parent_die():
    try:
        import ctypes
        from ctypes.util import find_library
    except:
        logging.error("Failed to load ctype library.")
        raise
    libc = ctypes.CDLL(find_library("c"))
    PR_SET_PDEATHSIG = 1; TERM = 15
    libc.prctl(PR_SET_PDEATHSIG, TERM)


def wait_for(func, timeout, first=0.0, step=1.0, text=None):
    """
    If func() evaluates to True before timeout expires, return the
    value of func(). Otherwise return None.

    @brief: Wait until func() evaluates to True.

    @param timeout: Timeout in seconds
    @param first: Time to sleep before first attempt
    @param steps: Time to sleep between attempts in seconds
    @param text: Text to print while waiting, for debug purposes
    """
    start_time = time.time()
    end_time = time.time() + timeout

    time.sleep(first)
    while time.time() < end_time:
        if text:
            logging.debug("%s (%f secs)", text, (time.time() - start_time))

        output = func()
        if output:
            return output

        time.sleep(step)

    logging.debug("Timeout elapsed")
    return None

def kmod_in_use(modulename, tries = 1):
    tries -= 1
    ret = False
    mod_file = "/proc/modules"
    handle = open(mod_file, "r")
    for line in handle:
        match = re.match(r'^(\S+)\s\d+\s(\d+).*$', line)
        if not match or not match.groups()[0] in re.split('\s+', modulename):
            continue
        if int(match.groups()[1]) != 0:
            ret = True
        break
    handle.close()
    if (ret and tries):
        return kmod_in_use(modulename, tries)
    return ret

def int_it(val):
    try:
        num = int(val)
    except ValueError:
        num = 0
    return num

def bool_it(val):
    if isinstance(val, str):
        if re.match("^\s*(?i)(true)", val):
            return True
        elif re.match("^\s*(?i)(false)", val):
            return False
    return True if int_it(val) else False

def md5sum(file_path, block_size=2**20):
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()

def create_tar_archive(input_path, target_path, compression=False):
    if compression:
        args = "cfj"
    else:
        args = "cf"

    if os.path.isdir(target_path):
        target_path += "/%s.tar.bz" % os.path.basename(input_file.rstrip("/"))

    input_path = input_path.rstrip("/")
    input_file = os.path.basename(input_path)
    parent = os.path.dirname(input_path)

    exec_cmd("cd \"%s\" && tar %s \"%s\" \"%s\"" % \
                (parent, args, target_path, input_file))

    return target_path

def dir_md5sum(dir_path):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.close()

    tar_filepath = create_tar_archive(dir_path, tmp_file.name)
    md5_digest = md5sum(tar_filepath)

    os.unlink(tar_filepath)

    return md5_digest

def has_changed_since(filepath, threshold):
    if os.path.isfile(filepath):
        return _is_newer_than(filepath, threshold)

    for root, dirs, files in os.walk(directory):
        for f in files:
            if _is_newer_than(f, threshold):
                return False

        for d in dirs:
            if _is_newer_than(d, threshold):
                return False

    return True

def _is_newer_than(f, threshold):
    stat = os.stat(f)
    return stat.st_mtime > threshold

def check_process_running(process_name):
    try:
        proc = subprocess.check_call(["pgrep", process_name],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False
