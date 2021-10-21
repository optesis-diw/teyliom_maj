# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
import logging
import base64

_logger = logging.getLogger(__name__)

class PortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        for employee in employees:
            domain = [('employee_id', '=', employee.id)]
            values['expense_count'] = request.env['hr.expense'].sudo().search_count(domain)
            return values

    def insert_attachment(self, model, id_record, files):
        orphan_attachment_ids = []
        record = model.env[model.model].browse(id_record)
        for file in files:
            attachment_value = {
                'name': 'Expense bill',
                'datas': base64.encodestring(file.load()),
                'datas_fname': 'expense attachment',
                'res_model': model.model,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            orphan_attachment_ids.append(attachment_id.id)

    @http.route(['/my/expenses', '/my/expenses/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_expenses(self, page=1, sortby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id','=',user.id)])
        for employee in employees:
            domain = [('employee_id', '=', employee.id)]

            # pager
            expenses_count = request.env['hr.expense'].search_count(domain)
            pager = portal_pager(
                url="/my/expenses",
                total=expenses_count,
                page=page,
                step=self._items_per_page
            )

            expenses = request.env['hr.expense'].sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
            request.session['my_expenses_history'] = expenses.ids[:100]

            values.update({
                'expenses': expenses,
                'page_name': 'expense',
                'default_url': '/my/expenses',
                'pager': pager,
            })
            return request.render("portal_expense.portal_my_expenses", values)

    @http.route(['/expense/create'], type='http', auth="user", website=True)
    def create_new_expense(self, page=1, sortby=None, search=None, search_in='content', **kw):

        return request.render("portal_expense.registration_expense", {
            'product_types': request.env['product.product'].sudo().search([('can_be_expensed','=',True)]),
        })

    @http.route(['/expense/register'], type='http', auth="user", website=True)
    def create_new_expense_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        for employee in employees:
            mode = ''
            if kw.get('payment_mode') == 'Employee':
                mode = 'own_account'
            else:
                mode = 'company_account'

            values = {
                'name': kw.get('name'),
                'employee_id': employee.id,
                'department_id': employee.department_id.id,
                'user_id': employee.expense_manager_id.id or employee.parent_id.user_id.id,
                'state': 'submit',
                'payment_mode': mode,
            }
            sheet_id = request.env['hr.expense.sheet'].sudo().create(values)

            values = {
                'name': kw.get('name'),
                'employee_id': employee.id,
                'product_id': int(kw.get('product_id')),
                'unit_amount': kw.get('price'),
                'date': kw.get('date'),
                'payment_mode': mode,
                'quantity':kw.get('quantity'),
                'name': kw.get('name'),
                'sheet_id':sheet_id.id,
            }
            expense = request.env['hr.expense'].sudo().create(values)
            account = expense.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                expense.account_id = account
            if kw['attachments']:
                attachment_value = {
                    'name': kw['attachments'].filename,
                    'datas': base64.encodestring(kw['attachments'].read()),
                    'store_fname': kw['attachments'].filename,
                    'res_model': 'hr.expense',
                    'res_id': expense.id,
                }
                request.env['ir.attachment'].sudo().create(attachment_value)

        return request.redirect("/my/expenses")

    @http.route(['/expense/editable/<int:expense_id>'], type='http', auth="user", website=True)
    def editable_expense(self, page=1, sortby=None, search=None, search_in='content', **kw):
        expense_id = request.env['hr.expense'].sudo().browse(int(kw['expense_id']))
        att = request.env['ir.attachment'].sudo().search([
            ('res_id', '=', expense_id.id),
            ('res_model', '=', 'hr.expense'),
            ('type', '=', 'binary')])
        return request.render("portal_expense.edit_expense", {
            'product_types': request.env['product.product'].sudo().search([('can_be_expensed','=',True)]),
            'expense' : request.env['hr.expense'].sudo().browse(int(kw['expense_id'])),
            'attachment_details': att,
        })

    @http.route(['/expense/edit/'], type='http', auth="user", website=True)
    def edit_expense_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        expense_id = request.env['hr.expense'].sudo().browse(int(kw['expense_id']))
        mode = ''
        if kw.get('payment_mode') == 'Employee':
            mode = 'own_account'
        else:
            mode = 'company_account'

        _logger.info(kw.get('payment_mode'))
        _logger.info(kw.get('mode'))
        _logger.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        values = {
            'name': kw.get('name'),
            'product_id': int(kw.get('product_id')),
            'unit_amount': kw.get('price'),
            'date': kw.get('date'),
            'payment_mode': mode,
            'quantity': kw.get('quantity'),
            'name': kw.get('name'),
        }
        expense_id.write(values)
        if kw['attachments']:
            attachment_value = {
                'name': kw['attachments'].filename,
                'datas': base64.encodestring(kw['attachments'].read()),
                'datas_fname': kw['attachments'].filename,
                'res_model': 'hr.expense',
                'res_id': expense_id.id,
            }
            request.env['ir.attachment'].sudo().create(attachment_value)

        return request.redirect("/my/expenses")

    @http.route(['/expense/delete/'], type='http', auth="user", website=True)
    def delete_expense_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
            expense_id = request.env['hr.expense'].sudo().browse(int(kw['expense_id']))
            expense_id.unlink()
            return request.redirect("/my/expenses")

    @http.route(['/expense/readonly/<int:expense_id>'], type='http', auth="user", website=True)
    def view_expense_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        expense_id = request.env['hr.expense'].sudo().browse(int(kw['expense_id']))
        att = request.env['ir.attachment'].sudo().search([
            ('res_id', '=', expense_id.id),
            ('res_model', '=', 'hr.expense'),
            ('type', '=', 'binary')])
        return request.render("portal_expense.view_expense", {
            'expense': request.env['hr.expense'].sudo().browse(int(kw['expense_id'])),
            'product_types': request.env['product.product'].sudo().search([('can_be_expensed', '=', True)]),
            'attachment_details': att,
        })

    @http.route(['/delete/attachment/<int:attachment_id>/<int:expense_id>'], type='http', auth="user", website=True)
    def delete_expense_request_attachment(self, page=1, sortby=None, search=None, search_in='content', **kw):
        attachment_id = request.env['ir.attachment'].sudo().browse(int(kw['attachment_id']))
        expense_id = request.env['hr.expense'].sudo().browse(int(kw['expense_id']))
        _logger.info('Logger is working')
        attachment_id.sudo().unlink()
        att = request.env['ir.attachment'].sudo().search([
            ('res_id', '=', expense_id.id),
            ('res_model', '=', 'hr.expense'),
            ('type', '=', 'binary')])
        return request.render("portal_expense.edit_expense", {
            'product_types': request.env['product.product'].sudo().search([('can_be_expensed','=',True)]),
            'expense' : expense_id,
            'attachment_details': att,
        })