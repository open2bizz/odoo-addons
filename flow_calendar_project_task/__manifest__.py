# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

{
    'name': 'Flow Calendar Project Task',
    'summary': 'Plan your Project Tasks in the Odoo Calendar.',
    'description': 'Plan your Project Tasks in the Odoo Calendar.',
    'version': '1.2',
    'author': 'Nova Code',
    'website': 'https://www.novacode.nl',
    'license': 'OPL-1',
    'price': 30,
    'currency': 'EUR',
    'category': 'Project',
    'depends': [
        'flow_calendar',
        'project',
    ],
    'data': [
        'views/flow_calendar_project_task_views.xml',
    ],
    'qweb': [
        'static/src/xml/flow_calendar_project_task.xml'
    ],
    'images': [
        'static/description/flow_calendar_project_task_banner.jpg',
    ]
}
