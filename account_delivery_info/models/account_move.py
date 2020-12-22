# Copyright 2013-2020 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    delivery_ids = fields.May2many(string="Deliveries linked",
        comodel_name='stock.picking',
        compute='_compute_deliveries',
        )

    @api.depends('invoice_line_ids')
    def _compute_deliveries(self):
        for rec in self:
            rec.delivery_ids = []
            for line in rec.invoice_line_ids:
                for sale_line in line.sale_line_ids:
                    for stock_move in sale_line.move_ids:
                        rec.update({'delivery_ids': stock_move.picking_id})
            if not rec.delivery_ids:
               rec.delivery_ids = False

