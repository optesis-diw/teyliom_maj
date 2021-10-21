
    
# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, exceptions, _
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, _



                
class crm_update(models.Model):
    _inherit = 'crm.lead'  
    


  
    superficie = fields.Float(related='bien.superficie')
    
    ilot_ids = fields.Many2one(related='bien.ilot_ids')
    phase_ids = fields.Many2one(related='bien.phase_ids')
