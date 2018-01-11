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

{
    "name": "Orbeon Project Runner Form Copy",
    "summary": 'Copy the XML from a orbeon runner form that was previously added from the same type of form builder and same partner_id',
    "description": 'Copy Runner Forms',
    "version": "0.1",
    "author": "Open2bizz",
    "website": "http://www.open2bizz.nl",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ['orbeon','project'],
    "data": [
        "views/orbeon_runner.xml",
        "views/copy_runner_form_wizard.xml"
    ],
    "application": True,
    "installable": True,
}
