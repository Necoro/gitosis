# -*- coding: utf-8 -*-

import errno

import pytest
from gitosis import util


def test_catch():
    def foo():
        raise OSError(errno.EEXIST)

    with pytest.raises(OSError):
        util.catch(foo, [errno.ENOENT])()
