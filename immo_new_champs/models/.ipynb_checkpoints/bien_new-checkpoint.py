
from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp


class Article_new(models.Model):
    _inherit = 'product.template'
    
    
    avenants = fields.Float(string="Avenant", store=True ,write=['immobilier.library_group_user_new'])
    prix_maj = fields.Float(string="Prix MAJ", compute='get_prix_maj')


    #if it is user connect than it True or it is false
    @api.onchange('avenants')   
    def get_prix_maj(self):
        for r in self:
            r.prix_maj = r.list_price + r.avenants   
            