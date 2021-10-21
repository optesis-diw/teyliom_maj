# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class HolidaysType(models.Model):
    _inherit = 'hr.leave.type'

    custom_project_manager_approval_needed = fields.Boolean(
        string="Project Manager / Department Head Approval?",
    )