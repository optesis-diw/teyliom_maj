# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar software trading llc (<https://www.inteslar.com>).
#
###################################################################################
{
    'name': "Leave request from Website (portal)",
    'version': '13.0',
    'category': 'HR',
    'price': 600.00,
    'currency': 'EUR',
    'maintainer': 'inteslar',
    'website': "https://www.inteslar.com",
    'license': 'OPL-1',
    'author': 'inteslar',
    'summary': 'Leave request from Website (portal)',
    'images': ['static/images/main_screenshot.png'],
    'depends': ['resource', 'hr', 'web','website','calendar','hr_holidays','portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_leave_security.xml',
        'views/portal_leave_templates.xml',
        'views/portal_leave_view.xml',
    ],
    'installable': True,
    'application': True,
}