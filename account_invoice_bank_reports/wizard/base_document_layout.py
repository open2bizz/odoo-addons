from odoo import models,fields


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    company_registry = fields.Char(related='company_id.company_registry', readonly=True)
    bank_journal_ids = fields.One2many(related='company_id.bank_journal_ids', readonly=True)