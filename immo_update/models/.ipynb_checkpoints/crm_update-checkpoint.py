
    
# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, exceptions, _
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



                
class crm_update(models.Model):
    _inherit = 'crm.lead'  
    


  
    superficie = fields.Float(related='bien.superficie')
    
    ilot_ids = fields.Many2one(related='bien.ilot_ids')
    phase_ids = fields.Many2one(related='bien.phase_ids')
    
    date_debut = fields.Date('Date de début', related='ilot_ids.date_debut') 
    date_fin = fields.Date('Date de fin', related='ilot_ids.date_fin')
    
    date_debut_crm = fields.Date('Date de début', compute='_get_end_date_debut') 
    date_fin_crm = fields.Date('Date de fin', compute='_get_end_date_fin')
    

    

    @api.depends('date_debut')
    def _get_end_date_debut(self):
        for r in self:
             r.date_debut_crm = r.date_debut
                
    @api.depends('date_fin')
    def _get_end_date_fin(self):
        for r in self:
             r.date_fin_crm = r.date_fin           
            
    
    @api.constrains('date_debut_crm', 'date_fin_crm', 'date_livraison')
    def date_constrains(self):
        for rec in self:
            if rec.date_livraison < rec.date_debut_crm:
                raise ValidationError("date de livraison doit être comprise entre " + str(rec.date_debut_crm) + " et " + str(rec.date_fin_crm)) 
            if rec.date_fin_crm < rec.date_livraison:
                 raise ValidationError("date de livraison doit être comprise entre " + str(rec.date_debut_crm) + " et " + str(rec.date_fin_crm)) 
                
    
    
    status_ilot = fields.Selection([
        ('ouvert', 'Disponible à la vente'),
        ('ferme', 'Fermé'),
    ], string='status du ilot', related='ilot_ids.status_ilot')
    
    active_ouvert = fields.Boolean()

    active_ferme = fields.Boolean()

    vrai = fields.Boolean('vrai', default=True)
    

    @api.onchange('status_ilot')
    def _onchangebien(self):
        for r in self:
            if (self.status_ilot) == 'ouvert':
                r.active_ouvert = True
            else:
                r.active_ouvert = False

    @api.onchange('status_ilot')
    def _onchangebien_reserve(self):
        for r in self:
            if (self.status_ilot) == 'ferme':
                r.active_ferme = True
            else:
                r.active_ferme = False

    @api.constrains('vrai', 'active_ferme')
    def _constraint_status(self):
        for record in self:
            if record.active_ferme == record.vrai:
                raise ValidationError("Ce bien n'est pas dispo pour la vente")
            
