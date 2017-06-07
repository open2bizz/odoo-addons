# -*- encoding: utf-8 -*-
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
    'name': 'Default Data',
    'version': '0.1',
    'category': 'Tools',
    'description': """Framework for adding default data in Odoo.""",
    'author': 'Open2bizz',
    'website': 'http://open2bizz.nl/',
    'depends': ['base'],
    'data':[
        'security/groups.xml',
        'security/ir_model_access.xml',
        'views/view_default_data.xml',
    ],            
    'installable': True,
}