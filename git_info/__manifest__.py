# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2017 open2bizz (open2bizz.nl).
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

{
    "name": "Git Info",
    "summary": 'Git info about the Odoo installation',
    "description": 'Adds Git info about the Odoo installation to the Settings Dashboard.',
    "version": "0.1",
    "author": "Open2bizz",
    "website": "http://www.open2bizz.nl",
    "license": "AGPL-3",
    "category": "Tools",
    "depends": ['web'],
    "data": [],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    "application": False,
    "installable": False,
}
