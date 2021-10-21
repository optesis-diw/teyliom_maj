# -*- coding: utf-8 -*-
# from odoo import http


# class Immobilier(http.Controller):
#     @http.route('/immobilier/immobilier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/immobilier/immobilier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('immobilier.listing', {
#             'root': '/immobilier/immobilier',
#             'objects': http.request.env['immobilier.immobilier'].search([]),
#         })

#     @http.route('/immobilier/immobilier/objects/<model("immobilier.immobilier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('immobilier.object', {
#             'object': obj
#         })
