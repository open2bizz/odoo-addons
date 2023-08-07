# -*- encoding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2017 open2bizz (open2bizz.nl).
#    See licence file
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError
import logging
_logger = logging.getLogger(__name__)

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    default_solution_template_id = fields.Many2one(
        comodel_name = 'mail.template',
        string = 'Default Template'
    )
    default_stage_closed_id = fields.Many2one(
        comodel_name = 'helpdesk.stage',
        string = 'Default Stage initial Closed',
        domain = "[('model_id', '=', 'helpdesk.ticket')]"
    )

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    solution = fields.Html(
        string = 'Solution'
    )
    default_solution = fields.Many2one(
        comodel_name = 'default.data',
        string = 'Default Solution',
        domain = "[('model', '=', 'helpdesk.ticket'), ('field', '=', 'solution')]"
    )
    
    @api.onchange("default_solution")
    def onchange_default_solution(self):
        if self.default_solution:
            update_data = self.default_solution.get_update_default_data(self.solution)
            if update_data['update']:
                self.solution = update_data['data']

    def action_create_default_data(self):
        value = self.solution
        name_new = self.name
        model_id = self.env['ir.model'].search([('model','=','helpdesk.ticket')])
        field_id = self.env['ir.model.fields'].search([('model','=','helpdesk.ticket'),('name','=','solution')])
        default_data = self.env['default.data'].create({'model_id': model_id.id,'name': name_new ,'field_id': field_id.id ,'value_html': self.solution, 'type': 'html'})
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'default.data',
                'target': 'current',
                'res_id': default_data.id,
                'domain': [('model','=','helpdesk.ticket')],
            } 

    def action_ticket_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template = self.team_id.default_solution_template_id
        lang = self.env.context.get('lang')
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'helpdesk.ticket',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        if self.team_id.default_stage_closed_id:
            self.stage_id = self.team_id.default_stage_closed_id.id
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
