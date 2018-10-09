#!usr/bin/python
# -*- coding: utf-8 -*-

from . import bmagym

@bmagym.route('/')
def index():
    return 'success'
