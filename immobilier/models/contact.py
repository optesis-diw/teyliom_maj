# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class potenciel(models.Model):
    _inherit = 'res.partner'
    
  
    
    client = fields.Boolean('Client', default=False)
    prospect = fields.Boolean('Prospect', default=False)
    apporteur_affaires = fields.Boolean('Apporteur d’affaires', default=False)
    cooperative = fields.Boolean('Coopérative', default=False)
    origine_id = fields.Many2one('lb.origine', string="Origine")
    source_id = fields.Many2one('lb.source', string="Source")
    
    
    #pour les contacts (apporteur) et contacts d'une coopopérative
    nature_apporteur_id = fields.Many2one('lb.nature_apporteur', string="Est'apporteur")
    
    
    
    taux_apporteur = fields.Float(related='nature_apporteur_id.taux_apporteur', string="Taux Nature Apporteur(%)")
    
    est_cooperative = fields.Boolean('Est une coopérative', default=False, readonly=True)
    
    contact_cooperative = fields.One2many('res.partner','nom_cooperative', string='Membre de la Coopérative')
     
    #contact_cooperative = fields.One2many('res.partner','nom_cooperative', string='Nom de la Coopérative', domain = "[('nom_cooperative', '=', self.id)]")
           
    
    nom_cooperative = fields.Many2one('res.partner', string='Nom de la Coopérative')
    
    taux_cooperative = fields.Float(string='Taux coopérative(%)')    
    
    profession_id = fields.Many2one('immo.user_profession', string="Profession")
    

class origine(models.Model):
    _name = "lb.origine"
    _description = "name_origine"
    _rec_name = 'name_origine'

    name_origine = fields.Char()

class source(models.Model):
    _name = "lb.source"
    _description = "name_source"
    _rec_name = 'name_source'

    name_source = fields.Char()    
                  

class nature_apporteur(models.Model):
    _name = 'lb.nature_apporteur'
    _description = "nature_apporteur"
    _rec_name = 'nature_apporteur'

    nature_apporteur = fields.Char("Nature apporteur")
    taux_apporteur = fields.Float(string="Taux Nature Apporteur(%)")
    contacts_apporteur = fields.One2many('res.partner','nature_apporteur_id', string='Contacts apporteur')
   
                       
    

class profession(models.Model):
    _name = 'immo.user_profession'
    _description = "user_profession"
    
    name = fields.Char("profession")
    
    