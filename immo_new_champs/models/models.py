# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class immo_new_champs(models.Model):
#     _name = 'immo_new_champs.immo_new_champs'
#     _description = 'immo_new_champs.immo_new_champs'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
