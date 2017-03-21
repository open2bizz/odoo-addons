# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2016 open2bizz (open2bizz.nl).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp

class TODO_TEST(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg

def TODO(func):
    """unittest test method decorator that ignores
       exceptions raised by test.
   
    Used to annotate test methods for code that may
    not be written yet.  Ignores failures in the
    annotated test method; fails if the text
    unexpectedly succeeds.
    """

    def wrapper(*args, **kw):
        try:
            func(*args, **kw)
            succeeded = True
        except:
            succeeded = False

        if openerp.tools.config.get('orbeon_tests_todo', False):
            try:
                assert succeeded is False, \
                    "%s" % func.__name__
            except AssertionError, e:
                raise TODO_TEST(e)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
