
from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp


class Article(models.Model):
    _inherit = 'product.template'
    
    
    avenants = fields.Float(string="Avenant", store=True ,write=['immobilier.library_group_user_new'])
    prix_maj = fields.Float(string="Prix MAJ", compute='get_prix_maj')


    #if it is user connect than it True or it is false
    @api.onchange('avenants')   
    def get_prix_maj(self):
        for r in self:
            r.prix_maj = r.list_price + r.avenants   
            
    
   
    etat_bien_domain = fields.Selection([
        ('dispo', 'Disponible'),
        ('option', 'Option'),
       ('reserve', 'Réservé'),
    ], string='Etat du bien', related="etat_depend_etat")

        
    @api.model
    def fields_get(self, fields=None):
        hide = ['etat_depend_etat','etat','type_bien_ids']
        res = super(Article, self).fields_get()
        for field in hide:
            res[field]['selectable'] = False
        return res    
    
     
   
    def write(self, vals):
        if 'etat' in vals:
            etat_bien_domain = vals['etat']
        res = super(Article, self).write(vals)
        return res
    
    
   
            
    etat_depend_etat = fields.Selection([
        ('dispo', 'Disponible'),
        ('option', 'Option'),
       ('reserve', 'Réservé'),
    ], string='Etat', default="dispo", readonly=False) 
    

    user_connect = fields.Many2one('res.users', string='user_connect', compute='get_user_connect')

    #if it is user connect than it True or it is false
    @api.onchange('user_id','user_admin')   
    def get_user_connect(self):
        for r in self:
            r.user_connect = self.env.uid
    
    check_field = fields.Boolean('Check', compute='get_super')

    #if it is user connect than it True or it is false
    @api.onchange('user_id','user_admin')   
    def get_super(self):
        for r in self:
            if r.user_admin == self.env.user:
                r.check_field = True    
            else:
                r.check_field = False
    
    user_admin = fields.Many2one('res.users', string='admin', compute='get_admin')

    #if it is user connect than it True or it is false
    @api.onchange('user_admin')   
    def get_admin(self):
        for r in self:
            r.user_admin = 2
            
            
    
    etat = fields.Selection([
       ('dispo', 'Disponible'),
        ('option', 'Option'),
        ('reserve', 'Réservé'),
    ], string='Etat bien', compute='_onchange_etat_bien', default="dispo")

    @api.onchange('bien')
    def _onchange_etat_bien(self):
        for r in self:
            appointments = self.env['crm.lead'].search([('bien', '=', r.id)], order='id desc', limit=1)
            if appointments:
                for rec in appointments:
                    r.etat = rec.etat
            else:
                r.etat = 'dispo'   
    
   
          
    
    #@api.model
    #def #default_get(self, fields):
        #res = super(Article, self).default_get(fields)
        #res['res.country'] = 204
        #res['ville'] = 1
        #return res
    

    #pays = fields.Many2one('res.country', string="Pays")
    
    
    bien_ok = fields.Boolean('Est un Bien ?', default=False)
    
    
    user_id = fields.Many2one('res.users', string='Agent-Guide', track_visibility='onchange',
                              default=lambda self: self.env.user)
    team_id = fields.Many2one(
        'crm.team', 'Sales Team')      
  
    #pays = fields.Many2one('res.country', string="Pays")

    #name_pays = fields.Char(string="Nom du pays", related='pays.name')
    

    superficie = fields.Float(String="Superficie en m2")

    quartier = fields.Many2one('lb.quartier', string="Quartier")

    name_quartier = fields.Char(string="Nom du Quartier", related='quartier.nom_quartier')

    rue = fields.Char(string="Rue")

    ville = fields.Many2one('lb.ville', string="Ville")

    nom_ville = fields.Char(string="Ville", related='ville.nom')

   
    latitude = fields.Char(string="Latitude", default="0.0")
    longitude = fields.Char(string="Longitude", default="0.0")
    Date = fields.Date()
    
    nbre_tour = fields.Integer(string="Niveau")
    ameublement = fields.Char(string="Ameublement")

    

    chambres = fields.Integer(string="Nombre de chambres")
    salons = fields.Integer(string="Nombre de salons")
    cuisines = fields.Integer(string="Nombre de cuisines")
    toilette = fields.Integer(string="Nombre de toilettes")
    cour = fields.Integer(string="Espace de familiale")

    salles_bain = fields.Char(string="Nombre de salles de bain")
    parking = fields.Char(string="Nombre de parkings")
    balcon = fields.Char(string="Nombre de balcons")
    jardin = fields.Boolean(default=False, string="Jardin")
    ascenseur = fields.Boolean(default=False, string="Ascenseur")
    g_electroge = fields.Boolean(default=False, string="Groupe electrogène")

    oriente_vers = fields.Char(string="Position du bien", default='Bordure route principale')
   

    notes = fields.Text(string="Notes")

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('lb.location'),
                                 index=1)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')

    # 2 fonctions pour l'image attaché
    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for bien in self:
            bien.doc_count = Attachment.search_count([('res_model', '=', 'lb.bien'), ('res_id', '=', bien.id)])

    
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'lb.bien'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                            Cliquez sur créer (et non importer) pour ajouter les images associées à vos biens.</p><p>
                        </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

   
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    # kanban: qui affiche les sessions regroupées par cours (les colonnes sont donc des cours)
    color = fields.Integer()

    # géolocalisation du bien
    def tt_locate_bien(self):
        return {
            "type": "ir.actions.act_url",
            "url": 'https://www.google.com/maps/search/?api=1&query=' + self.longitude + ', -' + self.latitude,
        }

    # champs: lien avec les information du bien
   
    plus_proche_ids = fields.Many2many('lb.lieu', string="Lieux plus proche")
    sous_propriete_ids = fields.Many2many('lb.sous_propriete', string="Détail des pièces")

    # champs: Plans d'étage, photos et documents
    plan_ids = fields.Many2many('lb.plan_etage', string="Plans")
    photos_ids = fields.Many2many('lb.photos', string="Photos")
    documents_ids = fields.Many2many('lb.documents', string="Documents")
       
    name_categ_id = fields.Char(related='categ_id.name', string="Catégorie du Bien")

    superficie = fields.Float(String="Superficie(m²)")
    
    
    type_bien_ids = fields.Many2one('lb.type_bien', string="Type de bien")
    nom_projet_ids = fields.Many2one('lb.projet', string="Projet")
    
    
    

    
class type_lieu(models.Model):
    _name = 'lb.type_lieu'
    _description = "Type de lieu"
    _rec_name = 'type_lieu'

    type_lieu = fields.Char('Type de lieu')


class plus_proche(models.Model):
    _name = 'lb.lieu'
    _description = "Nom du lieu"
    _rec_name = 'name_lieu'

    name_lieu = fields.Char('Nom du lieu')
    type_lieu = fields.Many2one('lb.type_lieu', string="Type de lieu")
    distance = fields.Float(string="Distance(m)", default=5)


class sous_propriete(models.Model):
    _name = 'lb.sous_propriete'
    _description = "Sous propriété"
    _rec_name = 'type_piece'

    type_piece = fields.Many2one('lb.type_piece', string="Type de pièces")
    height = fields.Float(string="longueur(m)", default=3.0)
    width = fields.Float(string="Largeur(m)", default=2.0)


class type_piece(models.Model):
    _name = 'lb.type_piece'
    _description = "Type de pièces"
    _rec_name = 'type_piece'

    type_piece = fields.Char('Type de pièces')


class Plans_etage(models.Model):
    _name = 'lb.plan_etage'
    _description = "Plan du bien"
    _rec_name = 'description_plan'

    description_plan = fields.Char('Description plan')
    photos_plan = fields.Binary(string="Photos plan", attachment=True)


class photos(models.Model):
    _name = 'lb.photos'
    _description = "Photos"
    _rec_name = 'description'

    description = fields.Char('Description')
    photos = fields.Binary(string="Photos", attachment=True)


class documents(models.Model):
    _name = 'lb.documents'
    _description = "Documents"
    _rec_name = 'description'

    description = fields.Char('Description')
    date_expiration = fields.Date('Date expiration')
    fichier = fields.Binary(string="Fichiers", attachment=True)
    
    
    

class Ville(models.Model):
    _name = 'lb.ville'
    _description = "Villes"
    _rec_name = 'nom'

    nom = fields.Char(string="Ville")


class Quartier(models.Model):
    _name = 'lb.quartier'
    _description = "Quartiers"
    _rec_name = 'nom_quartier'

    nom_quartier = fields.Char(string="Quartier")
    
class Type_bien(models.Model):
    _name = 'lb.type_bien'
    _description = "Type de biens"
    _rec_name = 'name_type_bien'

    name_type_bien = fields.Char(string="type bien")
    
class projet_bien(models.Model):
    _name = 'lb.projet'
    _description = "Projets"
    _rec_name = 'nom_projet'

    nom_projet = fields.Char(string="Nom du projet")
   
    
   
    

    

    