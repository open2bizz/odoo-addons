# Copyright 2013-2020 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

{
    'name': 'account_invoice_bank_reports',
    'summary': 'Add Banks (optional) to report footer',
    'version': '13.0.1.0.0',
    'category': 'Accounting',
    'website': 'https://www.open2bizz.nl/',
    'author': 'Open2Bizz',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'report/footer.xml',
        'views/account_journal.xml',
    ]
}
