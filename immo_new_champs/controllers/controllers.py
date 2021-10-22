# -*- coding: utf-8 -*-
# from odoo import http


# class ImmoNewChamps(http.Controller):
#     @http.route('/immo_new_champs/immo_new_champs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/immo_new_champs/immo_new_champs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('immo_new_champs.listing', {
#             'root': '/immo_new_champs/immo_new_champs',
#             'objects': http.request.env['immo_new_champs.immo_new_champs'].search([]),
#         })

#     @http.route('/immo_new_champs/immo_new_champs/objects/<model("immo_new_champs.immo_new_champs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('immo_new_champs.object', {
#             'object': obj
#         })
