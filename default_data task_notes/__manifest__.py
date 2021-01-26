# -*- coding: utf-8 -*-
# Copyright Open2bizz (http://www.open2bizz.nl)
# See LICENSE file for full copyright and license details.
{
    'name': 'Default Data for notes',
    'version': '0.1',
    'category': 'Tools',
    'description': """default data for notes in Odoo.""",
    'author': 'Open2bizz',
    'website': 'http://open2bizz.nl/',
    'license': "LGPL-3",
    'depends': ['note','project_task_notes'],
    'data':[
        'views/view_notes.xml',
        'data/record_rule.xml',
    ],
    'installable': True,
}
