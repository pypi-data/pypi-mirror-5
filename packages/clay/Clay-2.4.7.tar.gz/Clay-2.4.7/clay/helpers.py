# -*- coding: utf-8 -*-
from datetime import datetime
import errno
import io
import os
import re
import shutil


def to_unicode(s, encoding='utf8', errors='strict'):
    return s.decode(encoding, errors)


def read_content(path, **kwargs):
    kwargs.setdefault('mode', 'rt')
    with io.open(path, **kwargs) as f:
        return f.read()


def make_dirs(*lpath):
    path = os.path.join(*lpath)
    try:
        os.makedirs(path)
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return path


def create_file(path, content, encoding='utf8'):
    if not isinstance(content, unicode):
        content = unicode(content, encoding)
    with io.open(path, 'w+t', encoding=encoding) as f:
        f.write(content)


def copy_if_updated(path_in, path_out):
    if os.path.exists(path_out):
        newt = os.path.getmtime(path_in)
        currt = os.path.getmtime(path_out)
        if currt >= newt:
            return
    shutil.copy2(path_in, path_out)


def get_updated_datetime(path):
    ut = os.path.getmtime(path)
    return datetime.fromtimestamp(ut)


def sort_paths_dirs_last(paths):
    def dirs_last(a, b):
        return cmp(a[0].count('/'), b[0].count('/')) or cmp(a[0], b[0])

    return sorted(paths, cmp=dirs_last)

