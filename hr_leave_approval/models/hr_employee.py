# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    custom_project_manager_id = fields.Many2one(
        'res.users',
        string="Project Manager/Department Head",
        help="Use for Leave Approval as a Project Manager/Department Head of Employee"
    )
