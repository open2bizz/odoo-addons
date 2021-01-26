# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Project and Task Notes",
    'currency': 'EUR',
    'license': 'Other proprietary',
        'price': 15.0,

    'summary': """This module allow project users to keep notes for project and tasks.""",
    'description': """
This module allow project users to keep notes for project and tasks.
Project Notes
Project and Task Notes
Task Notes
Project Task Notes
Notes for Project
Add Notes on Project
Add Notes on Task
Add notes on Project / Task
Print Project Notes
Print Task Notes
user notes
notes
project notes
task notes
project task notes
todo list
todo tasks
project user
project manager
project notice
user manual
Project and Task Notes

This module allow project users to keep notes for project and tasks.
Menus:

Project/Notes
Project/Notes/Project Notes
Project/Notes/Task Notes


    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'version': '1.0',
    'category' : 'Project',
    'depends': ['project','note'],
    'live_test_url': 'https://youtu.be/3zaiKzSS-aI',
    'data':[
        'views/note_view.xml',
        'views/report_noteview.xml',
        'views/project_view.xml',
        'views/task_view.xml'
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
