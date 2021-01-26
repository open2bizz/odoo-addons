# -*- coding: utf-8 -*-
# Copyright Open2bizz (http://www.open2bizz.nl)
# See LICENSE file for full copyright and license details.

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError
import logging
_logger = logging.getLogger(__name__)

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
    _description = 'Default Data'
    _order = 'model_id asc, name asc'
    
    name = fields.Char(
        string = 'Name',
        help = "General name to quick select the default data on a field/model"
    )
    model_id = fields.Many2one(
        comodel_name = 'ir.model',
        help = "The model on which the data is used",
        string = 'Model',
        ondelete = 'cascade',
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
        help = "The fiels on which the data is used to set as template",
        string = 'Field',
        required = True,
        ondelete = 'cascade',
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
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_text = fields.Text(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_html = fields.Html(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_integer = fields.Integer(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_float = fields.Float(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_boolean = fields.Boolean(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_binary = fields.Binary(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_date = fields.Date(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )
    value_datetime = fields.Datetime(
        string = 'Value',
        help = "The actual default value which will be used as a template",
    )


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

    def get_default_data(self):
        for record in self:
            if  record.type == 'html':
                return record.value_html
            elif  record.type == 'char':
                return record.value_char
            elif  record.type == 'float':
                return record.value_float
            elif  record.type == 'boolean':
                return record.value_boolean
            elif  record.type == 'integer':
                return record.value_integer
            elif  record.type == 'text':
                return record.value_text
            elif  record.type == 'binary':
                return record.value_binary
            elif  record.type == 'date':
                return record.value_date
            elif  record.type == 'datetime':
                return record.value_datetime
            else:
                raise ValidationError(_('Not able to find the default data record'))
        
    def get_update_default_data(self, old_data):
        for record in self:
            new_data = record.get_default_data()
            if old_data == new_data:
                return {
                    'update' : False
                }
            else:
                return {    
                    'update' : True,
                    'data' : new_data
                }


