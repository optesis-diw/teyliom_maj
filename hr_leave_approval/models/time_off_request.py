# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    custom_is_project_manager_approval = fields.Boolean(
        string="Project Manager/Department Head Approved?",
        readonly=True,
        copy=False
    )
    custom_project_manager_approver_id = fields.Many2one(
        'hr.employee', 
        string='Approved by Project Manager/Department Head', 
        readonly=True, 
        copy=False,
    )
    is_custom_warn_massage = fields.Boolean(
        string="Is Custom Information Message?",
        compute="_compute_is_custom_warn_massage",
        store = True
    )

    @api.depends('holiday_status_id', 'holiday_status_id.custom_project_manager_approval_needed','holiday_status_id.validation_type', 'custom_is_project_manager_approval')
    def _compute_is_custom_warn_massage(self):
        for rec in self:
            if not rec.custom_is_project_manager_approval and rec.holiday_status_id.custom_project_manager_approval_needed and rec.holiday_status_id.validation_type in ['hr','manager','both']:
                rec.is_custom_warn_massage = True
            else:
                rec.is_custom_warn_massage = False
                
    def action_approve(self):
        res = super(HolidaysRequest, self).action_approve()
        for rec in self:
            if rec.is_custom_warn_massage:
                raise UserError(_('Project Manager/Department Head Approval Pending.So you can not Approve Leave.'))
        return res

    def action_custom_project_manager_approve(self):
        for rec in self:
            if not rec.employee_id.custom_project_manager_id.id == self.env.user.id:
                raise UserError(_('You are not allow to Approve.'))
            if not rec.custom_is_project_manager_approval and rec.holiday_status_id.custom_project_manager_approval_needed and rec.holiday_status_id.validation_type in ['hr','manager','both']:
                from_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                if from_employee:
                    return rec.write({
                        'custom_is_project_manager_approval': True,
                        'custom_project_manager_approver_id': from_employee.id
                    })
        return True