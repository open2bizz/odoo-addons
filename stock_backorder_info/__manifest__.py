# Copyright 2013-2020 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

{
    'name': 'Backorder info on delivery',
    'summary': 'Adds backorder information on delivery',
    'version': '16.0.1.0.0',
    'category': 'Stock',
    'website': 'https://www.open2bizz.nl/',
    'author': 'Open2Bizz',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'stock',
        'sale',
    ],
    'data': [
        'reports/delivery.xml',
    ]
}
