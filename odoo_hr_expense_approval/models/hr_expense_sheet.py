# -*- coding: utf-8 -*-

from odoo import fields, models, api , _ #odoo13
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError #odoo13


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    department_manager_probc_id = fields.Many2one(
        # related='sheet_id.department_manager_id', #odoo13
        # store=True, #odoo13
        'hr.employee', #odoo13
        string='Department Manager',
        copy=True, #odoo13
    ) 

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection([
            ('draft', 'Draft'), #odoo13
            ('submit', 'Submitted'),
            ('department_app', 'Approved By Department'),
            ('approve', 'Approved'),
            ('finance_app', 'Approved By Finance'),
            ('post', 'Posted'),
            ('done', 'Paid'),
            ('cancel', 'Refused')],
            # string='Status',
            # index=True,
            # readonly=True,
            # track_visibility='onchange',
            # copy=False,
            # default='submit',
            # required=True,
            # help='Expense Report State'
    )
    department_manager_id = fields.Many2one(
        'hr.employee',
        'Department Manager',
    )
    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.department_manager_id = self.employee_id.parent_id.id

#    state = fields.Selection(
#        selection_add=[('department_app', 'Department Approval'),
#                    ('finance_app', 'Finanace Approval'),
#        ]
#    )

    # @api.multi #odoo13
    def approve_department_expense_sheets(self):
        for rec in self:
            rec.state = 'department_app'

    # @api.multi #odoo13
    def approve_finance_expense_sheets(self):
        for rec in self:
            rec.state = 'finance_app'

    # @api.multi #odoo13 # Below method is Fully Override
    def action_sheet_move_create(self):
        if any(sheet.state != 'finance_app' for sheet in self):
            raise UserError(_("You can only generate accounting entry for Finanace Approval expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.action_move_create()

        if not self.accounting_date:
            self.accounting_date = self.account_move_id.date

        if self.payment_mode == 'own_account' and expense_line_ids:
            self.write({'state': 'post'})
        else:
            self.write({'state': 'done'})
        self.activity_update()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
