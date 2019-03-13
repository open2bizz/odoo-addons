# -*- coding: utf-8 -*-
# Copyright Open2bizz (http://www.open2bizz.nl)
# See LICENSE file for full copyright and license details.
{
    'name': 'Default Data',
    'version': '0.1',
    'category': 'Tools',
    'description': """Framework for adding default data in Odoo.""",
    'author': 'Open2bizz',
    'website': 'http://open2bizz.nl/',
    'license': "LGPL-3",
    'depends': ['base'],
    'data':[
        'security/groups.xml',
        'security/ir_model_access.xml',
        'views/view_default_data.xml',
    ],
    'installable': True,
}
