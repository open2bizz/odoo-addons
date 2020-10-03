# -*- encoding: utf-8 -*-
##############################################################################
#    open2bizz
#    Copyright (C) 2020 open2bizz (open2bizz.nl).
#    See licence file
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError
import logging

class Note(models.Model):

    _inherit = 'note.note'
    
    default_data_id = fields.Many2one(
        comodel_name = 'default.data',
        string = 'Default Memo',
        domain = "[('model', '=', 'note.note'), ('field', '=', 'memo')]"
    )
    
    @api.onchange("default_data_id")
    def onchange_default_data_id(self):
        if self.default_data_id:
            update_data = self.default_data_id.get_update_default_data(self.memo)
            if update_data['update']:
                self.memo = update_data['data']

    def action_create_default_data(self):
        value = self.memo
        name_new = self.memo[:10]
        model_id = self.env['ir.model'].search([('model','=','note.note')])
        field_id = self.env['ir.model.fields'].search([('model','=','note.note'),('name','=','memo')])
        default_data = self.env['default.data'].create({'model_id': model_id.id,'name': name_new ,'field_id': field_id.id ,'value_html': self.memo, 'type': 'html'})
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'default.data',
                'target': 'current',
                'res_id': default_data.id,
                'domain': [('model','=','note.note')],
            } 

