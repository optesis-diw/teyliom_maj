

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class modele_acticle(models.Model):
    _inherit = 'product.template'
 
    
    
    ilot_ids = fields.Many2one('lb.ilot', string="Ilot")
    phase_ids = fields.Many2one('lb.phase', string="Phase")
  
    
    

    
class modele_ilot(models.Model):
    _name = 'lb.ilot'
    _description = "ilot"
    _rec_name = 'name_ilot'

    name_ilot = fields.Char('Ilot')
    status_ilot = fields.Selection([
        ('ouvert', 'Disponible à la vente'),
        ('ferme', 'Fermé'),
    ], string='status du ilot')
    
   
  
    date_debut = fields.Date('Date de début') 
    date_fin = fields.Date('Date de fin')
    


class modele_phase(models.Model):
    _name = 'lb.phase'
    _description = "Phase"
    _rec_name = 'name_phase'

    name_phase = fields.Char('Phase')
   

