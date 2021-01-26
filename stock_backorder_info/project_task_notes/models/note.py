# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html2plaintext

class Note(models.Model):
    _inherit = 'note.note'
    
    @api.onchange('task_id')
    def onchange_task(self):
        for rec in self:
            if rec.task_id.project_id:
                rec.project_id = rec.task_id.project_id.id
    
    project_id = fields.Many2one(
        'project.project',
        'Project',
    )
    task_id = fields.Many2one(
        'project.task',
        'Task',
    )
    is_task = fields.Boolean(
        'Is Task?',
    )
    is_project = fields.Boolean(
        'Is Project?',
    )
