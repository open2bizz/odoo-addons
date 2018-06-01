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
    "name": "Qweb reports for Orbeon Forms",
    'summary': 'Attach Qweb reports to Orbeon Forms, which becomes printable from the Runner Form',
    "version": "0.1",
    "author": "Open2bizz",
    "website": "http://www.open2bizz.nl",
    "license": "AGPL-3",
    "category": "orbeon",
    "depends": ["orbeon", "orbeon_project"],
    "data": [
        "views/ir_actions_report_xml.xml",
        "views/orbeon_builder.xml",
        "views/orbeon_runner.xml",
        "views/qweb_report_chooser.xml",
        "views/orbeon_builder_report_xml.xml",
        "security/ir_model_access.xml",
    ],
    "application": False,
    "installable": True,
}
