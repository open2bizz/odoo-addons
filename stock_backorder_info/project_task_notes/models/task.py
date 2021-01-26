# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    def _compute_notes_count(self):
        for task in self:
            task.notes_count = len(task.notes_ids)
            
    notes_ids = fields.One2many(
        'note.note', 
        'task_id', 
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes"
    )
    
    @api.multi
    def view_notes(self):
        for rec in self:
            res = self.env.ref('project_task_notes.action_task_note_note_smart')
            res = res.read()[0]
            res['domain'] = str([('task_id','in',rec.ids)])
        return res
