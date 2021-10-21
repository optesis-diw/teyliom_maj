# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Time Off Leave Project Manager / Department Head Approval',
    'version': '1.1.1',
    'price': 109.0,
    'depends': [
        'hr_holidays',
    ],
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Human Resources',
    'summary':  """HR Holidays / Time Off Leave - Project Manager / Department Head Approval""",
    'description': """
leave approve
leave approval
holiday approval
holiday approve
leave request
holiday request
tripple approval
tripple approve
double approve leave
odoo leave
hr leave approval
holidays approval
holiday approve
time off approve
leave approve
leave approval
    """,
    
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://youtu.be/8hbuc3uHC94',
    'data': [
        'security/security.xml',
        'views/hr_employee_view.xml',
        'views/time_off_request_views.xml',
        'views/time_off_types_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
