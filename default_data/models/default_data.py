# -*- coding: utf-8 -*-
# Copyright Open2bizz (http://www.open2bizz.nl)
# See LICENSE file for full copyright and license details.

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError

FIELD_TYPES = [
    ('html', 'HTML'),
    ('char', 'Char'),
    ('float', 'Float'),
    ('boolean', 'Boolean'),
    ('integer', 'Integer'),
    ('text', 'Text'),
    ('binary', 'Binary'),
    ('date', 'Date'),
    ('datetime', 'DateTime'),
]


class DefaultData(models.Model):
    _name = 'default.data'

    name = fields.Char(
        string = 'Name'
    )
    model_id = fields.Many2one(
        comodel_name = 'ir.model',
        string = 'Model',
        required = True
    )
    model = fields.Char(
        string = 'Model Name',
        related = 'model_id.model',
        store=True,
        readonly=True
    )
    field_id = fields.Many2one(
        comodel_name = 'ir.model.fields',
        string = 'Field',
        required = True,
        domain = "[('model_id.model', '=', model)]"
    )
    field = fields.Char(
        string = 'Field Name',
        related = 'field_id.name',
        store=True,
        readonly=True
    )
    type = fields.Selection(
        selection = FIELD_TYPES,
        string = 'Type',
        required=True,
    )
    value_char = fields.Char(
        string = 'Value'
    )
    value_text = fields.Text(
        string = 'Value'
    )
    value_html = fields.Html(
        string = 'Value'
    )
    value_integer = fields.Integer(
        string = 'Value'
    )
    value_float = fields.Float(
        string = 'Value'
    )
    value_boolean = fields.Boolean(
        string = 'Value'
    )
    value_binary = fields.Binary(
        string = 'Value'
    )
    value_date = fields.Date(
        string = 'Value'
    )
    value_datetime = fields.Datetime(
        string = 'Value'
    )
    value_many2one_id = fields.Integer(
        string = 'Record ID'
    )
    repr_value = fields.Text(
        compute='_compute_repr_value',
        string='Value'
    )

    @api.depends(
        'value_char', 'value_text', 'value_html', 'value_integer', 'value_float',\
        'value_boolean', 'value_binary', 'value_date', 'value_datetime')
    def _compute_repr_value(self):
        for r in self:
            default_data = r.get_default_data()
            if r.type == 'many2one':
                res = self.env[r.field_id.relation].browse(r.value_many2one_id)
                if hasattr(res, 'name'):
                    r.repr_value = res.name
                else:
                    r.repr_value = default_data
            else:
                r.repr_value = default_data

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.field_id = False
        
    @api.onchange('field_id')
    def onchange_fields_id(self):
        if self.field_id:
            if [field_type for field_type in FIELD_TYPES if field_type[0] == self.field_id.ttype]:
                self.type = self.field_id.ttype
            else:
                raise ValidationError(_('The type (\"%s\") of this field is not supported' % self.field_id.ttype))

    @api.multi
    def get_default_data(self):
        if self.type == 'html':
            return self.value_html
        elif self.type == 'char':
            return self.value_char
        elif self.type == 'float':
            return self.value_float
        elif self.type == 'boolean':
            return self.value_boolean
        elif self.type == 'integer':
            return self.value_integer
        elif self.type == 'text':
            return self.value_text
        elif self.type == 'binary':
            return self.value_binary
        elif self.type == 'date':
            return self.value_date
        elif  self.type == 'datetime':
            return self.value_datetime
        elif self.type == 'many2one':
            value = self.env[self.field_id.relation].browse(self.value_many2one_id)
            if value:
                return value.id
            else:
                raise ValidationError(_('Not able to find the default data record'))
        
    @api.multi
    def get_update_default_data(self, old_data):
        new_data = self.get_default_data()
        if old_data == new_data:
            return {
                'update' : False
            }
        else:
            return {    
                'update' : True,
                'data' : new_data
            }
