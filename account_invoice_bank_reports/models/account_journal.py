# Copyright 2013-2020 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = "account.journal"

    add_to_footer = fields.Boolean(string='Add Bank to footer templates')
    
