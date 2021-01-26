# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

{
    'name': 'Flow Calendar',
    'summary': 'Flow Calendar API',
    'version': '1.0',
    'author': 'Nova Code',
    'website': 'https://www.novacode.nl',
    'license': 'OPL-1',
    'price': 19.00,
    'currency': 'EUR',
    'category': 'Extra Tools',
    'depends': [
        'calendar',
    ],
    'data': [
        'views/flow_calendar_templates.xml',
        'views/flow_calendar_views.xml'
    ],
    'qweb': [
        'static/src/xml/flow_calendar.xml'
    ],
    'images': [
        'static/description/cover_banner.png',
    ],
    'description': """
Flow Calendar API
=================

A tiny API, which enables integration of Odoo Apps (planning) with the Odoo Calendar.

Useful modules
--------------
- Flow Calendar Project Task: https://apps.odoo.com/apps/modules/10.0/flow_calendar_project_task
- Flow Calendar Project Issue: https://apps.odoo.com/apps/modules/10.0/flow_calendar_project_issue
"""

}
