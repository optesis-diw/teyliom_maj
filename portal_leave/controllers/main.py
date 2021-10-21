# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from datetime import datetime
from odoo.tools import float_compare
from pytz import timezone, UTC
import logging
from dateutil.relativedelta import relativedelta
import dateutil.parser

_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
        for employee in employees:
            domain = [('employee_id', '=', employee.id)]
            values['leave_count'] = request.env['hr.leave'].sudo().search_count(domain)
            return values

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_leaves(self, page=1, sortby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        employees = request.env['hr.employee'].sudo().search([('user_id','=',user.id)])
        for employee in employees:
            domain = [('employee_id', '=', employee.id)]

            # pager
            leaves_count = request.env['hr.leave'].search_count(domain)
            pager = portal_pager(
                url="/my/leaves",
                total=leaves_count,
                page=page,
                step=self._items_per_page
            )

            leaves = request.env['hr.leave'].sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
            request.session['my_leaves_history'] = leaves.ids[:100]

            values.update({
                'leaves': leaves,
                'page_name': 'leave',
                'default_url': '/my/leaves',
                'pager': pager,
            })
            return request.render("portal_leave.portal_my_leaves", values)

    @http.route(['/leave/create'], type='http', auth="user", website=True)
    def create_new_leave(self, page=1, sortby=None, search=None, search_in='content', **kw):

        return request.render("portal_leave.registration_leave", {
            'leave_types': request.env['hr.leave.type'].sudo().search([]),
        })

    @http.route(['/leave/register'], type='http', auth="user", website=True)
    def create_new_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        user = request.env.user
        _logger.info(kw.get('state_id'))
        from_date =''
        to_date = datetime.now().date()
        if kw.get('request_date_from'):
            from_date = dateutil.parser.parse(kw.get('request_date_from')).date()
        if kw.get('request_date_to'):
            to_date = dateutil.parser.parse(kw.get('request_date_to')).date()
        type_id = request.env['hr.leave.type'].sudo().browse(int(kw['state_id']))
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        for employee in employees:
            period = ''
            if kw.get('halfday'):
                if kw.get('period') == 'Morning':
                    period = 'am'
                if kw.get('period') == 'Afternoon':
                    period = 'pm'

                domain = [('calendar_id', '=', employee.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain,order='dayofweek, day_period DESC')
                # find first attendance coming after first_day
                attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),attendances[0])
                # find last attendance coming before last_day
                attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= from_date.weekday()),attendances[-1])
                if period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
                tz = request.env.user.tz  # custom -> already in UTC
                date_from= timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                    UTC).replace(tzinfo=None)
                date_to=timezone(tz).localize(datetime.combine(from_date, hour_to)).astimezone(UTC).replace(tzinfo=None)

                nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                    ('date_to', '>', date_from),
                    ('employee_id', '=', employee.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                ])
                if nholidays:
                    return request.render("portal_leave.registration_leave", {
                        'leave_types': request.env['hr.leave.type'].sudo().search([]),
                        'overlaps': True,
                    })
                if type_id.allocation_type != 'no':
                    leave_days = type_id.get_days(employee.id)[type_id.id]
                    _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                    _logger.info(leave_days)
                    if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                            float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        return request.render("portal_leave.registration_leave", {
                            'leave_types': request.env['hr.leave.type'].sudo().search([]),
                            'sufficient': True,
                        })

                values = {
                    'employee_id': employee.id,
                    'holiday_status_id': int(kw.get('state_id')),
                    'request_date_from': kw.get('request_date_from'),
                    'request_date_to': kw.get('request_date_from'),
                    'number_of_days':0.5,
                    'request_date_from_period': period,
                    'request_unit_half': kw.get('halfday'),
                    'name': kw.get('name'),
                }
                _logger.info(values)
                leave = request.env['hr.leave'].sudo().create(values)
                if not leave.request_date_from:
                    leave.date_from = False
                    return

                if leave.request_unit_half or leave.request_unit_hours:
                    leave.request_date_to = leave.request_date_from

                if not leave.request_date_to:
                    leave.date_to = False
                    return

                domain = [('calendar_id', '=',
                           leave.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

                # find first attendance coming after first_day
                attendance_from = next(
                    (att for att in attendances if int(att.dayofweek) >= leave.request_date_from.weekday()), attendances[0])
                # find last attendance coming before last_day
                attendance_to = next(
                    (att for att in reversed(attendances) if int(att.dayofweek) <= leave.request_date_to.weekday()),
                    attendances[-1])

                if leave.request_unit_half:
                    if leave.request_date_from_period == 'am':
                        hour_from = float_to_time(attendance_from.hour_from)
                        hour_to = float_to_time(attendance_from.hour_to)
                    else:
                        hour_from = float_to_time(attendance_to.hour_from)
                        hour_to = float_to_time(attendance_to.hour_to)
                else:
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)

                tz = request.env.user.tz if request.env.user.tz and not leave.request_unit_custom else 'UTC'  # custom -> already in UTC
                leave.write({'date_from' : timezone(tz).localize(datetime.combine(leave.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None),'date_to' : timezone(tz).localize(datetime.combine(leave.request_date_to, hour_to)).astimezone(
                    UTC).replace(tzinfo=None)})
                if leave.date_from and leave.date_to:
                    leave.write({'number_of_days' : leave._get_number_of_days(leave.date_from, leave.date_to, leave.employee_id.id)['days']})
                else:
                    leave.write({'number_of_days' : 0})

            if not kw.get('halfday'):
                domain = [('calendar_id', '=', employee.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain,order='dayofweek, day_period DESC')
                # find first attendance coming after first_day
                attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),attendances[0])
                # find last attendance coming before last_day
                attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= to_date.weekday()),attendances[-1])
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
                tz = request.env.user.tz  # custom -> already in UTC
                date_from= timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                    UTC).replace(tzinfo=None)
                date_to=timezone(tz).localize(datetime.combine(to_date, hour_to)).astimezone(UTC).replace(tzinfo=None)
                nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                    ('date_to', '>', date_from),
                    ('employee_id', '=', employee.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                ])
                if nholidays:
                    return request.render("portal_leave.registration_leave", {
                        'leave_types': request.env['hr.leave.type'].sudo().search([]),
                        'overlaps': True,
                    })

                if type_id.allocation_type != 'no':
                    leave_days = type_id.get_days(employee.id)[type_id.id]
                    _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                    _logger.info(leave_days)
                    if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                            float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                            float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        return request.render("portal_leave.registration_leave", {
                            'leave_types': request.env['hr.leave.type'].sudo().search([]),
                            'sufficient': True,
                        })

                values = {
                    'employee_id': employee.id,
                    'holiday_status_id': int(kw.get('state_id')),
                    'request_date_from': kw.get('request_date_from'),
                    'request_date_to': kw.get('request_date_to') or datetime.now().date(),
                    'name': kw.get('name'),
                }
                leave = request.env['hr.leave'].sudo().create(values)
                if not leave.request_date_from:
                    leave.date_from = False
                    return

                if leave.request_unit_half or leave.request_unit_hours:
                    leave.request_date_to = leave.request_date_from

                if not leave.request_date_to:
                    leave.date_to = False
                    return

                domain = [('calendar_id', '=',
                           leave.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
                attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

                # find first attendance coming after first_day
                attendance_from = next(
                    (att for att in attendances if int(att.dayofweek) >= leave.request_date_from.weekday()), attendances[0])
                # find last attendance coming before last_day
                attendance_to = next(
                    (att for att in reversed(attendances) if int(att.dayofweek) <= leave.request_date_to.weekday()),
                    attendances[-1])

                if leave.request_unit_half:
                    if leave.request_date_from_period == 'am':
                        hour_from = float_to_time(attendance_from.hour_from)
                        hour_to = float_to_time(attendance_from.hour_to)
                    else:
                        hour_from = float_to_time(attendance_to.hour_from)
                        hour_to = float_to_time(attendance_to.hour_to)
                else:
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)

                tz = request.env.user.tz if request.env.user.tz and not leave.request_unit_custom else 'UTC'  # custom -> already in UTC
                leave.write({'date_from' : timezone(tz).localize(datetime.combine(leave.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None),'date_to' : timezone(tz).localize(datetime.combine(leave.request_date_to, hour_to)).astimezone(
                    UTC).replace(tzinfo=None)})
                if leave.date_from and leave.date_to:
                    leave.write({'number_of_days' : leave._get_number_of_days(leave.date_from, leave.date_to, leave.employee_id.id)['days']})
                else:
                    leave.write({'number_of_days' : 0})

        return request.redirect("/my/leaves")

    @http.route(['/leave/editable/<int:leave_id>'], type='http', auth="user", website=True)
    def editable_leave(self, page=1, sortby=None, search=None, search_in='content', **kw):
        return request.render("portal_leave.edit_leave", {
            'leave_types': request.env['hr.leave.type'].sudo().search([]),
            'leave' : request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
        })

    @http.route(['/leave/edit/'], type='http', auth="user", website=True)
    def edit_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        type_id = request.env['hr.leave.type'].sudo().browse(int(kw['state_id']))
        if kw.get('request_date_from'):
            from_date = dateutil.parser.parse(kw.get('request_date_from')).date()
        if kw.get('request_date_to'):
            to_date = dateutil.parser.parse(kw.get('request_date_to')).date()
        else:
            to_date = datetime.now().date()
        leave_id = request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
        period = ''
        if kw.get('halfday'):
            if kw.get('period') == 'am':
                period = 'am'
            if kw.get('period') == 'pm':
                period = 'pm'

            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),
                                   attendances[0])
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= from_date.weekday()),
                                 attendances[-1])
            if period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
            tz = request.env.user.tz  # custom -> already in UTC
            date_from = timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                UTC).replace(tzinfo=None)
            date_to = timezone(tz).localize(datetime.combine(from_date, hour_to)).astimezone(UTC).replace(tzinfo=None)

            nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                                                                     ('date_to', '>', date_from),
                                                                     ('employee_id', '=', leave_id.employee_id.id),
                                                                     ('id', '!=', leave_id.id),
                                                                     ('state', 'not in', ['cancel', 'refuse']),
                                                                     ])
            if nholidays:
                return request.render("portal_leave.registration_leave", {
                    'leave_types': request.env['hr.leave.type'].sudo().search([]),
                    'overlaps': True,
                })

            if type_id.allocation_type != 'no':
                leave_days = type_id.get_days(leave_id.employee_id.id)[type_id.id]
                _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                _logger.info(leave_days)
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                        float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    return request.render("portal_leave.registration_leave", {
                        'leave_types': request.env['hr.leave.type'].sudo().search([]),
                        'sufficient': True,
                    })

            leave_id.write({
                'holiday_status_id': int(kw.get('state_id')),
                'request_date_from': kw.get('request_date_from'),
                'request_date_to': kw.get('request_date_from'),
                'request_date_from_period': period,
                'number_of_days':0.5,
                'request_unit_half': kw.get('halfday'),
                'name': kw.get('name'),
            })
            if not leave_id.request_date_from:
                leave_id.date_from = False
                return

            if leave_id.request_unit_half or leave_id.request_unit_hours:
                leave_id.request_date_to = leave_id.request_date_from

            if not leave_id.request_date_to:
                leave_id.date_to = False
                return

            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

            # find first attendance coming after first_day
            attendance_from = next(
                (att for att in attendances if int(att.dayofweek) >= leave_id.request_date_from.weekday()), attendances[0])
            # find last attendance coming before last_day
            attendance_to = next(
                (att for att in reversed(attendances) if int(att.dayofweek) <= leave_id.request_date_to.weekday()),
                attendances[-1])

            if leave_id.request_unit_half:
                if leave_id.request_date_from_period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
            else:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)

            tz = request.env.user.tz if request.env.user.tz and not leave_id.request_unit_custom else 'UTC'  # custom -> already in UTC
            leave_id.write(
                {'date_from': timezone(tz).localize(datetime.combine(leave_id.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None),
                 'date_to': timezone(tz).localize(datetime.combine(leave_id.request_date_to, hour_to)).astimezone(
                     UTC).replace(tzinfo=None)})
            if leave_id.date_from and leave_id.date_to:
                leave_id.write(
                    {'number_of_days': leave_id._get_number_of_days(leave_id.date_from, leave_id.date_to, leave_id.employee_id.id)['days']})
            else:
                leave_id.write({'number_of_days': 0})

        if not kw.get('halfday'):
            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')
            # find first attendance coming after first_day
            attendance_from = next((att for att in attendances if int(att.dayofweek) >= from_date.weekday()),
                                   attendances[0])
            # find last attendance coming before last_day
            attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= to_date.weekday()),
                                 attendances[-1])
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)
            tz = request.env.user.tz  # custom -> already in UTC
            date_from = timezone(tz).localize(datetime.combine(from_date, hour_from)).astimezone(
                UTC).replace(tzinfo=None)
            date_to = timezone(tz).localize(datetime.combine(to_date, hour_to)).astimezone(UTC).replace(tzinfo=None)
            nholidays = request.env['hr.leave'].sudo().search_count([('request_date_from', '<=', date_to),
                                                                     ('date_to', '>', date_from),
                                                                     ('employee_id', '=', leave_id.employee_id.id),
                                                                     ('id', '!=', leave_id.id),
                                                                     ('state', 'not in', ['cancel', 'refuse']),
                                                                     ])
            if nholidays:
                return request.render("portal_leave.registration_leave", {
                    'leave_types': request.env['hr.leave.type'].sudo().search([]),
                    'overlaps': True,
                })
            if type_id.allocation_type != 'no':
                leave_days = type_id.get_days(leave_id.employee_id.id)[type_id.id]
                _logger.info("Leave Days ----------------------------->>>>>>>>>>>>>>>>>")
                _logger.info(leave_days)
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                        float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == 0 or \
                        float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    return request.render("portal_leave.registration_leave", {
                        'leave_types': request.env['hr.leave.type'].sudo().search([]),
                        'sufficient': True,
                    })

            leave_id.write({
                'holiday_status_id': int(kw.get('state_id')),
                'request_date_from': kw.get('request_date_from'),
                'request_date_to':kw.get('request_date_to') or datetime.now().date(),
                'request_unit_half': False,
                'name': kw.get('name'),
            })
            if not leave_id.request_date_from:
                leave_id.date_from = False
                return

            if leave_id.request_unit_half or leave_id.request_unit_hours:
                leave_id.request_date_to = leave_id.request_date_from

            if not leave_id.request_date_to:
                leave_id.date_to = False
                return

            domain = [('calendar_id', '=',
                       leave_id.employee_id.resource_calendar_id.id or request.env.user.company_id.resource_calendar_id.id)]
            attendances = request.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

            # find first attendance coming after first_day
            attendance_from = next(
                (att for att in attendances if int(att.dayofweek) >= leave_id.request_date_from.weekday()), attendances[0])
            # find last attendance coming before last_day
            attendance_to = next(
                (att for att in reversed(attendances) if int(att.dayofweek) <= leave_id.request_date_to.weekday()),
                attendances[-1])

            if leave_id.request_unit_half:
                if leave_id.request_date_from_period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
            else:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)

            tz = request.env.user.tz if request.env.user.tz and not leave_id.request_unit_custom else 'UTC'  # custom -> already in UTC
            leave_id.write(
                {'date_from': timezone(tz).localize(datetime.combine(leave_id.request_date_from, hour_from)).astimezone(
                    UTC).replace(tzinfo=None),
                 'date_to': timezone(tz).localize(datetime.combine(leave_id.request_date_to, hour_to)).astimezone(
                     UTC).replace(tzinfo=None)})
            if leave_id.date_from and leave_id.date_to:
                leave_id.write(
                    {'number_of_days': leave_id._get_number_of_days(leave_id.date_from, leave_id.date_to, leave_id.employee_id.id)['days']})
            else:
                leave_id.write({'number_of_days': 0})

        return request.redirect("/my/leaves")

    @http.route(['/leave/delete/'], type='http', auth="user", website=True)
    def delete_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
            leave_id = request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
            leave_id.unlink()
            return request.redirect("/my/leaves")

    @http.route(['/leave/readonly/<int:leave_id>'], type='http', auth="user", website=True)
    def view_leave_request(self, page=1, sortby=None, search=None, search_in='content', **kw):
        return request.render("portal_leave.view_leave", {
            'leave': request.env['hr.leave'].sudo().browse(int(kw['leave_id']))
        })