# -*- coding: utf-8 -*-
{
    'name': "immobilier",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Moore Senegal",
    'website': "http://www.moore.sn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sales_team','contacts','crm','sale'],

    # always loaded
    'data': [
        'security/library_security.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        #'security/securite.xml',
        'demo/demo.xml',
        'views/data_email_crm.xml',
        'views/views.xml',
        'views/biens_view.xml',
        'views/contact.xml',
        'views/crm.xml',
        'views/data.xml',
        'views/cron_data.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
