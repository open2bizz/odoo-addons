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
    "name": "Orbeon XML API",
    'summary': 'Orbeon XML API',
    'description': """
Orbeon XML API
===============

Use Orbeon (Runner) Forms XML, like it's a simple Python object.  This
module extends the Orbeon Runner model-object, with a special
attribute *o_xml*, which is the "Pythonic" object API on the Runner
its XML.

Syntax examples:
- runner.o_xml.section_general.firstname: Returns a Python string e.g. "Bob"
- runner.o_xml.section_general.birthdate: Returns a Python Date object.
- runner.o_xml.section_general.avatar_pic: Returns Python base64decoded data object.

""",
    "version": "0.1",
    "author": "Open2bizz",
    "website": "http://www.open2bizz.nl",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "orbeon",
    ],
    # 'external_dependencies': {
    #     'python': ['orbeon_xml_api'],
    # },
    'data': [
        'views/report_runner_test.xml'
    ],
    "application": False,
    "installable": True,
}
