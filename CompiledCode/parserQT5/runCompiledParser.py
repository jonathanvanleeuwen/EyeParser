# -*- coding: utf-8 -*-
"""
Created on Fri Feb 02 15:02:08 2018

@author: User1
"""

import marshal

s = open('EyeParser.pyc', 'rb')
s.seek(8)  # go past first eight bytes
code_obj = marshal.load(s)

exec(code_obj)