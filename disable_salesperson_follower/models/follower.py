# Copyright 2013-2020 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, get_lang
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['invoice_user_id'] = self.env.uid
        invoice_vals['user_id'] = self.env.uid
        return invoice_vals

class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountInvoice, self).create(vals_list)
        for vals in vals_list:
            if vals.get('invoice_user_id'):
                partner = self.env['res.partner'].search([('user_ids','in',vals.get('invoice_user_id'))])
                follow_record = self.env['mail.followers'].search([('res_id','=',res.id),('res_model','=','account.move'),('partner_id','=',partner[0].id)])
                follow_record.unlink()    
            if vals.get('user_id'):
                partner = self.env['res.partner'].search([('user_ids','in',vals.get('user_id'))])
                follow_record = self.env['mail.followers'].search([('res_id','=',res.id),('res_model','=','account.move'),('partner_id','=',partner[0].id)])
                follow_record.unlink()    
        res.invoice_user_id = self.env.uid
        return res
