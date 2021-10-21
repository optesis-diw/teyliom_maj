
    
# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, exceptions, _
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re

from datetime import date
from dateutil.relativedelta import relativedelta
_
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.osv import expression
from odoo.tools import float_compare, pycompat
from odoo.addons import decimal_precision as dp

from odoo.exceptions import ValidationError



                
class crm(models.Model):
    _inherit = 'crm.lead' 
    
 
    
    @api.model
    def field_filter_hide(self, fields=None):
        hide = ['active_l','active_r','vrai']
        res = super(crm, self).fields_get()
        for field in hide:
            res[field]['selectable'] = False
        return res
    
    
    @api.onchange('etat','apport_verse', 'apport_min')
    def onchange_etat_depend_etat(self):
        for r in self:
            if r.bien:
                r.etat_depend_etat = 'option'
                if r.etat == 'option':
                    r.etat_depend_etat = 'option'   
                if r.etat == 'dispo':
                    r.etat_depend_etat = 'dispo'
                if r.apport_verse >= r.apport_min:            
                    if r.etat == 'reserve':
                        r.etat_depend_etat = 'reserve'
            else:
                r.etat_depend_etat = 'dispo'
                
    
    etat_depend_etat = fields.Selection([
        ('dispo', 'Disponible'),
        ('option', 'Option'),
       ('reserve', 'Réservé'),
    ], string='', default="dispo", related='bien.etat_depend_etat', readonly=False)

    
   #partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
        #domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", context="{'default_source_id': source_id, 'default_origine_id': origine_id}")
    
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", context="{'default_origine_id': origine_id}")
    
    
    active_l = fields.Boolean()

    active_r = fields.Boolean()

    vrai = fields.Boolean('vrai', default=True)
    

    @api.onchange('etat_du_bien')
    def _onchangebien(self):
        for r in self:
            if (self.etat_du_bien) == 'option':
                r.active_l = True
            else:
                r.active_l = False

    @api.onchange('etat_du_bien')
    def _onchangebien_reserve(self):
        for r in self:
            if (self.etat_du_bien) == 'reserve':
                r.active_r = True
            else:
                r.active_r = False

    @api.constrains('active_l', 'vrai', 'active_r', 'etat_du_bien')
    def _check_something(self):
        for record in self:
            if record.active_l == record.vrai:
                raise ValidationError("Ce bien est en : %s" % record.etat_du_bien)
            if record.active_r == record.vrai:
                raise ValidationError("Ce bien est : %s" % record.etat_du_bien)


                 
                             
   
    etat_du_bien = fields.Selection([
       ('dispo', 'Disponible'),
        ('option', 'Option'),
        ('reserve', 'Réservé'),
    ], string='Etat du bien', related='bien.etat')

    @api.onchange('etat_du_bien')
    def _check_etat(self):
        for r in self:
             if (r.etat_du_bien) == 'reserve':       
                 return {
                    'warning': {
                    'title': "Ce bien n'est pas disponible",
                    'message': "Veuillez choisir un autre bien svp",
                   },
                    
                 }
             if (r.etat_du_bien) == 'option':       
                  return {
                    'warning': {
                    'title': "Ce bien est en option",
                    'message': "Veuillez choisir un autre bien svp",
                    },
                  }
    
   

  
    type_bien = fields.Many2one(related='bien.type_bien_ids', string="Type de bien", store="True")
    
    name_bien = fields.Char(related='bien.name', string="name bien")



    prix_vente = fields.Float(related='bien.prix_maj', string="prix de vente")

    #projet = fields.Many2one(related='bien.nom_projet_ids', string="Projet")
   
    nom_projet_ids = fields.Many2one('lb.projet', string="Projet", related='bien.nom_projet_ids', readonly=False,  context="{'nom_projet_ids': nom_projet_ids}") 
        
    bien = fields.Many2one('product.template', string="Bien", domain="['&',('nom_projet_ids', '=', nom_projet_ids), ('etat_depend_etat', '=', 'dispo')]")

    pourcentage = fields.Char(default="%")

    remise = fields.Float(string="Remise(%)",  compute='_remise', inverse='_inverseremise', readonly=False, store=True)

    @api.onchange('taux_cooperative')
    def _remise(self):
        for r in self:
            r.remise = r.taux_cooperative

    def _inverseremise(self):
        for r in self:
            r.taux_cooperative = r.remise

    planned_revenue = fields.Float(string="Revenu espéré ", compute='_Revenu', store=True)

    @api.depends('prix_vente', 'remise')
    def _Revenu(self):
        for r in self:
            if r.remise:
                r.planned_revenue = r.prix_vente - (r.prix_vente*r.remise/100)
            else:
                r.planned_revenue = r.prix_vente    
            
    currency_id = fields.Many2one('res.currency')
    
    
    apport_min = fields.Monetary('Apport initial minimum', 'currency_id', defaul=5, compute='_apport')
    
    
    @api.onchange('prix_vente')
    def _apport(self):
        for r in self:
            r.apport_min = r.prix_vente*10/100
    
    
    apport_verse = fields.Monetary('Apport vérsée', 'currency_id', defaul=0)
    
    montant_verse = fields.Monetary('Montant versé', 'currency_id')
  
    dateoftoday1 = fields.Datetime('Date mise à jour', required=False, readonly=False, select=True, compute='_updatedate')
    
    @api.onchange('dateoftoday')
    def _updatedate(self):
        for r in self:
            #r.dateoftoday1 = fields.Datetime('Date current action', required=False, readonly=False, select=True, default = lambda *a: #fields.datetime.now())
            r.dateoftoday1 = fields.Datetime.to_string(datetime.today())

            
    dateoftoday = fields.Datetime('Date de création', required=False, readonly=False, select=True, default=lambda self: fields.datetime.now())
    date_livraison = fields.Date('Date de livraison') 
    date_entree = fields.Date('Date d’entrée')
    #date_creation = fields.Date('Date de création')
    date_depot = fields.Date('Date de dépôt') 
    date_reservation = fields.Datetime('Date de réservation')
    
    mode_financement = fields.Selection(
                   [('appel_fond', 'Appel de fonds'),
                    ('financement_bancaire','financement bancaire'),
                    ('delai_imparti','délai imparti')
                   ],string="Mode de financement", default="delai_imparti")
    

    apporteur = fields.Many2one('res.partner', string="Apporteur d’affaires", domain="[('apporteur_affaires','=','True')]")
    
    nature_apporteur = fields.Many2one(related='apporteur.nature_apporteur_id', string="Nature d'apporteur")
    
    taux_apporteur = fields.Float(related='apporteur.taux_apporteur', string="Taux Nature Apporteur(%)")

    
    mobile_apporteur = fields.Char(string="Téléphone", related='apporteur.phone')
    adresse_apporteur = fields.Char(string="Adresse",related='apporteur.street')

    email_apporteur = fields.Char(related='apporteur.email', string="Email")
    #cin_ou_passeport = fields.Char(string="Code postal",related='apporteur.num_piece_identite')
    
    nom_cooperative = fields.Many2one('res.partner', string='Nom de la Coopérative', related='partner_id.nom_cooperative')
    taux_cooperative = fields.Float('Taux coopérative(%)', related='partner_id.taux_cooperative')

    
    contrat_id = fields.Many2one('lb.contrat', string="Type de contrat")
    
    origine_id = fields.Many2one('lb.origine', string="Moyen", related='partner_id.origine_id' , readonly=False, store="True")
    #source_id = fields.Many2one('lb.source', string="Source", related='partner_id.source_id', readonly=False, store="True")
    
   
   
    #origine_id = fields.Many2one('lb.origine', string="Moyen", related='apporteur.origine_id' , readonly=False)
    #source_id = fields.Many2one('lb.source', string="Source", related='apporteur.source_id', readonly=False)

    
   #etat = fields.Many2one('etat.bien', string= "Etat",compute='_onchange_etat' ) 
    etat = fields.Selection([
        ('dispo', 'Disponible'),
        ('option', 'Option'),
       ('reserve', 'Réservé'),
    ], string='', default="dispo", compute='_onchange_etat')
    
    #   if str(r.date_expiration) >= fields.Date.to_string(date.today()):

    @api.onchange('mode_financement', 'bien', 'date_expiration', 'date_expiration_bancaire', 'apport_min', 'apport_verse')
    def _onchange_etat(self):
        for r in self:
            if r.bien:
                r.etat = 'option'

                #if str(r.date_expiration) >= fields.Datetime.to_string(date.today()):
                if str(r.date_expiration) >= str(r.dateoftoday1):
                    if r.apport_verse >= r.apport_min:              
                        r.etat = 'reserve'
                    else:
                        r.etat = 'option'
                if r.apport_verse < r.apport_min:            
                    if str(r.date_expiration) < str(r.dateoftoday1):
                        r.etat = 'dispo'
                if r.apport_verse >= r.apport_min:            
                    r.etat = 'reserve'           
            else:
                r.etat = 'dispo'
                
                
            
    
    date_order = fields.Datetime('Date current action', required=False, readonly=False, select=True, default=lambda self: fields.datetime.now())
    
    
    #date_jr = fields.datetime(date.today())

    date_debut = fields.Date("Date Aujourdhuit")

    date_expiration = fields.Datetime(string="Date d'expiration", store=True,readonly=False, select=True,
        compute='_get_end_date')

    
    
    duration = fields.Float(default=15, help="Duration in days 15jr")
    
    duration_bancaire = fields.Float(default=45, help="Duration dans 45jr")
    
   
    

    @api.depends('dateoftoday', 'duration', 'duration_bancaire', 'mode_financement')
    def _get_end_date(self):
        for r in self:
            if not (r.dateoftoday and r.duration and r.duration_bancaire):
                r.date_expiration = r.dateoftoday
                continue
            duration = timedelta(days = r.duration, seconds=-1)
            duration_bancaire = timedelta(days=r.duration_bancaire, seconds=-1)
            if str(r.mode_financement) == 'financement_bancaire':
                r.date_expiration = r.dateoftoday + duration_bancaire
            else:
                r.date_expiration = r.dateoftoday + duration
            
            
  
    def house_reminder_email(self):
        for due in self.env['crm.lead'].search([]):
            email_to = []
            if not isinstance(due.date_expiration, bool):
                today = datetime.now().date()
                date_two_days_before = due.date_expiration - timedelta(days=5)
                if due.date_expiration == today:
                    template_id = self.env['ir.model.data'].get_object_reference(
																				  'immobilier',
																				  'email_template_invoice_due_remainder')[1]
                    email_template_obj = self.env['mail.template'].browse(template_id)
                    if template_id:
                        values = email_template_obj.generate_email(due.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date','attachment_ids'])
                        values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email 
                        values['email_to'] = due.email_from
                        values['subject'] = "Remainder about "+ due.name +" due on "+ str(due.date_expiration)
                        values['res_id'] = False
                        values['recipient_ids'] = [(6,0,email_to)]
                        user_id = self.env['res.users'].browse(self.env.context.get('uid'))
                        values['author_id'] = user_id.partner_id.id or self.env.user.partner_id.id
                        msg_id = self.env['mail.mail'].create(values)
                        if msg_id:
                            msg_id.sudo().send()
                    
                elif date_two_days_before == today:
                    template_id = self.env['ir.model.data'].get_object_reference(
																				  'immobilier',
																					'email_template_invoice_before_due_remainder')[1]
                    email_template_obj = self.env['mail.template'].browse(template_id)
                    if template_id:
                        values = email_template_obj.generate_email(due.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date','attachment_ids'])
                        values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email 
                        values['email_to'] = due.user_id.email
                        values['subject'] = "Remainder about "+ due.name +" due on "+ str(due.date_expiration)
                        values['res_id'] = False
                        values['recipient_ids'] = [(6,0,email_to)]
                        user_id = self.env['res.users'].browse(self.env.context.get('uid'))
                        values['author_id'] = user_id.partner_id.id or self.env.user.partner_id.id
                        msg_id = self.env['mail.mail'].create(values)
                        if msg_id:
                         msg_id.sudo().send()
                else:
                    pass						
        return True
    
    
    
    nom_banque_id = fields.Many2one('lb.banque', string="Nom du banquee")

class type_lieu(models.Model):
    _name = 'lb.banque'
    _description = "Nom du banque"
    _rec_name = 'nom_banque'

    nom_banque = fields.Char('Nom du banque')    
    
class type(models.Model):
    _name = "etat.bien"

    etat = fields.Selection([
        ('dispo', 'Disponible'),
        ('option', 'Option'),
        ('reserve', 'Réservé'),
        ]) 
              
    
   
class Contrat(models.Model):
    _name = 'lb.contrat'
    _description = "Contrat"
    _rec_name = 'nom_contrat'
    
    nom_contrat = fields.Char("Nom contrat")

    
    
    
class AccountMove(models.Model):
    _inherit = 'crm.lead'
    
    
    
    duration_send_mail = fields.Float(default=13, help="Duration send mail 2jr before date d'expiration=13jr date crate")

    duration_send_mail_banc = fields.Float(default=35, help="Duration send mail 10jr before date d'expiration=35jr date")

    date_auj = fields.Date(string='Your string', default=datetime.today())

    date_mail = fields.Date(inverse='_set_end_date', compute='_get_end_date_mail')
    
    @api.depends('date_auj', 'duration_send_mail', 'duration_send_mail_banc', 'mode_financement')
    def _get_end_date_mail(self):
        for r in self:
            if not (r.date_auj and r.duration_send_mail and r.duration_send_mail_banc):
                r.date_mail = r.date_auj                   
                continue
            duration_send_mail = timedelta(days = r.duration_send_mail, seconds=-1)
            duration_send_mail_banc = timedelta(days = r.duration_send_mail_banc, seconds=-1)
            if str(r.mode_financement) == 'financement_bancaire':
                r.date_mail = r.date_auj + duration_send_mail_banc
            else:
                r.date_mail = r.date_auj + duration_send_mail
                
        
    due_reminder_date = fields.Date()

 
    def _set_end_date(self):  
        today_date = date.today()
        today_date = str(today_date)
        obj = self.env['crm.lead'].search([('etat','!=',('dispo'))])
        if obj:
            context = self._context
            current_uid = context.get('uid')
            current_login_user = self.env['res.users'].browse(current_uid)
            for invoice in obj:
                invoice.duration_send_mail_banc = (invoice.date_auj - invoice.date_mail).days + 1
                email_to = []
                obj_date = str(invoice.due_reminder_date)
                obj_date_mail = str(invoice.date_mail)
                if obj_date_mail == today_date:
                    email_to.append(invoice.user_id.email)
                    
                    template1 = self.env.ref('immobilier.email_template_edi_crm')
                    if template1:
                        mail_create = template1.send_mail(invoice.id)
                        if mail_create:
                            mail = self.env['mail.mail'].browse(mail_create).send()    
               
                             
    
    
    
    
    duration_send_mail_banc_5d = fields.Float(default=40, help="Duration send mail 5jr before date d'expiration=40jr date create")


    date_mail_5d = fields.Date(inverse='_set_end_date_5day', compute='_get_end_date_mail_5d')
    
    @api.depends('date_auj', 'duration_send_mail_banc_5d', 'mode_financement')
    def _get_end_date_mail_5d(self):
        for r in self:
            if not (r.date_auj and r.duration_send_mail_banc_5d):
                r.date_mail_5d = r.date_auj                   
                continue
            duration_send_mail_banc_5d = timedelta(days = r.duration_send_mail_banc_5d, seconds=-1)
            if str(r.mode_financement) == 'financement_bancaire':
                r.date_mail_5d = r.date_auj + duration_send_mail_banc_5d
            else:
            	r.date_mail_5d = r.date_auj - duration_send_mail_banc_5d  
                
                
    def _set_end_date_5day(self):  
        today_date = date.today()
        today_date = str(today_date)
        obj = self.env['crm.lead'].search([('etat','!=',('dispo'))])
        if obj:
            context = self._context
            current_uid = context.get('uid')
            current_login_user = self.env['res.users'].browse(current_uid)
            for invoice in obj:
                invoice.duration_send_mail_banc_5d = (invoice.date_auj - invoice.date_mail_5d).days + 1
                email_to = []
                obj_date = str(invoice.due_reminder_date)
                obj_date_mail_5d = str(invoice.date_mail_5d)
                if obj_date_mail_5d == today_date:
                    email_to.append(invoice.user_id.email)
                    
                    template1 = self.env.ref('immobilier.email_template_edi_crm_cinq')
                    if template1:
                        mail_create = template1.send_mail(invoice.id)
                        if mail_create:
                            mail = self.env['mail.mail'].browse(mail_create).send()    

                            
    email_company = fields.Char(related='company_id.email', string="Email") 
    
    active_partner = fields.Boolean(related='partner_id.active', compute='_clear_contact')

    
     
    @api.onchange('etat_filter')
    def onchange_inactive_partner(self):
         for r in self:
            if r.bien:
                if r.etat_filter == 'dispo':
                    r.partner_id.active = False
                else:
                    r.partner_id.active = True
                    
     
        
    @api.onchange('etat')
    def onchange_client_partner(self):
        for r in self:
            if r.etat == 'reserve':
                r.partner_id.client = True
            else:
                r.partner_id.client = False
            
        
    etat_filter = fields.Selection([
        ('dispo', 'Disponible'),
        ('option', 'Option'),
       ('reserve', 'Réservé'),
        ('pas_bien', 'pas de bien'),
    ], string='', default="pas_bien")
    
    @api.onchange('etat','apport_verse', 'apport_min')
    def onchange_etat_filterr(self):
        for r in self:
            if r.bien:
                r.etat_filter = 'option'
                if r.etat == 'option':
                    r.etat_filter = 'option'   
                if r.etat == 'dispo':
                    r.etat_filter = 'dispo'
                if r.apport_verse >= r.apport_min:            
                    if r.etat == 'reserve':
                        r.etat_filter = 'reserve'
            else:
                r.etat_filter = 'pas_bien'