# -*- coding: utf-8 -*-
# from odoo import http


# class ImmoUpdate(http.Controller):
#     @http.route('/immo_update/immo_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/immo_update/immo_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('immo_update.listing', {
#             'root': '/immo_update/immo_update',
#             'objects': http.request.env['immo_update.immo_update'].search([]),
#         })

#     @http.route('/immo_update/immo_update/objects/<model("immo_update.immo_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('immo_update.object', {
#             'object': obj
#         })
