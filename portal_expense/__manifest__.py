# -*- coding: utf-8 -*-
##########################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar software trading llc (<https://www.inteslar.com>).
#
##########################################################################################
{
    'name': "Expense request from Website(portal)",
    'version': '14.0',
    'category': 'HR',
    'price': 600.00,
    'currency': 'EUR',
    'maintainer': 'inteslar',
    'website': "https://www.inteslar.com",
    'license': 'OPL-1',
    'summary': 'Expense request from Website(portal) By Inteslar',
    'author': 'inteslar',
    'summary': 'Expense request from Website(portal) By Inteslar',
    'images': ['static/images/main_screenshot.png'],
    'depends': ['hr', 'web','website','calendar','hr_expense','portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_expense_security.xml',
        'views/portal_expense_templates.xml',
    ],
    'installable': True,
    'application': True,
}