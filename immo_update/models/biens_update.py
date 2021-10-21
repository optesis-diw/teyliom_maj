

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _



class modele_acticle(models.Model):
    _inherit = 'product.template'
 
    
    
    ilot_ids = fields.Many2one('lb.ilot', string="Ilot")
    phase_ids = fields.Many2one('lb.phase', string="Phase")
    
    
    

    
class modele_ilot(models.Model):
    _name = 'lb.ilot'
    _description = "ilot"
    _rec_name = 'name_ilot'

    name_ilot = fields.Char('Ilot')


class modele_phase(models.Model):
    _name = 'lb.phase'
    _description = "Phase"
    _rec_name = 'name_phase'

    name_phase = fields.Char('Phase')
   

