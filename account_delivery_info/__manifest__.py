# Copyright 2013-2020 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

{
    'name': 'Delivery info on Invoice',
    'summary': 'Adds delivery information on invoice',
    'version': '13.0.1.0.0',
    'category': 'Accounting',
    'website': 'https://www.open2bizz.nl/',
    'author': 'Open2Bizz',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'account',
        'sale',
    ],
    'data': [
        'views/invoice_views.xml',
    ]
}
