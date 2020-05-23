from odoo import api, fields, models, _

class Project(models.Model):
     _name = "project.project"
     _inherit = ['project.project', 'mail.thread', 'mail.activity.mixin']

