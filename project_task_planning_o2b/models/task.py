# -*- coding: utf-8 -*-
##############################################################################
#    open2bizz
#    Copyright (C) 2020 open2bizz (www.open2bizz.tech).
##############################################################################
from odoo import api, fields, models
import odoo.exceptions

class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'
    
    new_stage_id = fields.Many2one('project.task.type' , 'New Stage')
    prev_stage_id = fields.Many2one('project.task.type' , 'Prev Stage')
    is_planned = fields.Boolean(string='Is Planned')

    @api.onchange('tag_ids')
    def _onchange_tag_ids(self):
        tag_this_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_this_week')
        tag_next_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_next_week')
        tag_other_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_other_week')
        for record in self:
            if tag_this_week in record.tag_ids or tag_next_week in record.tag_ids or tag_other_week in record.tag_ids:
	            record.is_planned = 1
            else:
	            record.is_planned = 0
        
    # todo: This is not working when onchange of mail template is called..
        
    @api.onchange('stage_id')
    def _onchange_stage(self):
        self.prev_stage_id = self._origin.stage_id
        self.new_stage_id = self.stage_id
        if self.new_stage_id.sequence < self.prev_stage_id.sequence:
            self.color = 6
        else:
            self.color = 0

    def set_plan_this_week(self):
        tag_this_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_this_week')
        tag_next_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_next_week')
        tag_other_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_other_week')
        if not tag_this_week in self.tag_ids:
	        self.write({'tag_ids': [(4,tag_this_week.id)]})
        if tag_next_week in self.tag_ids:
	        self.write({'tag_ids': [(3,tag_next_week.id)]})
        if tag_other_week in self.tag_ids:
	        self.write({'tag_ids': [(3,tag_other_week.id)]})
        self._onchange_tag_ids()

    def set_plan_next_week(self):
        tag_this_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_this_week')
        tag_next_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_next_week')
        tag_other_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_other_week')
        if not tag_next_week in self.tag_ids:
	        self.write({'tag_ids': [(4,tag_next_week.id)]})
        if tag_this_week in self.tag_ids:
	        self.write({'tag_ids': [(3,tag_this_week.id)]})
        if tag_other_week in self.tag_ids:
	        self.write({'tag_ids': [(3,tag_other_week.id)]})
        self._onchange_tag_ids()

    def set_plan_other_week(self):
        tag_this_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_this_week')
        tag_next_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_next_week')
        tag_other_week = self.env['ir.model.data'].get_object('project_task_planning_o2b','tag_other_week')
        if not tag_other_week in self.tag_ids:
	        self.write({'tag_ids': [(4,tag_other_week.id)]})
        if tag_this_week in self.tag_ids:
	        self.write({'tag_ids': [(3,tag_this_week.id)]})
        if tag_next_week in self.tag_ids:
	        self.write({'tag_ids': [(3,tag_next_week.id)]})
        self._onchange_tag_ids()
            
class ProjectTask(models.Model):
    _inherit = 'project.tags'
    
    plan_type = fields.Selection([('this_week','This Week'),('next_week','Next Week'),('other_week','After next Week')],'Plan Type')

