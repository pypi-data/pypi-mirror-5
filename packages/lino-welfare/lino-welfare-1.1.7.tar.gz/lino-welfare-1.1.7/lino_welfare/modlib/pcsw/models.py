# -*- coding: UTF-8 -*-
## Copyright 2008-2013 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
Contains PCSW-specific models and tables that have not yet been 
moved into a separate module because they are really very PCSW specific.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import base64
import os
import cgi
import datetime

from django.db import models
from django.db.models import Q
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.exceptions import MultipleObjectsReturned
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.utils.encoding import force_unicode 
from django.utils.functional import lazy

#~ import lino
#~ logger.debug(__file__+' : started')
#~ from django.utils import translation


#~ from lino import reports
from lino import dd
#~ from lino import layouts
#~ from lino.core import perms
#~ from lino.utils import printable
from lino import mixins
#~ from lino import fields
#~ from lino.modlib.users.models import UserLevels
#~ from lino.modlib.uploads.models import UploadsByPerson
#~ from lino.models import get_site_config
from lino.core import dbutils
from lino.core.dbutils import get_field
from lino.core.dbutils import resolve_field
#~ from north import babel
from lino.utils import join_words
from lino.utils.choosers import chooser
from lino.utils import mti
from lino.utils.ranges import isrange
from lino.utils.xmlgen import html as xghtml
from lino.utils import IncompleteDate

from lino.mixins.printable import DirectPrintAction, Printable
#~ from lino.mixins.reminder import ReminderEntry
from lino.core import actions
#~ from lino.core import changes

from lino.modlib.contacts.utils import street2kw
from lino.modlib.contacts import models as contacts

#~ from lino.modlib.notes import models as notes
#~ from lino.modlib.links import models as links
#~ from lino.modlib.uploads import models as uploads
#~ from lino.modlib.cal import models as cal
#~ from lino.modlib.users import models as users
#~ from lino.modlib.countries.models import CountryCity
#~ from lino.modlib.cal.models import DurationUnits, update_reminder
#~ from lino.modlib.properties import models as properties
#~ from lino_welfare.modlib.cv import models as cv
#~ from lino.modlib.contacts.models import Contact
from lino.core.dbutils import resolve_model, UnresolvedModel

households = dd.resolve_app('households')
cal = dd.resolve_app('cal')
properties = dd.resolve_app('properties')
countries = dd.resolve_app('countries')
cv = dd.resolve_app('cv')
uploads = dd.resolve_app('uploads')
users = dd.resolve_app('users')
isip = dd.resolve_app('isip')
#~ from lino_welfare.modlib.isip import models as isip
#~ newcomers = dd.resolve_app('newcomers')
notes = dd.resolve_app('notes')

#~ from lino.utils.ssin import ssin_validator
from lino.utils import ssin

class CivilState(dd.ChoiceList):
    """
    Civil states, using Belgian codes.
    
    """
    required = dd.required(user_level='admin')
    verbose_name = _("Civil state")
    verbose_name_plural = _("Civil states")
    
    @classmethod
    def old2new(cls,old): # was used for migrating to 1.4...
        if old == '1': return cls.single
        if old == '2': return cls.married
        if old == '3': return cls.divorced
        if old == '4': return cls.widowed
        if old == '5': return cls.separated
        return ''

add = CivilState.add_item
add('10', _("Single"),'single')
add('13', _("Single cohabitating"))
add('18', _("Single with child"))
add('20', _("Married"),'married')
add('21', _("Married (living alone)"))
add('22', _("Married (living with another partner)"))
add('30', _("Widowed"),'widowed')
add('33', _("Widow cohabitating"))
add('40', _("Divorced"),'divorced')
add('50', _("Separated"),'separated') # Getrennt von Tisch und Bett / 


#~ '10', 'Célibataire', 'Ongehuwd', 'ledig'
#~ '13', 'Célibataire cohab.', NULL, 'ledig mit zus.', 
#~ '18', 'Célibataire avec enf', NULL, 'ledig mit kind', 
#~ '20', 'Marié', 'Gehuwd', 'verheiratet', 
#~ '21', 'Séparé de fait', NULL, 'verheiratet alleine', 
#~ '22', 'Séparé de fait cohab', NULL, 'verheiratet zus.', 
#~ '30', 'Veuf(ve)', NULL, 'Witwe(r)', 
#~ '33', 'Veuf(ve) cohab.', NULL, 'Witwe(r) zus.', 
#~ '40', 'Divorcé', NULL, 'geschieden', 
#~ '50', 'séparé(e) de corps', NULL, 'von Tisch & Bet get.', 





def card_number_to_picture_file(card_number):
    #~ TODO: handle configurability of card_number_to_picture_file
    return os.path.join(settings.MEDIA_ROOT,'beid',card_number+'.jpg')



# http://en.wikipedia.org/wiki/European_driving_licence

class ResidenceType(dd.ChoiceList):
    """
    Types of registries for the Belgian residence.
    
    """
    verbose_name = _("Residence type")
    
add = ResidenceType.add_item
add('1', _("Registry of citizens"))    # Bevölkerungsregister registre de la population
add('2', _("Registry of foreigners"))  # Fremdenregister        Registre des étrangers      vreemdelingenregister 
add('3', _("Waiting for registry"))    # Warteregister


class BeIdCardTypes(dd.ChoiceList):
    """
    List of Belgian Identification Card Types.
    
    Didn't yet find any official reference document.
    
    The eID applet returns a field `documentType` which contains a numeric code.
    For example 1 is for "Belgian citizen", 6 for "Kids card",...
    
    The eID viewer, when saving a card as xml file, doesn't save these values nowhere, 
    it saves a string equivalent (1 becomes "belgian_citizen", 6 becomes "kids_card", 
    17 becomes "foreigner_f", 16 becomes "foreigner_e_plus",...
    
    Sources:
    | [1] https://securehomes.esat.kuleuven.be/~decockd/wiki/bin/view.cgi/EidForums/ForumEidCards0073
    | [2] `Enum be.fedict.commons.eid.consumer.DocumentType <http://code.google.com/p/eid-applet/source/browse/trunk/eid-applet-service/src/main/java/be/fedict/eid/applet/service/DocumentType.java>`_
    
    """
    required = dd.required(user_level='admin')
    verbose_name = _("eID card type")
    verbose_name_plural = _("eID card types")
    
add = BeIdCardTypes.add_item
add('1',_("Belgian citizen"),"belgian_citizen") 
# ,de=u"Belgischer Staatsbürger",fr=u"Citoyen belge"),
add('6', _("Kids card (< 12 year)"),"kids_card") 
#,de=u"Kind unter 12 Jahren"),

"""
from [1]: 
Johan: A document type of 7 is used for bootstrap cards ? What is a bootstrap card (maybe some kind of test card?) 
Danny: A bootstrap card was an eID card that was used in the early start of the eID card introduction to bootstrap 
the computers at the administration. This type is no longer issued. 
"""

#~ add('8', _("Habilitation")) 
#,fr=u"Habilitation",nl=u"Machtiging")
"""
from [1]: 
Johan: A document type of 8 is used for a “habilitation/machtigings” card ? Is this for refugees or asylum seekers? 
Danny: A habilitation/machtigings card was aimed at civil servants. This type is also no longer used. 
"""

add('11', _("Foreigner card A"),"foreigner_a")
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister - Tijdelijk verblijf",
        #~ fr=u"Certificat d'inscription au registre des étrangers - Séjour temporaire",
        #~ de=u"Ausländerkarte A Bescheinigung der Eintragung im Ausländerregister - Vorübergehender Aufenthalt",
add('12', _("Foreigner card B"),"foreigner_b")
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister",
        #~ fr=u"Certificat d'inscription au registre des étrangers",
        #~ de=u"Ausländerkarte B (Bescheinigung der Eintragung im Ausländerregister)",
add('13', _("Foreigner card C"),"foreigner_c")
        #~ nl=u"Identiteitskaart voor vreemdeling",
        #~ fr=u"Carte d'identité d'étranger",
        #~ de=u"C (Personalausweis für Ausländer)",
add('14', _("Foreigner card D"),"foreigner_d")
        #~ nl=u"EG - langdurig ingezetene",
        #~ fr=u"Résident de longue durée - CE",
        #~ de=u"Daueraufenthalt - EG",
add('15', _("Foreigner card E"),"foreigner_e")
        #~ nl=u"Verklaring van inschrijving",
        #~ fr=u"Attestation d’enregistrement",
        #~ de=u"Anmeldebescheinigung",
add('16', _("Foreigner card E+"),"foreigner_e_plus")
        # Document ter staving van duurzaam verblijf van een EU onderdaan
add('17', _("Foreigner card F"),"foreigner_f")
        #~ nl=u"Verblijfskaart van een familielid van een burger van de Unie",
        #~ fr=u"Carte de séjour de membre de la famille d’un citoyen de l’Union",
        #~ de=u"Aufenthaltskarte für Familienangehörige eines Unionsbürgers",
add('18', _("Foreigner card F+"),"foreigner_f_plus")


class ClientEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
add = ClientEvents.add_item
add('10', _("Coached"),'coached')
add('20', _("Dispense"),'dispense')
add('30', _("Exclusion"),'exclusion')
add('40', _("Note"),'note')
add('50', _("Created"),'created')
add('60', _("Modified"),'modified')
#~ add('20', _("Started"),'started')
#~ add('30', _("Ended"),'ended')

class CoachingEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
add = CoachingEvents.add_item
add('10', _("Started"),'started')
add('20', _("Active"),'active')
add('30', _("Ended"),'ended')





class ImportedFields(object):
    _imported_fields = set()
    
    @classmethod
    def declare_imported_fields(cls,names):
        cls._imported_fields = cls._imported_fields | set(dd.fields_list(cls,names))
        #~ logger.info('20120801 %s.declare_imported_fields() --> %s' % (
            #~ cls,cls._imported_fields))
        
#~ class CpasPartner(dd.Model,mixins.DiffingMixin):
#~ class Partner(contacts.Partner,mixins.DiffingMixin,mixins.CreatedModified):
class Partner(contacts.Partner,mixins.CreatedModified,ImportedFields):
    """
    """
    
    class Meta(contacts.Partner.Meta):
        app_label = 'contacts'
  
    #~ is_active = models.BooleanField(
        #~ verbose_name=_("is active"),default=True,
        #~ help_text = "Only active Persons may be used when creating new operations.")
    
    #~ newcomer = models.BooleanField(
        #~ verbose_name=_("newcomer"),default=False)
    #~ """Means that there's no responsible user for this partner yet. 
    #~ New partners may not be used when creating new operations."""
    
    is_obsolete = models.BooleanField(
        verbose_name=_("obsolete"),default=False,help_text=u"""\
Altfälle sind Partner, deren Stammdaten nicht mehr gepflegt werden und 
für neue Operationen nicht benutzt werden können.""")
    
    activity = models.ForeignKey("pcsw.Activity",
        blank=True,null=True)
    
    bank_account1 = models.CharField(max_length=40,
        blank=True,# null=True,
        verbose_name=_("Bank account 1"))
        
    bank_account2 = models.CharField(max_length=40,
        blank=True,# null=True,
        verbose_name=_("Bank account 2"))
        
    hidden_columns = 'created modified activity bank_account1 bank_account2'
    
    @classmethod
    def on_analyze(cls,site):
        super(Partner,cls).on_analyze(site)
        cls.declare_imported_fields('''
          created modified
          name remarks region zip_code city country 
          street_prefix street street_no street_box 
          addr2
          language 
          phone fax email url
          bank_account1 bank_account2 activity 
          is_obsolete 
          ''')
        if cls is contacts.Partner: # not e.g. on JobProvider who has no own site_setup()
            cls.declare_imported_fields('''
            is_person is_company
            ''')
        
    def disabled_fields(self,ar):
        #~ logger.info("20120731 CpasPartner.disabled_fields()")
        #~ raise Exception("20120731 CpasPartner.disabled_fields()")
        if settings.SITE.is_imported_partner(self):
            return self._imported_fields
        return set()
        
    def disable_delete(self,ar):
        if ar is not None and settings.SITE.is_imported_partner(self):
            return _("Cannot delete companies and persons imported from TIM")
        return super(Partner,self).disable_delete(ar)

    #~ def get_row_permission(self,ar,state,ba):
        #~ if isinstance(ba.action,dd.MergeAction) and settings.SITE.is_imported_partner(self):
            #~ return False
        #~ return super(Partner,self).get_row_permission(ar,state,ba)
        
class Person(Partner,contacts.Person,mixins.Born,Printable):
    """
    Represents a physical person.
    
    """
    
    class Meta(contacts.PersonMixin.Meta):
        app_label = 'contacts'
        verbose_name = _("Person") # :doc:`/tickets/14`
        verbose_name_plural = _("Persons") # :doc:`/tickets/14`
        
    is_client = mti.EnableChild('pcsw.Client',verbose_name=_("is Client"),
        help_text=_("Whether this Person is a Client."))
        
        
    def get_queryset(self):
        return self.model.objects.select_related('country','city')
        
    def get_print_language(self,pm):
        "Used by DirectPrintAction"
        return self.language
        
    @classmethod
    def on_analyze(cls,site):
        super(Person,cls).on_analyze(site)
        cls.declare_imported_fields(
          '''name first_name last_name title birth_date gender is_client
          ''')


dd.update_field(Person,'first_name',blank=False)
dd.update_field(Person,'last_name',blank=False)

class PersonDetail(contacts.PersonDetail):
    bottom_box = """
    activity bank_account1 bank_account2 is_obsolete
    is_client created modified
    remarks contacts.RolesByPerson households.MembersByPerson
    """
  

class Persons(contacts.Persons):
    app_label = 'contacts'
    detail_layout = PersonDetail()
    
    params_panel_hidden = True
    parameters = dict(
        gender = mixins.Genders.field(blank=True,help_text=u"""\
Nur Personen, deren Feld "Geschlecht" ausgefüllt ist und dem angegebenen Wert entspricht."""),
        also_obsolete = models.BooleanField(
            _("Also obsolete data"),
            default=False,help_text=u"""\
Auch Datensätze anzeigen, die als veraltet markiert sind."""))

    params_layout = """
    gender also_obsolete 
    """

    @classmethod
    def get_request_queryset(self,ar):
        qs = super(Persons,self).get_request_queryset(ar)
        if not ar.param_values.also_obsolete:
            qs = qs.filter(is_obsolete=False)
        if ar.param_values.gender:
            qs = qs.filter(gender__exact=ar.param_values.gender)
        return qs
  
    @classmethod
    def get_title_tags(self,ar):
        for t in super(Persons,self).get_title_tags(ar):
            yield t
        if ar.param_values.gender:
            yield unicode(ar.param_values.gender)
        if ar.param_values.also_obsolete:
            yield unicode(self.parameters['also_obsolete'].verbose_name)
      
    
class ClientStates(dd.Workflow):
    required = dd.required(user_level='admin')
    #~ label = _("Client state")
    
    #~ debug_permissions = True
    
    verbose_name_plural = _("Client states")
    
    #~ @classmethod
    #~ def allow_state_newcomer(cls,obj,user):
        #~ if obj.client_state == ClientStates.coached:
            #~ if obj.coachings_by_client.count() > 0:
                #~ return False
        #~ return True
        
        
    @classmethod
    def before_state_change(cls,obj,ar,kw,oldstate,newstate):
      
        #~ if newstate.name == 'refused':
            #~ pass
            
        if newstate.name == 'former':
            qs = obj.coachings_by_client.filter(end_date__isnull=True)
            if qs.count():
                def ok():
                    for co in qs:
                        #~ co.state = CoachingStates.ended
                        co.end_date = datetime.date.today()
                        co.save()
                return ar.confirm(ok,
                    _("This will end %(count)d coachings of %(client)s.") % dict(
                        count=qs.count(),client=unicode(obj)))
                #~ obj.set_change_summary()
                #~ raise actions.Warning(_("You must first fill end_date of existing coachings!"))
            #~ if issubclass(ar.actor,IntegClients):
                #~ ar.confirm(_("This will remove %s from this table.") % unicode(obj))
                #~ kw.update(refresh_all=True)
                
add = ClientStates.add_item
add('10', _("Newcomer"),'newcomer',help_text=u"""\
Klient hat Antrag auf Hilfe eingereicht, 
der jedoch noch nicht genehmigt wurde 
oder es wurde noch kein Sachbearbeiter oder Sozi zur Begleitung zugewiesen.
(TIM: Attribut "N" (Neuantrag) gesetzt)""") # "N" in PAR->Attrib
    #~ required=dict(states=['refused','coached'],user_groups='newcomers'))           
add('20', _("Refused"),'refused',help_text=u"""\
Alle bisherigen Hilfsanträge wurden abgelehnt.
(TIM kennt diesen Aktenzustand nicht)""")
# coached: neither newcomer nor former, IdPrt != "I"
add('30', _("Coached"),'coached',help_text=u"""\
Es gibt mindestens eine Person im ÖSHZ, die sich um die Person kümmert.
(TIM: IdPrt == "S" und Attribut N (Neuantrag) nicht gesetzt)""")

add('50', _("Former"),'former',help_text=u"""\
War mal begleitet, ist es aber jetzt nicht mehr. 
Es existiert keine *aktive* Begleitung.
(TIM: Attribut `W (Warnung bei Auswahl)` oder Partnerart `I (Inaktive)`)""")

#~ add('60', _("Invalid"),'invalid',help_text=u"""\
#~ Klient ist laut TIM weder Ehemalig noch Neuantrag, hat aber keine gültige NISS.""")


#~ class RefuseClient(dd.NotifyingAction,dd.ChangeStateAction):
    #~ label = _("Refuse")
    #~ required = dict(states='newcomer invalid',user_groups='newcomers')
    #~ # help_text = _("Write a refusal note and remove the new client request.")
    
    #~ def get_notify_subject(self,ar,obj,**kw):
        #~ return _("%(client)s has been refused.") % dict(client=obj)
        
class RefusalReasons(dd.ChoiceList):
    pass
    
add = RefusalReasons.add_item
add('10',_("Information request (No coaching needed)"))
add('20',_("PCSW is not competent"))
add('30',_("Client did not return"))
        
class RefuseClient(dd.ChangeStateAction):
    label = _("Refuse")
    #~ required = dict(states='newcomer invalid',user_groups='newcomers')
    required = dict(states='newcomer',user_groups='newcomers')
    
    #~ icon_file = 'flag_blue.png'
    help_text=_("Refuse this newcomer request.")
    
    parameters = dict(
        reason = RefusalReasons.field(),
        remark = dd.RichTextField(_("Remark"),blank=True),
        )
    
    params_layout = dd.Panel("""
    reason
    remark
    """,window_size=(50,15))
    
    #~ def action_param_defaults(self,ar,obj,**kw):
        #~ kw = super(AssignEvent,self).action_param_defaults(ar,obj,**kw)
        #~ kw.update(
            #~ remark=unicode(_("I made up this event for you. %s")) 
                #~ % ar.get_user())
        #~ return kw
    
    
    def unused_run_from_ui(self,obj,ar,**kw):
        obj.refusal_reason = ar.action_param_values.reason
        kw = super(RefuseClient,self).run_from_ui(obj,ar,**kw)
        #~ obj.save()
        #~ kw.update(refresh=True)
        return kw
    
        
    def run_from_ui(self,obj,ar,**kw):
        assert isinstance(obj,Client)
        obj.refusal_reason = ar.action_param_values.reason
        subject = _("%(client)s has been refused.") % dict(client=obj)
        body = unicode(ar.action_param_values.reason)
        if ar.action_param_values.remark:
            body += '\n' + ar.action_param_values.remark
        kw.update(message=subject)
        kw.update(alert=_("Success"))
        kw = super(RefuseClient,self).run_from_ui(obj,ar,**kw)
        #~ self.add_system_note(ar,obj)
        silent = False
        ar.add_system_note(
            obj,
            subject,
            body,
            silent)
        return kw

        
            
    

class Getter(object):
    def __init__(self,query_dict):
        self.query_dict = query_dict
        
    def __getattr__(self,name):
        return self.query_dict.get(name)


#~ from lino.utils.instantiator import lookup_or_create


def card2client(data):
    kw = dict()
    #~ def func(fldname,qname):
        #~ kw[fldname] = data[qname]
    kw.update(national_id=ssin.format_ssin(data['nationalNumber']))
    kw.update(first_name=join_words(
        data['firstName1'],
        data['firstName2'],
        data['firstName3']))
    #~ func('first_name','firstName1')
    kw.update(last_name=data['surname'])
    
    card_number = data['cardNumber']
    
    if data.has_key('picture'):
        fn = card_number_to_picture_file(card_number)
        if os.path.exists(fn):
            logger.warning("Overwriting existing image file %s.",fn)
        fp = file(fn,'wb')
        fp.write(base64.b64decode(data['picture']))
        fp.close()
        #~ print 20121117, repr(data['picture'])
        #~ kw.update(picture_data_encoded=data['picture'])
    
    #~ func('card_valid_from','validityBeginDate')
    #~ func('card_valid_until','validityEndDate')
    #~ func('birth_date','birthDate')
    kw.update(birth_date=IncompleteDate(*settings.SITE.parse_date(data['birthDate'])))
    kw.update(card_valid_from=datetime.date(*settings.SITE.parse_date(data['validityBeginDate'])))
    kw.update(card_valid_until=datetime.date(*settings.SITE.parse_date(data['validityEndDate'])))
    kw.update(card_number=card_number)
    kw.update(card_issuer=data['issuingMunicipality'])
    kw.update(noble_condition=data['nobleCondition'])
    kw.update(street=data['street'])
    kw.update(street_no=data['streetNumber'])
    kw.update(street_box=data['boxNumber'])
    if kw['street'] and not (kw['street_no'] or kw['street_box']):
        kw = street2kw(kw['street'],**kw)
    kw.update(zip_code=data['zipCode'])
    kw.update(birth_place=data['birthLocation'])
    pk = data['country'].upper()
    
    msg1 = "BeIdReadCardToClientAction %s" % kw.get('national_id')

    #~ try:
    country = countries.Country.objects.get(isocode=pk)
    kw.update(country=country)
    #~ except countries.Country.DoesNotExist,e:
    #~ except Exception,e:
        #~ logger.warning("%s : no country with code %r",msg1,pk)
    #~ BE = countries.Country.objects.get(isocode='BE')
    #~ fld = countries.City._meta.get_field()
    kw.update(city=countries.City.lookup_or_create(
        'name',data['municipality'],country=country))
    def sex2gender(sex):
        if sex == 'M' : return mixins.Genders.male
        if sex in 'FVW' : return mixins.Genders.female
        logger.warning("%s : invalid gender code %r",msg1,sex)
    kw.update(gender=sex2gender(data['sex']))
    
    if False:
        def nationality2country(nationality):
            try:
                return countries.Country.objects.get(
                    nationalities__icontains=nationality)
            except countries.Country.DoesNotExist,e:
                logger.warning("%s : no country for nationality %r",
                    msg1,nationality)
            except MultipleObjectsReturned,e:
                logger.warning(
                    "%s : found more than one country for nationality %r",
                    msg1,nationality)
        kw.update(nationality=nationality2country(data['nationality']))
    
    def doctype2cardtype(dt):
        #~ logger.info("20130103 documentType is %r",dt)
        #~ if dt == 1: return BeIdCardTypes.get_by_value("1")
        return BeIdCardTypes.get_by_value(str(dt))
    kw.update(card_type=doctype2cardtype(data['documentType']))
    
    #~ unused = dict()
    #~ unused.update(country=country)
    #~ kw.update(sex=data['sex'])
    #~ unused.update(documentType=data['documentType'])
    #~ logger.info("Unused data: %r", unused)
    return kw
    
    
   
class BeIdReadCardAction(actions.BeIdReadCardAction):
    """
    Read beid card and store the data in a Client instance.
    The base version is a row action (called on a given client).
    """
    label = _("Read eID card")
    sorry_msg = _("Sorry, I cannot handle that case: %s")
    required = dd.required(user_level='admin')
  
    def run_from_ui(self,row,ar,**kw):
        data = ar.request.POST
        attrs = card2client(data)
        logger.info("20130103 BeIdReadCardAction.run_from_ui() : %s -> %s",data,attrs)
        #~ print 20121117, attrs
        #~ ssin = data['nationalNumber']
        #~ ssin = attrs['national_id']
        if row is None:
            qs = Client.objects.filter(national_id=attrs['national_id'])
            if qs.count() > 1:
                return ar.error(self.sorry_msg % 
                    _("There is more than one client with national id %(national_id)s in our database.")
                    % attrs)
            if qs.count() == 0:
                fkw = dict(last_name__iexact=attrs['last_name'],first_name__iexact=attrs['first_name'])
                """
                if a client with same last_name and first_name 
                exists, the user cannot (automatically) create a new client from eid card.
                """
                #~ fkw.update(national_id__isnull=True)
                qs = Client.objects.filter(**fkw)
                if qs.count() == 0:
                    def yes():
                        obj = Client(**attrs)
                        obj.full_clean()
                        obj.save()
                        #~ changes.log_create(ar.request,obj)
                        dd.pre_ui_create.send(obj,request=ar.request)
                        return self.goto_client_response(ar,obj,
                            _("New client %s has been created") % obj)
                    return ar.confirm(yes,
                        _("Create new client %(first_name)s %(last_name)s : Are you sure?") % attrs)
                elif qs.count() > 1:
                    return ar.error(self.sorry_msg % 
                        _("There is more than one client named %(first_name)s %(last_name)s in our database.")
                        % attrs,alert=_("Oops!"))
                        
            assert qs.count() == 1
            row = qs[0]
        return self.process_row(ar,row,attrs)
  
  
    def process_row(self,ar,obj,attrs):
        oldobj = obj
        watcher = dd.ChangeWatcher(obj)
        diffs = []
        for fldname,new in attrs.items():
            fld = get_field(Client,fldname)
            old = getattr(obj,fldname)
            if old != new:
                diffs.append("%s : %s -> %s" % (unicode(fld.verbose_name),dd.obj2str(old),dd.obj2str(new)))
                setattr(obj,fld.name,new)
                
        if len(diffs) == 0:
            #~ return self.no_diffs_response(ar,obj)
            return self.goto_client_response(ar,obj,_("Client %s is up-to-date") % unicode(obj))
            
        msg = unicode(_("Click OK to apply the following changes for %s") % obj)
        msg += ' :<br/>'
        msg += '\n<br/>'.join(diffs)
        #~ print msg
        def apply():
            obj.full_clean()
            obj.save()
            watcher.send_update(ar.request)
            #~ return self.saved_diffs_response(ar,obj)
            return self.goto_client_response(ar,obj,_("%s has been saved.") % dd.obj2unicode(obj))
        def no():
            return self.goto_client_response(ar,oldobj)
        cb = ar.callback(msg)
        cb.add_choice('yes',apply,_("Yes"))
        cb.add_choice('no',no,_("No"))
        #~ cb.add_choice('cancel',no,_("Don't apply"))
        return cb
        
    def goto_client_response(self,ar,obj,msg=None):
        if msg:
            return ar.success(msg,_("Success"),refresh=True)
        return ar.success(msg)
  
            
class FindByBeIdAction(BeIdReadCardAction):
    """
    main menu command: read beid data and find that client.
    """
    single_row = False
          
    #~ label = _("Find by eID card")
    callable_from = tuple() # only explicitely callable

    def goto_client_response(self,ar,obj,msg=None):
        return ar.success(msg,eval_js=ar.instance_handler(obj))
        


class Client(Person):
    """
    A :class:`Client` is a specialized :class:`Person`.
    
    """
    class Meta:
        verbose_name = _("Client") 
        verbose_name_plural = _("Clients") 
        
    workflow_state_field = 'client_state'
        
    remarks2 = models.TextField(_("Remarks (Social Office)"),blank=True) # ,null=True)
    gesdos_id = models.CharField(max_length=40,blank=True,
        #null=True,
        verbose_name=_("Gesdos ID"))
        
    is_cpas = models.BooleanField(verbose_name=_("receives social help"))
    is_senior = models.BooleanField(verbose_name=_("is senior"))
    #~ is_minor = models.BooleanField(verbose_name=_("is minor"))
    group = models.ForeignKey("pcsw.PersonGroup",blank=True,null=True,
        verbose_name=_("Integration phase"))
    #~ is_dsbe = models.BooleanField(verbose_name=_("is coached"),default=False)
    #~ "Indicates whether this Person is coached."
    
    #~ coached_from = models.DateField(
        #~ blank=True,null=True,
        #~ verbose_name=_("Coached from"))
    #~ coached_until = models.DateField(
        #~ blank=True,null=True,
        #~ verbose_name=_("until"))
    
    #~ coach1 = dd.ForeignKey(settings.SITE.user_model,
        #~ blank=True,null=True,
        #~ verbose_name=_("Coach 1"),related_name='coached1')
    #~ coach2 = dd.ForeignKey(settings.SITE.user_model,
        #~ blank=True,null=True,
        #~ verbose_name=_("Coach 2"),related_name='coached2')
        
    birth_place = models.CharField(_("Birth place"),
        max_length=200,
        blank=True,
        #~ null=True
        )
    birth_country = models.ForeignKey("countries.Country",
        blank=True,null=True,
        verbose_name=_("Birth country"),related_name='by_birth_place')
    #~ civil_state = models.CharField(max_length=1,
        #~ blank=True,# null=True,
        #~ verbose_name=_("Civil state"),
        #~ choices=CIVIL_STATE_CHOICES) 
    civil_state = CivilState.field(blank=True) 
    #~ national_id = models.CharField(max_length=200,
    national_id = dd.NullCharField(max_length=200,
        unique=True,
        verbose_name=_("National ID")
        #~ blank=True,verbose_name=_("National ID")
        #~ ,validators=[ssin.ssin_validator] # 20121108
        )
        
    health_insurance = dd.ForeignKey('contacts.Company',blank=True,null=True,
        verbose_name=_("Health insurance"),related_name='health_insurance_for')
    pharmacy = dd.ForeignKey('contacts.Company',blank=True,null=True,
        verbose_name=_("Pharmacy"),related_name='pharmacy_for')
    
    nationality = dd.ForeignKey(countries.Country,
        blank=True,null=True,
        related_name='by_nationality',
        verbose_name=_("Nationality"))
    #~ tim_nr = models.CharField(max_length=10,blank=True,null=True,unique=True,
        #~ verbose_name=_("TIM ID"))
    card_number = models.CharField(max_length=20,
        blank=True,#null=True,
        verbose_name=_("eID card number"))
    card_valid_from = models.DateField(
        blank=True,null=True,
        verbose_name=_("ID card valid from"))
    card_valid_until = models.DateField(
        blank=True,null=True,
        verbose_name=_("until"))
        
    #~ card_type = models.CharField(max_length=20,
        #~ blank=True,# null=True,
        #~ verbose_name=_("eID card type"))
    #~ "The type of the electronic ID card. Imported from TIM."
    
    card_type = BeIdCardTypes.field(blank=True)
    
    card_issuer = models.CharField(max_length=50,
        blank=True,# null=True,
        verbose_name=_("eID card issuer"))
    "The administration who issued this ID card. Imported from TIM."
    
    #~ eid_panel = dd.FieldSet(_("eID card"),
        #~ "card_number card_valid_from card_valid_until card_issuer card_type:20",
        #~ card_number=_("number"),
        #~ card_valid_from=_("valid from"),
        #~ card_valid_until=_("until"),
        #~ card_issuer=_("issued by"),
        #~ card_type=_("eID card type"),
        #~ )
    
    noble_condition = models.CharField(max_length=50,
        blank=True,#null=True,
        verbose_name=_("noble condition"))
    "The eventual noble condition of this person. Imported from TIM."
        
    
    #~ residence_type = models.SmallIntegerField(blank=True,null=True,
        #~ verbose_name=_("Residence type"),
        #~ choices=RESIDENCE_TYPE_CHOICES,
        #~ max_length=1,
        #~ )
    residence_type = ResidenceType.field(blank=True) 
        
    in_belgium_since = models.DateField(_("Lives in Belgium since"),
        blank=True,null=True)
    unemployed_since = models.DateField(_("Seeking work since"),blank=True,null=True)
    #~ work_permit_exempt = models.BooleanField(verbose_name=_("Work permit exemption"))
    needs_residence_permit = models.BooleanField(verbose_name=_("Needs residence permit"))
    needs_work_permit = models.BooleanField(verbose_name=_("Needs work permit"))
    #~ work_permit_valid_until = models.DateField(blank=True,null=True,verbose_name=_("Work permit valid until"))
    work_permit_suspended_until = models.DateField(blank=True,null=True,verbose_name=_("suspended until"))
    aid_type = models.ForeignKey("pcsw.AidType",blank=True,null=True)
        #~ verbose_name=_("aid type"))
        
    income_ag    = models.BooleanField(verbose_name=_("unemployment benefit")) # Arbeitslosengeld
    income_wg    = models.BooleanField(verbose_name=_("waiting pay")) # Wartegeld
    income_kg    = models.BooleanField(verbose_name=_("sickness benefit")) # Krankengeld
    income_rente = models.BooleanField(verbose_name=_("retirement pension")) # Rente
    income_misc  = models.BooleanField(verbose_name=_("other incomes")) # Andere Einkommen
    
    is_seeking = models.BooleanField(_("is seeking work"))
    unavailable_until = models.DateField(blank=True,null=True,verbose_name=_("Unavailable until"))
    unavailable_why = models.CharField(max_length=100,
        blank=True,# null=True,
        verbose_name=_("reason"))
    
    obstacles = models.TextField(_("Obstacles"),blank=True,null=True)
    skills = models.TextField(_("Other skills"),blank=True,null=True)
    job_agents = models.CharField(max_length=100,
        blank=True,# null=True,
        verbose_name=_("Job agents"))
    
    #~ job_office_contact = models.ForeignKey("contacts.Contact",
    #~ job_office_contact = models.ForeignKey("links.Link",
    job_office_contact = models.ForeignKey("contacts.Role",
      blank=True,null=True,
      verbose_name=_("Contact person at local job office"),
      related_name='persons_job_office')
      
    client_state = ClientStates.field(default=ClientStates.newcomer)
    
    refusal_reason = RefusalReasons.field(blank=True)
    
    
    print_eid_content = DirectPrintAction(_("eID sheet"),'eid-content',icon_name='x-tbar-vcard')
    
    read_beid = BeIdReadCardAction()
    find_by_beid  = FindByBeIdAction()
    
    #~ def update_system_note(self,note):
        #~ note.project = self
            


    @classmethod
    def on_analyze(cls,site):
        super(Client,cls).on_analyze(site)
        cls.declare_imported_fields(
          '''remarks2
          zip_code city country street street_no street_box 
          birth_place language 
          phone fax email 
          card_type card_number card_valid_from card_valid_until
          noble_condition card_issuer
          national_id health_insurance pharmacy 
          is_cpas is_senior 
          gesdos_id 
          nationality
          ''') # coach1 

    def disabled_fields(self,ar):
        rv = super(Client,self).disabled_fields(ar)
        if not ar.get_user().profile.newcomers_level:
            rv = rv | set(['broker','faculty','refusal_reason'])
        return rv
        
    def get_queryset(self):
        return self.model.objects.select_related(
            #~ 'country','city','coach1','coach2','nationality')
            'country','city','nationality')
            
    def get_coachings(self,today=None,**flt):
        qs = self.coachings_by_client.filter(**flt)
        if today is not None:
            qs = self.coachings_by_client.filter(only_active_coachings_filter(today))
        return qs
        #~ if qs.count() == 1:
            #~ return qs[0]
        #~ elif qs.count() != 0:
            #~ logger.error("get_primary_coach() found more than 1 primary coachings for %s",self)
        #~ return None
        
        
    
    
    @dd.chooser()
    def job_office_contact_choices(cls):
        sc = settings.SITE.site_config # get_site_config()
        if sc.job_office is not None:
            #~ return sc.job_office.contact_set.all()
            #~ return sc.job_office.rolesbyparent.all()
            return sc.job_office.rolesbycompany.all()
            #~ return links.Link.objects.filter(a=sc.job_office)
        return []
        
    def __unicode__(self):
        #~ return u"%s (%s)" % (self.get_full_name(salutation=False),self.pk)
        return u"%s %s (%s)" % (self.last_name.upper(),self.first_name,self.pk)
        
    def update_owned_instance(self,owned):
        owned.project = self
        super(Client,self).update_owned_instance(owned)

    #~ def full_clean(self,*args,**kw):
        #~ if not isrange(self.coached_from,self.coached_until):
            #~ raise ValidationError(u'Coaching period ends before it started.')
        #~ super(Client,self).full_clean(*args,**kw)
            
    #~ def clean(self):
        #~ if self.job_office_contact: 
            #~ if self.job_office_contact.b == self:
                #~ raise ValidationError(_("Circular reference"))
        #~ super(Person,self).clean()
        
    #~ def card_type_text(self,request):
        #~ if self.card_type:
            #~ s = babeldict_getitem(BEID_CARD_TYPES,self.card_type)
            #~ if s:
                #~ return s
            #~ return _("Unknown card type %r") % self.card_type
        #~ return _("Not specified") # self.card_type
    #~ card_type_text.return_type = dd.DisplayField(_("eID card type"))
        
        
    def full_clean(self,*args,**kw):
        if self.job_office_contact: 
            if self.job_office_contact.person_id == self.id:
                raise ValidationError(_("Circular reference"))
        if False:
            if self.national_id:
                ssin.ssin_validator(self.national_id)
        #~ if not self.national_id:
            #~ self.national_id = str(self.id)
        if False: # Regel deaktiviert seit 20121207
            if self.client_state == ClientStates.coached:
                ssin.ssin_validator(self.national_id)
        super(Client,self).full_clean(*args,**kw)
        
      
    def save(self,*args,**kw):
        super(Client,self).save(*args,**kw)
        self.update_reminders()
        
    def get_primary_coach(self):
        """
        Return the one and only primary coach 
        (or `None` if there's less or more than one).
        """
        qs = self.coachings_by_client.filter(primary=True).distinct()
        if qs.count == 1:
            return qs[0].user
        return None
    
    primary_coach = property(get_primary_coach)
        
    def update_reminders(self):
        """
        Creates or updates automatic tasks controlled directly by this Person.
        """
        #~ user = self.coach2 or self.coach1
        user = self.get_primary_coach()
        if user:
            def f():
                M = cal.DurationUnits.months
                cal.update_reminder(1,self,user,
                  self.card_valid_until,
                  _("eID card expires in 2 months"),2,M)
                cal.update_reminder(2,self,user,
                  self.unavailable_until,
                  _("becomes available again in 1 month"),1,M)
                cal.update_reminder(3,self,user,
                  self.work_permit_suspended_until,
                  _("work permit suspension ends in 1 month"),1,M)
                #~ cal.update_reminder(4,self,user,
                  #~ self.coached_until,
                  #~ _("coaching ends in 1 month"),1,M)
            dbutils.run_with_language(user.language,f)
              
          


    @classmethod
    def get_reminders(model,ui,user,today,back_until):
        q = Q(coach1__exact=user) | Q(coach2__exact=user)
        
        def find_them(fieldname,today,delta,msg,**linkkw):
            filterkw = { fieldname+'__lte' : today + delta }
            if back_until is not None:
                filterkw.update({ 
                    fieldname+'__gte' : back_until
                })
            for obj in model.objects.filter(q,**filterkw).order_by(fieldname):
                linkkw.update(fmt='detail')
                url = ui.get_detail_url(obj,**linkkw)
                html = '<a href="%s">%s</a>&nbsp;: %s' % (url,unicode(obj),cgi.escape(msg))
                yield ReminderEntry(getattr(obj,fieldname),html)
            
        #~ delay = 30
        #~ for obj in model.objects.filter(q,
              #~ card_valid_until__lte=date+datetime.timedelta(days=delay)).order_by('card_valid_until'):
            #~ yield ReminderEntry(obj,obj.card_valid_until,_("eID card expires in %d days") % delay,fmt='detail',tab=3)
        for o in find_them('card_valid_until', today, datetime.timedelta(days=30),
            _("eID card expires"),tab=0):
            yield o
        for o in find_them('unavailable_until', today, datetime.timedelta(days=30),
            _("becomes available again"),tab=1):
            yield o
        for o in find_them('work_permit_suspended_until', today, datetime.timedelta(days=30),
              _("work permit suspension ends"),tab=1):
            yield o
        for o in find_them('coached_until', today, datetime.timedelta(days=30),
            _("coaching ends"),tab=1):
            yield o
            
        
    #~ @dd.displayfield(_("Actions"))
    #~ def read_beid_card(self,ar):
        #~ return '[<a href="javascript:Lino.read_beid_card(%r)">%s</a>]' % (
          #~ str(ar.requesting_panel),unicode(_("Read eID card")))
      
    @dd.virtualfield(dd.HtmlBox())
    def image(self,ar):
        url = self.get_image_url(ar)
        #~ s = '<img src="%s" width="100%%" onclick="window.open(\'%s\')"/>' % (url,url)
        s = '<img src="%s" width="100%%"/>' % url
        s = '<a href="%s" target="_blank">%s</a>' % (url,s)
        return s
        #~ return '<img src="%s" width="120px"/>' % self.get_image_url()
    #~ image.return_type = dd.HtmlBox()

    def get_image_parts(self):
        if self.card_number:
            return ("beid",self.card_number+".jpg")
        return ("pictures","contacts.Person.jpg")
        
    def get_image_url(self,ar):
        #~ return settings.MEDIA_URL + "/".join(self.get_image_parts())
        #~ return ar.ui.media_url(*self.get_image_parts())
        return settings.SITE.build_media_url(*self.get_image_parts())
        
    def get_image_path(self):
        #~ TODO: handle configurability of card_number_to_picture_file
        return os.path.join(settings.MEDIA_ROOT,*self.get_image_parts())
        
    def get_skills_set(self):
        return self.personproperty_set.filter(
          group=settings.SITE.site_config.propgroup_skills)
    skills_set = property(get_skills_set)
    
    def properties_list(self,*prop_ids):
        """
        Yields a list of the :class:`PersonProperty <lino_welfare.modlib.cv.models.PersonProperty>` 
        properties of this person in the specified order.
        If this person has no entry for a 
        requested :class:`Property`, it is simply skipped.
        Used in notes/Note/cv.odt"""
        for pk in prop_ids:
            try:
                yield self.personproperty_set.get(property__id=pk)
            except cv.PersonProperty.DoesNotExist,e:
                pass
        
    def unused_get_property(self,prop_id):
        """used in notes/Note/cv.odt"""
        return self.personproperty_set.get(property__id=prop_id)
        #~ return PersonProperty.objects.get(property_id=prop_id,person=self)
        
        
            
    def overview(self,request):
        def qsfmt(qs):
            s = qs.model._meta.verbose_name_plural + ': '
            if qs.count():
                s += ', '.join([unicode(lk) for lk in qs])
            else:
                s += '<b>%s</b>' % force_unicode(_("not filled in"))
            return force_unicode(s)
        
        lines = []
        #~ lines.append('<div>')
        lines.append(qsfmt(self.languageknowledge_set.all()))
        lines.append(qsfmt(self.study_set.all()))
        lines.append(qsfmt(self.contract_set.all()))
        #~ from django.utils.translation import string_concat
        #~ lines.append('</div>')
        return '<br/>'.join(lines)
    overview.return_type = dd.HtmlBox(_("Overview"))
    
    @dd.displayfield(_("Residence permit"))
    def residence_permit(self,ar):
        kv = dict(type=settings.SITE.site_config.residence_permit_upload_type)
        r = ar.spawn(uploads.UploadsByController,
              master_instance=self,
              known_values=kv)
        return ar.renderer.quick_upload_buttons(r)
        #~ rrr = uploads.UploadsByPerson().request(rr.ui,master_instance=self,known_values=kv)
        #~ return rr.ui.quick_upload_buttons(rrr)
    #~ residence_permit.return_type = dd.DisplayField(_("Residence permit"))
    
    @dd.displayfield(_("Work permit"))
    def work_permit(self,ar):
        kv = dict(type=settings.SITE.site_config.work_permit_upload_type)
        r = ar.spawn(uploads.UploadsByController,
              master_instance=self,
              known_values=kv)
        return ar.renderer.quick_upload_buttons(r)
    #~ work_permit.return_type = dd.DisplayField(_("Work permit"))
    
    @dd.displayfield(_("driving licence"))
    #~ @dd.virtualfield(dd.DisplayField(_("driving licence")))
    def driving_licence(self,ar):
        kv = dict(type=settings.SITE.site_config.driving_licence_upload_type)
        r = ar.spawn(uploads.UploadsByController,
              master_instance=self,known_values=kv)
        return ar.renderer.quick_upload_buttons(r)
    #~ driving_licence.return_type = dd.DisplayField(_("driving licence"))
    
    def get_active_contract(self):
        """
        Return the one and only "active contract" of this client.
        
        If there is exactly one contract (past, active or future), 
        return this one. Otherwise:
        
        - If there's exactly one that ends in the future, 
          return this one.
        
        There might be no active contract today, 
        but one contract in the future *or* one contract in the past.
        
        Or there may be several contracts,
        and only one of them ends in the future.
        
        Otherwise return `None`, meaning that Lino fails 
        to decide which contact must be 
        considerd "active".
        
        """
        
        def the_one_and_only(qs1,qs2):
            if qs1.count() + qs2.count() == 1:
                if qs1.count() == 1: return qs1[0]
                if qs2.count() == 1: return qs2[0]
              
        # past and future
        qs1 = self.isip_contract_set_by_client.all()
        qs2 = self.jobs_contract_set_by_client.all()
        if qs1.count() + qs2.count() == 0: 
            return None
        c = the_one_and_only(qs1,qs2)
        if c is not None: return c
        
        # only present and future contracts
        today = datetime.date.today()
        #~ q1 = Q(applies_from__isnull=True) | Q(applies_from__lte=today)
        #~ q2 = Q(applies_until__isnull=True) | Q(applies_until__gte=today)
        q2 = Q(applies_until__gte=today)
        q3 = Q(date_ended__isnull=True) | Q(date_ended__gte=today)
        #~ flt = Q(q1,q2,q3)
        flt = Q(q2,q3)
        qs1 = self.isip_contract_set_by_client.filter(flt)
        qs2 = self.jobs_contract_set_by_client.filter(flt)
        if qs1.count() + qs2.count() > 0:
            return the_one_and_only(qs1,qs2)
        # there is no "present and future" contract, but more than exactly one,
        # so they are all past: return the most recent contract.
        qs1 = self.isip_contract_set_by_client.order_by('-applies_from')
        qs2 = self.jobs_contract_set_by_client.order_by('-applies_from')
        if qs1.count() == 0: return qs2[0]
        if qs2.count() == 0: return qs1[0]
        if qs2[0].applies_from > qs1[0].applies_from: return qs2[0]
        return qs1[0]
        
        
    @dd.virtualfield(models.DateField(_("Contract starts")))
    def applies_from(obj,ar):
        c = obj.get_active_contract()
        if c is not None:
            return c.applies_from
            
    @dd.virtualfield(models.DateField(_("Contract ends")))
    def applies_until(obj,ar):
        c = obj.get_active_contract()
        if c is not None:
            return c.applies_until

    @dd.displayfield(_("Coaches"))
    def coaches(self,ar):
        today = datetime.date.today()
        period = (today,today)
        items = [unicode(obj.user) for obj in self.get_coachings(period)]
        return ', '.join(items)


    def get_system_note_type(self,ar):
        return settings.SITE.site_config.system_note_type
        
    def get_system_note_recipients(self,ar,silent):
        for u in settings.SITE.user_model.objects.filter(coaching_supervisor=True):
            yield "%s <%s>" % (unicode(u),u.email)
            

    





class PartnerDetail(contacts.PartnerDetail):
    #~ general = contacts.PartnerDetail.main
    #~ main = "general debts.BudgetsByPartner"
    bottom_box = """
    remarks 
    activity bank_account1 bank_account2 is_obsolete
    is_person is_company #is_user is_household created modified 
    """
    #~ def setup_handle(self,h):
        #~ h.general.label = _("General")
    

#~ class Partners(contacts.Partners):
    #~ """
    #~ Base class for Companies and Persons tables,
    #~ *and* for households.Households.
    #~ """
    #~ detail_layout = PartnerDetail()

#~ class AllPartners(contacts.AllPartners,Partners):
    #~ app_label = 'contacts'



class Household(Partner,households.Household):
    """
    for lino_welfare we want to inherit also from Partner
    """
    class Meta(households.Household.Meta):
        app_label = 'households'
        
    #~ @classmethod
    #~ def on_analyze(cls,site):
        #~ super(Household,cls).on_analyze(site)
        #~ cls.declare_imported_fields('type')
          
    def disable_delete(self,ar):
        # skip the is_imported_partner test
        return super(Partner,self).disable_delete(ar)
        

class Company(Partner,contacts.Company):
  
    
    class Meta(contacts.Company.Meta):
        abstract = False
        app_label = 'contacts'
        
    #~ # to be maintaned with ClientContactTypes
    #~ dd.inject_field(Company,'is_health_insurance',models.BooleanField(verbose_name=_("Health insurance"),default=False))
    #~ dd.inject_field(Company,'is_pharmacy',models.BooleanField(verbose_name=_("Pharmacy"),default=False))
    #~ dd.inject_field(Company,'is_attorney',models.BooleanField(verbose_name=_("Attorney"),default=False))
    #~ dd.inject_field(Company,'is_job_office',models.BooleanField(verbose_name=_("Job office"),default=False))
    
    # to be maintaned with ClientContactTypes
    #~ is_health_insurance = models.BooleanField(verbose_name=_("Health insurance"),default=False)
    #~ is_pharmacy = models.BooleanField(verbose_name=_("Pharmacy"),default=False)
    #~ is_attorney = models.BooleanField(verbose_name=_("Attorney"),default=False)
    #~ is_job_office = models.BooleanField(verbose_name=_("Job office"),default=False)
        
    client_contact_type = dd.ForeignKey('pcsw.ClientContactType',blank=True,null=True)
        
        
    @classmethod
    def on_analyze(cls,site):
        #~ if cls.model is None:
            #~ raise Exception("%r.model is None" % cls)
        super(Company,cls).on_analyze(site)
        cls.declare_imported_fields(
            '''name 
            vat_id prefix
            phone fax email 
            bank_account1 bank_account2 activity''')

    # todo: remove hourly_rate after data migration. this is now in Job
    #~ hourly_rate = dd.PriceField(_("hourly rate"),blank=True,null=True)
    
  
    

#~ class CompanyDetail(dd.FormLayout):
class CompanyDetail(contacts.CompanyDetail):
  
    box3 = """
    country region
    city zip_code:10
    street_prefix street:25 street_no street_box
    addr2:40
    """

    box4 = """
    email:40 
    url
    phone
    gsm
    """

    address_box = "box3 box4"

    #~ box5 = """
    #~ remarks 
    #~ is_courseprovider is_jobprovider is_health_insurance is_pharmacy is_attorney is_job_office
    #~ """

    box5 = """
    remarks 
    is_courseprovider is_jobprovider client_contact_type
    """

    bottom_box = "box5 contacts.RolesByCompany"

    intro_box = """
    prefix name id language 
    vat_id:12 activity:20 type:20 #hourly_rate
    bank_account1 bank_account2 is_obsolete
    """

    general = dd.Panel("""
    intro_box
    address_box
    bottom_box
    """,label = _("General"))
    
    notes = "pcsw.NotesByCompany"
    
    main = "general notes"

    #~ def setup_handle(self,lh):
      
        #~ lh.general.label = _("General")
        #~ lh.notes.label = _("Notes")


#~ if settings.SITE.company_model is None:
    #~ raise Exception("settings.SITE.company_model is None")

#~ class Companies(Partners):
    #~ model = settings.SITE.company_model
    #~ detail_layout = CompanyDetail()
        
    #~ order_by = ["name"]
    #~ app_label = 'contacts'
    




class ClientDetail(dd.FormLayout):
    """
    The layout of the detail window of a Client.
    """
    #~ actor = 'contacts.Person'
    
    main = "general status_tab coaching education languages competences jobs contracts history calendar outbox misc"
    
    general = dd.Panel("""
    box1 box2
    box4 image:15 #overview     
    """,label=_("Person"))
    
    box1 = dd.Panel("""
    last_name first_name:15 title:10
    country city zip_code:10
    street_prefix street:25 street_no street_box
    addr2:40
    """,label = _("Address"))
    
    box2 = dd.Panel("""
    id:12 language
    email
    phone fax
    gsm
    """,label = _("Contact"))
    
    box3 = dd.Panel("""
    gender:10 birth_date age:10 civil_state:15 noble_condition 
    birth_country birth_place nationality:15 national_id:15 
    """,label = _("Birth"))
    
    eid_panel = dd.Panel("""
    card_number:12 card_valid_from:12 card_valid_until:12 card_issuer:10 card_type:12
    """,label = _("eID card"))

    box4 = """
    box3
    eid_panel
    created modified
    """


    status = """
    in_belgium_since:15 residence_type gesdos_id 
    bank_account1:12 bank_account2:12 
    job_agents group:16
    """
    
      
    income = """
    aid_type   
    income_ag  income_wg    
    income_kg   income_rente  
    income_misc  
    """
      
    #~ suche = dd.Panel("""
    #~ is_seeking unemployed_since work_permit_suspended_until
    #~ # job_office_contact job_agents
    #~ pcsw.ExclusionsByClient:50x3
    #~ """,label = _("Job search"))
    
    suche = dd.Panel("""
    # job_office_contact job_agents
    pcsw.DispensesByClient:50x3
    pcsw.ExclusionsByClient:50x3
    """)
    
    
      
    papers = dd.Panel("""
    is_seeking unemployed_since work_permit_suspended_until
    needs_residence_permit needs_work_permit 
    residence_permit work_permit driving_licence
    uploads.UploadsByController
    """) # ,label = _("Papers"))
    
    status_tab = dd.Panel("""
    status:55 income:25
    suche:40  papers:40
    """,label=_("Status"))
    
      
    #~ coaching = dd.Panel("""
    #~ group:16 client_state
    #~ # coach1:12 coach2:12 coached_from:12 coached_until:12 
    #~ # health_insurance pharmacy job_office_contact 
    #~ job_agents
    #~ ContactsByClient:40 CoachingsByClient:40
    #~ """,label=_("Coaching"))
    
    coaching = dd.Panel("""
    workflow_buttons
    pcsw.ContactsByClient:40 pcsw.CoachingsByClient:40
    """,label=_("Coaching"))
    
    #~ coaching_left = """
    #~ """
    
    history = dd.Panel("""
    pcsw.NotesByPerson #:60 #pcsw.LinksByPerson:20
    # lino.ChangesByMaster
    """,label = _("History"))
    
    outbox = dd.Panel("""
    outbox.MailsByProject
    postings.PostingsByProject
    """,label = _("Correspondence"))
    
    calendar = dd.Panel("""
    cal.EventsByProject
    cal.TasksByProject
    """,label = _("Calendar"))
    
    misc = dd.Panel("""
    activity client_state refusal_reason
    is_cpas is_senior is_obsolete 
    unavailable_until:15 unavailable_why:30
    remarks:30 remarks2:30 
    contacts.RolesByPerson:20 households.MembersByPerson:40
    # links.LinksToThis:30 links.LinksFromThis:30 
    """,label = _("Miscellaneous"),required=dict(user_level='manager'))
    
    
    education = dd.Panel("""
    jobs.StudiesByPerson 
    jobs.ExperiencesByPerson:40
    """,label = _("Education"))
    
    languages = dd.Panel("""
    cv.LanguageKnowledgesByPerson 
    courses.CourseRequestsByPerson  
    # skills obstacles
    """,label = _("Languages"))
    
    competences = dd.Panel("""
    cv.SkillsByPerson cv.SoftSkillsByPerson  skills
    cv.ObstaclesByPerson obstacles 
    """,label = _("Competences"),required=dict(user_groups='integ'))

    jobs = dd.Panel("""
    jobs.CandidaturesByPerson
    """,label = _("Job Requests"))
      
    contracts = dd.Panel("""
    isip.ContractsByPerson
    jobs.ContractsByPerson
    """,label = _("Contracts"))
    
    #~ def setup_handle(self,lh):
        #~ lh.card_number.label = _("number")
        #~ lh.card_valid_from.label = _("valid from")
        #~ lh.card_valid_until.label = _("valid until")
        #~ lh.card_issuer.label = _("issued by")
        #~ lh.card_type.label = _("eID card type")
    def override_labels(self):
        return dict(card_number = _("number"),
        card_valid_from = _("valid from"),
        card_valid_until = _("valid until"),
        card_issuer = _("issued by"),
        card_type = _("eID card type"))
    
if not settings.SITE.use_eid_jslib:
    ClientDetail.eid_panel.replace('read_beid_card:12 ','')
    
if settings.SITE.is_installed('cbss'):
    ClientDetail.main += ' cbss' 
    ClientDetail.cbss = dd.Panel("""
cbss_identify_person cbss_manage_access cbss_retrieve_ti_groups
cbss_summary
""",label=_("CBSS"),required=dict(user_groups='cbss'))


  
def only_coached_by(qs,user):
    return qs.filter(coachings_by_client__user=user).distinct()
    
def only_coached_on(qs,today,join=None):
    """
    Add a filter to the Queryset `qs` (on model Client) 
    which leaves only the clients that are (or were or will be) coached 
    on the specified date.
    """
    n = 'coachings_by_client__'
    if join: 
        n = join + '__' + n
    return qs.filter(only_active_coachings_filter(today,n)).distinct()

def only_active_coachings_filter(today,prefix=''):
    assert len(today) == 2
    return Q(
        #~ Q(**{n+'__end_date__isnull':False}) | Q(**{n+'__start_date__isnull':False}),
        Q(**{prefix+'end_date__isnull':True})  | Q(**{prefix+'end_date__gte':today[0]}),
        Q(**{prefix+'start_date__lte':today[1]}))
        #~ Q(**{prefix+'start_date__isnull':True}) | Q(**{prefix+'start_date__lte':today}))

def add_coachings_filter(qs,user,today,primary):
    assert today is None or len(today) == 2
    if not (user or today or primary):
        return qs
    flt = Q()
    if today:
        flt &= only_active_coachings_filter(today,'coachings_by_client__')
    if user:
        flt &= Q(coachings_by_client__user=user)
    if primary:
        flt &= Q(coachings_by_client__primary=True)
    return qs.filter(flt).distinct()


def daterange_text(a,b):
    return dd.dtos(a)+"-"+dd.dtos(b)
    
class Clients(Persons):
    #~ debug_permissions = True # '20120925'
    #~ title = _("All Clients")
    #~ title = _("Clients")
    model = Client # settings.SITE.person_model
    params_panel_hidden = True
    
    insert_layout = dd.FormLayout("""
    first_name last_name
    national_id
    gender language
    """,window_size=(60,'auto'))
    
    column_names = "name_column:20 client_state national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type language:10"
    
    detail_layout = ClientDetail()

    parameters = dd.ObservedPeriod(
        aged_from = models.IntegerField(_("Aged from"),
            blank=True,null=True,help_text=u"""\
Nur Klienten, die mindestens so alt sind."""),
        aged_to = models.IntegerField(_("Aged to"),
            blank=True,null=True,help_text=u"""\
Nur Klienten, die höchstens so alt sind."""),
        coached_by = models.ForeignKey(users.User,
            blank=True,null=True,
            verbose_name=_("Coached by"),help_text=u"""\
Nur Klienten, die eine Begleitung mit diesem Benutzer haben."""),
        and_coached_by = models.ForeignKey(users.User,
            blank=True,null=True,
            verbose_name=_("and by"),help_text=u"""\
Nur Klienten, die auch mit diesem Benutzer eine Begleitung haben."""),
        nationality = models.ForeignKey(countries.Country,blank=True,null=True,
            verbose_name=_("Nationality")),
            
        #~ start_date = models.DateField(_("Period from"),
            #~ blank=True,null=True,
            #~ help_text="""Date début de la période observée"""),
        #~ end_date = models.DateField(_("until"),
            #~ blank=True,null=True,
            #~ help_text="""Date fin de la période observée"""),
        observed_event = ClientEvents.field(blank=True,default=ClientEvents.coached),
        only_primary = models.BooleanField(
            _("Only primary clients"),default=False,help_text=u"""\
Nur Klienten, die eine effektive <b>primäre</b> Begleitung haben."""),
        client_state = ClientStates.field(blank=True,help_text=u"""\
Nur Klienten mit diesem Status (Aktenzustand)."""),
        #~ new_since = models.DateField(_("Newly coached since"),blank=True),
        **Persons.parameters)
    params_layout = """
    aged_from aged_to gender nationality also_obsolete 
    client_state coached_by and_coached_by start_date end_date observed_event only_primary 
    """
    
            
      
    @classmethod
    def get_request_queryset(self,ar):
        #~ logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
        qs = super(Clients,self).get_request_queryset(ar)
        #~ if ar.param_values.new_since:
            #~ qs = only_new_since(qs,ar.param_values.new_since)
            
        ce = ar.param_values.observed_event
        if ar.param_values.start_date is None or ar.param_values.end_date is None:
            period = None
        else:
            period = (ar.param_values.start_date, ar.param_values.end_date)
            
        qs = add_coachings_filter(qs,
            ar.param_values.coached_by,
            period,
            ar.param_values.only_primary)
        if ar.param_values.and_coached_by:
            qs = add_coachings_filter(qs,
                ar.param_values.and_coached_by,
                period,
                False)
            
        if period is not None and ce is not None:
            if ce == ClientEvents.coached:
                pass
            elif ce == ClientEvents.dispense:
                qs = qs.filter(
                    dispense__end_date__gte=period[0],
                    dispense__start_date__lte=period[1]).distinct()
            elif ce == ClientEvents.created:
                qs = qs.filter(
                    created__gte=datetime.datetime.combine(period[0],datetime.time()),
                    created__lte=datetime.datetime.combine(period[1],datetime.time()))
                #~ print 20130527, qs.query
            elif ce == ClientEvents.modified:
                qs = qs.filter(
                    modified__gte=datetime.datetime.combine(period[0],datetime.time()),
                    modified__lte=datetime.datetime.combine(period[1],datetime.time()))
            elif ce == ClientEvents.exclusion:
                qs = qs.filter(
                    exclusion__excluded_until__gte=period[0],
                    exclusion__excluded_from__lte=period[1]).distinct()
            elif ce == ClientEvents.note:
                qs = qs.filter(
                    notes_note_set_by_project__date__gte=period[0],
                    notes_note_set_by_project__date__lte=period[1]).distinct()
            else:
                raise Warning(repr(ce))
            
        if ar.param_values.client_state:
            qs = qs.filter(client_state=ar.param_values.client_state)
            
        if ar.param_values.nationality:
            qs = qs.filter(nationality__exact=ar.param_values.nationality)
        today = datetime.date.today()
        if ar.param_values.aged_from:
            min_date = today - datetime.timedelta(days=ar.param_values.aged_from*365)
            qs = qs.filter(birth_date__lte=min_date.strftime("%Y-%m-%d"))
            #~ qs = qs.filter(birth_date__lte=today-datetime.timedelta(days=search.aged_from*365))
        if ar.param_values.aged_to:
            #~ q1 = models.Q(birth_date__isnull=True)
            #~ q2 = models.Q(birth_date__lte=today-datetime.timedelta(days=search.aged_to*365))
            #~ qs = qs.filter(q1|q2)
            max_date = today - datetime.timedelta(days=ar.param_values.aged_to*365)
            qs = qs.filter(birth_date__gte=max_date.strftime("%Y-%m-%d"))
            #~ qs = qs.filter(birth_date__gte=today-datetime.timedelta(days=search.aged_to*365))
        return qs
        

    @classmethod
    def get_title_tags(self,ar):
        for t in super(Clients,self).get_title_tags(ar):
            yield t
        if ar.param_values.aged_from or ar.param_values.aged_to:
            yield unicode(_("Aged %(min)s to %(max)s") % dict(
              min=ar.param_values.aged_from or'...',
              max=ar.param_values.aged_to or '...'))
              
        if ar.param_values.observed_event:
            yield unicode(ar.param_values.observed_event)
            
        if ar.param_values.client_state:
            yield unicode(ar.param_values.client_state)
            
        if ar.param_values.start_date is None or ar.param_values.end_date is None:
            period = None
        else:
            period = daterange_text(ar.param_values.start_date, ar.param_values.end_date)
            
        if ar.param_values.coached_by:
            s = unicode(self.parameters['coached_by'].verbose_name) + ' ' + unicode(ar.param_values.coached_by)
            if ar.param_values.and_coached_by:
                s += " %s %s" % (unicode(_('and')),ar.param_values.and_coached_by)
                
            if period:
                yield s \
                    + _(' on %(date)s') % dict(date=period)
            else:
                yield s
        elif period:
            yield _("Coached %s") % period
        
        if ar.param_values.only_primary:
            #~ yield unicode(_("primary"))
            yield unicode(self.parameters['only_primary'].verbose_name)
            
    
class DebtsClients(Clients):
    #~ Black right-pointing triangle : Unicode number: U+25B6  HTML-code: &#9654;
    #~ Black right-pointing pointer Unicode number: U+25BA HTML-code: &#9658;
    help_text = u"""Wie Kontakte \u25b8 Klienten, aber mit Kolonnen und Filterparametern für Schuldnerberatung."""
    required = dict(user_groups = 'debts')
    params_panel_hidden = True
    title = _("DM Clients")
    order_by = "last_name first_name id".split()
    allow_create = False # see blog/2012/0922
    use_as_default_table = False
    column_names = "name_column:20 national_id:10 gsm:10 address_column email phone:10 id "
    
    @classmethod
    def param_defaults(self,ar,**kw):
        kw = super(DebtsClients,self).param_defaults(ar,**kw)
        kw.update(coached_by=ar.get_user())
        return kw
        
    
class IntegClients(Clients):
    #~ Black right-pointing triangle : Unicode number: U+25B6  HTML-code: &#9654;
    #~ Black right-pointing pointer Unicode number: U+25BA HTML-code: &#9658;
    help_text = u"""Wie Kontakte \u25b8 Klienten, aber mit DSBE-spezifischen Kolonnen und Filterparametern."""
    #~ detail_layout = IntegClientDetail()
    required = dict(user_groups = 'integ')
    params_panel_hidden = True
    title = _("Integration Clients")
    order_by = "last_name first_name id".split()
    allow_create = False # see blog/2012/0922
    use_as_default_table = False
    column_names = "name_column:20 applies_from applies_until national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type language:10"
    
    parameters = dict(
        group = models.ForeignKey("pcsw.PersonGroup",blank=True,null=True,
            verbose_name=_("Integration phase")),
        #~ new_since = models.DateField(_("Coached since"),blank=True,default=amonthago),
        language = dd.ForeignKey(countries.Language,
            verbose_name=_("Language knowledge"),
            blank=True,null=True),
        wanted_property = dd.ForeignKey(properties.Property,
            verbose_name=_("Wanted skill"),
            blank=True,null=True),
        only_active = models.BooleanField(_("Only active clients"),default=False,
          help_text=_("Show only clients in 'active' integration phases")),
        **Clients.parameters)
    #~ params_layout = 'coached_on coached_by group only_active only_primary also_obsolete client_state new_since'
    #~ params_layout = 'coached_on coached_by group only_active only_primary also_obsolete new_since'
    params_layout = """
    client_state coached_by and_coached_by start_date end_date observed_event 
    aged_from aged_to gender nationality also_obsolete 
    language wanted_property group only_active only_primary 
    """
    
    #~ @classmethod
    #~ def get_actor_label(self):
        #~ return self.model._meta.verbose_name_plural
    
    @classmethod
    def param_defaults(self,ar,**kw):
        kw = super(IntegClients,self).param_defaults(ar,**kw)
        kw.update(client_state=ClientStates.coached)
        kw.update(coached_by=ar.get_user())
        #~ # print "20120918 MyClients.param_defaults", kw['coached_by']
        return kw
        
    @classmethod
    def get_request_queryset(self,ar):
        #~ ar.param_values.update(client_state = ClientStates.coached)
        qs = super(IntegClients,self).get_request_queryset(ar)
        if ar.param_values.language:
            qs = qs.filter(
                languageknowledge__language=ar.param_values.language).distinct()
        if ar.param_values.wanted_property:
            qs = qs.filter(
                personproperty__property=ar.param_values.wanted_property).distinct()
                
        if ar.param_values.group:
            qs = qs.filter(group=ar.param_values.group)
        if ar.param_values.only_active:
            qs = qs.filter(group__active=True)
        #~ qs = qs.filter(client_state__in=(ClientStates.coached,ClientStates.official))
        #~ qs = qs.filter(client_state=ClientStates.coached)
        #~ logger.info('20120914 Clients.get_request_queryset --> %d',qs.count())
        return qs
        
    @classmethod
    def get_title_tags(self,ar):
        for t in super(IntegClients,self).get_title_tags(ar):
            yield t
        if ar.param_values.only_active:
            yield unicode(ar.actor.parameters['only_active'].verbose_name)
        if ar.param_values.language:
            yield unicode(ar.actor.parameters['language'].verbose_name) + ' '+unicode(ar.param_values.language)
        if ar.param_values.group:
            yield unicode(ar.param_values.group)
            

class ClientsByNationality(Clients):
    #~ app_label = 'contacts'
    master_key = 'nationality'
    order_by = "city name".split()
    column_names = "city street street_no street_box addr2 name country language *"



#~ class MyClients(IntegClients):
    #~ label = _("Integration Clients")
    #~ # label = _("My clients")
    #~ required = dict(user_groups = 'integ')
    #~ use_as_default_table = False
    
    #~ @classmethod
    #~ def param_defaults(self,ar,**kw):
        #~ kw = super(MyClients,self).param_defaults(ar,**kw)
        #~ kw.update(coached_by=ar.get_user())
        #~ # print "20120918 MyClients.param_defaults", kw['coached_by']
        #~ return kw
        
    
  
#~ class UnusedMyClients(Clients):
    #~ u"""
    #~ Show only Clients attended 
    #~ by the requesting user (or another user, 
    #~ specified via :attr:`lino.ui.requests.URL_PARAMS_SUBST_USER`),
    #~ either as primary or as secondary attendant.
    
    #~ Damit jemand als begleitet gilt, muss mindestens eines der 
    #~ beiden Daten coached_from und coached_until ausgefüllt sein.
    
    #~ """
    #~ required = dict(user_groups = ['integ'])
    #~ use_as_default_table = False
    #~ label = _("My clients")
    #~ column_names = "name_column:20 client_state applies_from applies_until national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type coach1 language:10"
    
    #~ @classmethod
    #~ def get_title(self,rr):
        #~ return _("Clients of %s") % rr.get_user()
        
    #~ @classmethod
    #~ def get_request_queryset(self,ar):
        #~ qs = super(MyClients,self).get_request_queryset(ar)
        #~ u = ar.get_user()
        #~ qs = only_coached_by(qs,u)
        #~ return qs
        

#~ class MyClientsByGroup(MyClients):
    #~ master_key = 'group'
    
    #~ @classmethod
    #~ def get_title(self,rr):
        #~ return _("%(phase)s clients of %(user)s") % dict(
          #~ phase=rr.master_instance, user=rr.get_user())
    
#~ class MyPrimaryClients(MyClients): # "Komplette Akten"
    #~ label = _("Primary clients by coach")
    
    #~ @classmethod
    #~ def get_title(self,rr):
        #~ return _("Primary clients of %s") % rr.master_instance
        
    #~ @classmethod
    #~ def get_request_queryset(self,ar):
        #~ qs = super(MyPrimaryClients,self).get_request_queryset(ar)
        #~ qs = qs.filter(coachings_by_client__primary=True).distinct()
        #~ return qs


#~ class MyActiveClients(MyClients):
  
    #~ @classmethod
    #~ def get_title(self,rr):
        #~ return _("Active clients of %s") % rr.get_user()
        
    #~ @classmethod
    #~ def get_request_queryset(self,rr):
        #~ qs = super(MyActiveClients,self).get_request_queryset(rr)
        #~ qs = qs.filter(group__active=True)
        #~ return qs
  

#~ if True: # dd.is_installed('pcsw'):

#~ from lino.core.dbutils import models_by_abc


  
#~ class InvalidClients(Clients):
class ClientsTest(Clients):
    help_text = _("Table of Clients whose data seems unlogical or inconsistent.")
    required = dict(user_level='manager')
    use_as_default_table = False
    #~ required_user_level = UserLevels.manager
    label = _("Data Test Clients")
    parameters = dict(
      #~ user = dd.ForeignKey(settings.SITE.user_model,blank=True,verbose_name=_("Coached by")),
      #~ only_coached_on = models.DateField(_("Only coached on"),blank=True,default=datetime.date.today),
      #~ today = models.DateField(_("only active on"),blank=True,default=datetime.date.today),
      #~ coached_by = models.ForeignKey(users.User,blank=True,null=True,
          #~ verbose_name=_("Coached by")),
      invalid_niss = models.BooleanField(_("Check NISS validity"),default=True),
      overlapping_contracts = models.BooleanField(_("Check for overlapping contracts"),default=True),
      #~ coached_period = models.BooleanField(_("Check coaching period"),default=True),
      #~ only_my_persons = models.BooleanField(_("Only my persons"),default=True),
      **Clients.parameters)
    params_layout = """
    aged_from aged_to gender also_obsolete
    client_state coached_by and_coached_by start_date end_date observed_event 
    invalid_niss overlapping_contracts only_primary nationality
    """
    
    #~ params_layout = """invalid_niss overlapping_contracts coached_by"""
    #~ params_panel_hidden = False
    column_names = "name_column error_message national_id id"
    
    #~ @classmethod
    #~ def get_request_queryset(self,ar):
        #~ return super(Clients,self).get_request_queryset(ar)
    
    
    @classmethod
    def todo_get_row_by_pk(self,pk):
        """
        This would be to avoid "AttributeError 'Client' object has no attribute 'error_message'"
        after a PUT from GridView.
        One detail is missing: We should change the API to include `ar`.
        But that's not so easy because we have for example 
        lino.ui.extjs3.views.Templates.get
        """
        obj = super(ClientsTest,self).get_row_by_pk(pk)
        if obj is None: 
            return obj
        return list(self.get_data_rows(ar,[obj]))[0]
        
      
    @classmethod
    def get_data_rows(self,ar,qs=None):
        """
        """
        #~ from lino_welfare.modlib.isip.models import OverlappingContractsTest
        #~ qs = Person.objects.all()
        
        if qs is None:
            qs = self.get_request_queryset(ar)
        
        #~ logger.info("Building ClientsTest data rows...")
        #~ for p in qs.order_by('name'):
        for obj in qs:
            messages = []
            if ar.param_values.overlapping_contracts:
                messages += isip.OverlappingContractsTest(obj).check_all()
              
            if ar.param_values.invalid_niss and obj.national_id is not None:
                try:
                    ssin.ssin_validator(obj.national_id)
                except ValidationError,e:
                    messages += e.messages
          
            if messages:
                #~ client.error_message = ';<br/>'.join([cgi.escape(m) for m in messages])
                obj.error_message = ';\n'.join(messages)
                #~ logger.info("%s : %s", p, p.error_message)
                yield obj
                
        #~ logger.info("Building ClientsTest data rows: done")
                
        
    @dd.displayfield(_('Error message'))
    def error_message(self,obj,ar):
        #~ return obj.error_message.replace('\n','<br/>')
        return obj.error_message
        


    
#~ class OverviewClientsByUser(dd.VirtualTable):
class UsersWithClients(dd.VirtualTable):
    """
    A customized overview table.
    """
    #~ debug_permissions = True
    required = dict(user_groups='integ newcomers')
    #~ label = _("Overview Clients By User")
    label = _("Users with their Clients")
    #~ column_defaults = dict(width=8)
    
    slave_grid_format = 'html'    
    
    #~ @classmethod
    #~ def on_analyze(self,site):
        #~ if self.has_handle(site.ui):
        #~ raise Exception("20130302 on_analyze called after handle")
        
    

    @classmethod
    def get_data_rows(self,ar):
        """
        We only want the users who actually have at least one client.
        We store the corresponding request in the user object 
        under the name `my_persons`.
        
        The list displays only integration agents, i.e. users with a nonempty `integ_level`.
        With one subtility: system admins also have a nonempty `integ_level`, 
        but normal users don't want to see them. 
        So we add the rule that only system admins see other system admins.
        
        """
        #~ profiles = [p for p in dd.UserProfiles.items() if p.integ_level]
        u = ar.get_user()
        if u is None or u.profile.level < dd.UserLevels.admin:
            profiles = [p for p in dd.UserProfiles.items() 
                if p.integ_level and p.level < dd.UserLevels.admin]
        else:
            profiles = [p for p in dd.UserProfiles.items() if p.integ_level ]
            #~ qs = qs.exclude(profile__gte=UserLevels.admin)
                  
        qs = users.User.objects.filter(profile__in=profiles)
        for user in qs.order_by('username'):
            #~ r = MyClients.request(ar.ui,subst_user=user)
            r = IntegClients.request(param_values=dict(coached_by=user))
            if r.get_total_count():
                user.my_persons = r
                #~ user._detail_action = users.MySettings.default_action
                yield user
                
    #~ @dd.virtualfield('pcsw.Client.coach1')
    #~ @dd.virtualfield(dd.ForeignKey(settings.SITE.user_model,verbose_name=_("Coach")))
    @dd.virtualfield('pcsw.Coaching.user')
    def user(self,obj,ar):
        return obj
        
    @dd.requestfield(_("Total"))
    def row_total(self,obj,ar):
        return obj.my_persons
        
    @dd.requestfield(_("Primary clients"))
    def primary_clients(self,obj,ar):
        #~ return MyPrimaryClients.request(ar.ui,subst_user=obj)
        #~ return MyClients.request(ar.ui,subst_user=obj,param_values=dict(only_primary=True))
        t = datetime.date.today()
        return IntegClients.request(param_values=dict(
            only_primary=True,coached_by=obj,start_date=t,end_date=t))
        
    @dd.requestfield(_("Active clients"))
    def active_clients(self,obj,ar):
        #~ return MyActiveClients.request(ar.ui,subst_user=obj)
        t = datetime.date.today()
        return IntegClients.request(param_values=dict(
            only_active=True,coached_by=obj,start_date=t,end_date=t))

@dd.receiver(dd.database_connected)
def on_connection_created(sender,**kw):  #~ def on_connection_created(sender=None,**kw):
    """
    Builds columns dynamically from the :class:`PersonGroup` database table.
    Called when kernel setup is done, 
    before the UI handle is being instantiated.
    
    This must also be called by
    """
    self = UsersWithClients
    self.column_names = 'user:10'
    today = datetime.date.today()
    try:
        for pg in PersonGroup.objects.filter(ref_name__isnull=False).order_by('ref_name'):
            def w(pg):
                def func(self,obj,ar):
                    return IntegClients.request(
                        param_values=dict(group=pg,
                            coached_by=obj,start_date=today,end_date=today))
                return func
            vf = dd.RequestField(w(pg),verbose_name=pg.name)
            self.add_virtual_field('G'+pg.ref_name,vf)
            self.column_names += ' ' + vf.name 
    except DatabaseError as e:
        pass # happens e.g. if database isn't yet initialized
        
    self.column_names += ' primary_clients active_clients row_total'
    settings.SITE.resolve_virtual_fields()



#
# PERSON GROUP
#
class PersonGroup(dd.Model):
    name = models.CharField(_("Designation"),max_length=200)
    ref_name = models.CharField(_("Reference name"),max_length=20,blank=True)
    active = models.BooleanField(_("Considered active"),default=True)
    #~ text = models.TextField(_("Description"),blank=True,null=True)
    class Meta:
        verbose_name = _("Integration Phase")
        verbose_name_plural = _("Integration Phases")
    def __unicode__(self):
        return self.name

class PersonGroups(dd.Table):
    help_text = _("Liste des phases d'intégration possibles.")
    model = PersonGroup
    #~ required_user_groups = ['integ']
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager',user_groups='integ')

    order_by = ["ref_name"]

    
    
    

#
# ACTIVITIY (Berufscode)
#
class Activity(dd.Model):
    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
    name = models.CharField(max_length=80)
    lst104 = models.BooleanField(_("Appears in Listing 104"))
    
    def __unicode__(self):
        return unicode(self.name)

class Activities(dd.Table):
    help_text = _("""Liste des "activités" ou "codes profession".""")
    model = Activity
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager')
    #~ label = _('Activities')

#~ class ActivitiesByPerson(Activities):
    #~ master_key = 'activity'

#~ class ActivitiesByCompany(Activities):
    #~ master_key = 'activity'
    

class DispenseReason(dd.BabelNamed,dd.Sequenced):
    class Meta:
        verbose_name = _("Dispense reason")
        verbose_name_plural = _('Dispense reasons')
        
    #~ name = models.CharField(_("designation"),max_length=200)
    #~ 
    #~ def __unicode__(self):
        #~ return unicode(self.name)
        
class DispenseReasons(dd.Table):
    help_text = _("A list of reasons for being dispensed")
    required=dict(user_groups = ['integ'],user_level='manager')
    model = DispenseReason
    column_names = 'seqno name *'
    order_by = ['seqno']

    
class Dispense(dd.Model):
    class Meta:
        verbose_name = _("Dispense")
        verbose_name_plural = _("Dispenses")
    allow_cascaded_delete = ['client']
    client = dd.ForeignKey(Client)
    reason = dd.ForeignKey(DispenseReason,verbose_name=_("Reason"))
    remarks = models.TextField(_("Remark"),blank=True) 
    start_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("Dispensed from"))
    end_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("until"))
    

class Dispenses(dd.Table):
    order_by = ['start_date']
    help_text = _("Liste de dispenses")
    required=dict(user_groups = ['integ'],user_level='manager')
    model = Dispense

class DispensesByClient(Dispenses):
    master_key = 'client'
    column_names = 'start_date end_date reason remarks:10'
    hidden_columns = 'id'
    auto_fit_column_widths = True



class ExclusionType(dd.Model):
    class Meta:
        verbose_name = _("Exclusion Type")
        verbose_name_plural = _('Exclusion Types')
        
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.name)

class ExclusionTypes(dd.Table):
    help_text = _("""Liste des raisons possibles d'arrêter temporairement 
    le paiement d'une aide financière prévue.""")
    #~ required_user_groups = ['integ']
    required = dict(user_level='manager')
    #~ required_user_level = UserLevels.manager
    model = ExclusionType
    #~ label = _('Exclusion Types')
    

class Exclusion(dd.Model):
    class Meta:
        verbose_name = _("exclusion")
        verbose_name_plural = _('exclusions')
        
    person = models.ForeignKey('pcsw.Client')
    type = models.ForeignKey("pcsw.ExclusionType",
        verbose_name=_("Reason"),
        blank=True,null=True)
    excluded_from = models.DateField(blank=True,null=True,
        verbose_name=_("Excluded from"))
    excluded_until = models.DateField(blank=True,null=True,
        verbose_name=_("until"))
    remark = models.CharField(_("Remark"),max_length=200,blank=True)
    
    def __unicode__(self):
        s = unicode(self.type)
        if self.excluded_from: s += ' ' +unicode(self.excluded_from)
        if self.excluded_until: s += '-'+unicode(self.excluded_until)
        return s

class Exclusions(dd.Table):
    required = dd.required(user_level='admin')
    help_text = _("Liste des exclusions.")
  
    #~ required_user_level = UserLevels.manager
    model = Exclusion
    #~ label = _('Exclusions')
    
class ExclusionsByClient(Exclusions):
    required = dd.required(user_groups='integ')
    #~ required_user_level = None
    master_key = 'person'
    column_names = 'excluded_from excluded_until type remark:10'
    auto_fit_column_widths = True



#
# AID TYPES
#
class AidType(dd.BabelNamed):
    class Meta:
        verbose_name = _("aid type")
        verbose_name_plural = _('aid types')

class AidTypes(dd.Table):
    help_text = _("Liste des types d'aide financière.")
    model = AidType
    column_names = 'name *'
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager')



class OverlappingContracts(dd.Table):
    required = dict(user_groups = 'integ')
    model = Person
    use_as_default_table = False
    #~ base_queryset = only_coached_persons(Person.objects.all())
    label = _("Overlapping Contracts")
    #~ def a(self):
        
    
    #~ def get_title(self,rr):
        #~ return _("Primary clients of %s") % rr.master_instance
        
    @classmethod
    def get_request_queryset(self,rr):
        #~ rr.master_instance = rr.get_user()
        qs = super(OverlappingContracts,self).get_request_queryset(rr)
        #~ only_my_persons(qs,rr.get_user())
        #~ qs = only_coached_persons(qs,datetime.date.today())
        qs = only_coached_at(qs,datetime.date.today())
        #~ qs = qs.filter()
        #~ print 20111118, 'get_request_queryset', rr.user, qs.count()
        return qs

class ClientContactType(dd.BabelNamed):
    class Meta:
        verbose_name = _("Client Contact type")
        verbose_name_plural = _("Client Contact types")
        
class ClientContactTypes(dd.Table):
    help_text = _("Liste des types de contacts client.")
    model = ClientContactType
    required = dd.required(user_level='manager')

#~ class ClientContactType(Choice):
  
    #~ def __init__(self,choicelist,value,text,name,companies_table,**kw):
        #~ self.companies_table = companies_table
        #~ super(ClientContactType,self).__init__(choicelist,value,text,name,**kw)
        
#~ class ClientContactTypes(ChoiceList):
    #~ label = _("Client Contact type")
    #~ item_class = ClientContactType
    
#~ class HealthInsurances(Companies):
    #~ label = _("Health insurances")
    #~ known_values = dict(is_health_insurance=True)
#~ class Pharmacies(Companies):
    #~ label = _("Pharmacies")
    #~ known_values = dict(is_pharmacy=True)
#~ class Attorneys(Companies):
    #~ label = _("Attorneys")
    #~ known_values = dict(is_attorney=True)
#~ class JobOffices(Companies):
    #~ label = _("Job offices")
    #~ known_values = dict(is_job_office=True)
    
#~ add = ClientContactTypes.add_item
#~ add('10', _("Health insurance"),'health_insurance',HealthInsurances)
#~ add('20', _("Pharmacy"),        'pharmacy',        Pharmacies)
#~ add('30', _("Attorney"),        'attorney',        Attorneys)
#~ add('40', _("Job office"),      'job_office',      JobOffices)
#~ add('90', _("Other"),           'other',           Companies)


#~ class ClientContact(mixins.ProjectRelated,contacts.CompanyContact):
class ClientContact(contacts.ContactRelated):
    """
    project : the Client
    company : the Company
    contact_person : the Contact person in the Company
    contact_role : the role of the contact person in the Company
    """
    class Meta:
        verbose_name = _("Client Contact")
        verbose_name_plural = _("Client Contacts")
    #~ type = ClientContactTypes.field(blank=True)
    client = dd.ForeignKey(Client)
    type = dd.ForeignKey(ClientContactType,blank=True,null=True)
    remark = models.TextField(_("Remarks"),blank=True) # ,null=True)
    
    @dd.chooser()
    def company_choices(self,type):
        qs = contacts.Companies.request().data_iterator
        if type is not None:  
            qs = qs.filter(client_contact_type=type)
        return qs
        #~ if not type:  
            #~ return contacts.Companies.request().data_iterator
        #~ return contacts.Companies.request(client_contact_type=type).data_iterator
        
dd.update_field(ClientContact,'contact_person',verbose_name=_("Contact person"))
          
    
class ClientContacts(dd.Table):
    required = dd.required(user_level='admin')
    help_text = _("Liste des contacts clients.")
    model = ClientContact
    
class ContactsByClient(ClientContacts):
    required = dd.required()
    master_key = 'client'
    column_names = 'type company contact_person contact_role remark *'
    label = _("Contacts")




#~ class CoachingStates(dd.Workflow):
    #~ """Lifecycle of a :class:`Coaching`."""
    
    #~ @classmethod
    #~ def before_state_change(cls,obj,ar,kw,oldstate,newstate):
        
        #~ if newstate.name == 'ended':
            #~ obj.end_date = datetime.date.today()
        #~ elif newstate.name in ('active','standby'):
            #~ obj.end_date = None
    
#~ add = CoachingStates.add_item
#~ # add('10', _("New"),'new')
#~ # add('10', _("Suggested"),'suggested')
#~ # add('20', _("Refused"),'refused')
#~ # add('30', _("Confirmed"),'confirmed')
#~ add('30', _("Active"),'active')
#~ add('40', _("Standby"),'standby')
#~ add('50', _("Ended"),'ended')

class EndCoaching(dd.ChangeStateAction,dd.NotifyingAction):
    label = _("End coaching")
    help_text = _("User no longer coaches this client.")  
    required = dict(states='active standby',user_groups='integ',owner=True)
        
        
    def get_notify_subject(self,ar,obj,**kw):
        return _("%(client)s no longer coached by %(coach)s") % dict(
            client=obj.client,coach=obj.user)
            
    #~ def action_param_defaults(self,ar,obj,**kw):
        #~ kw = super(EndCoaching,self).action_param_defaults(ar,obj,**kw)
        #~ if obj is not None:
            #~ kw.update(notify_subject=
                #~ _("%(client)s no longer coached by %(coach)s") 
                #~ % dict(client=obj.client,coach=obj.user))
        #~ return kw
        
    #~ def update_system_note_kw(self,ar,kw,obj):
        #~ if obj is not None:
            #~ return kw.update(project=obj.client)
            
          
        
    

# CoachingStates.suggested.set_required(owner=False)
# CoachingStates.refused.add_workflow(_("refuse"),states='suggested standby',owner=True)
# CoachingStates.active.add_workflow(_("accept"),states='suggested',owner=True)
#~ CoachingStates.active.add_workflow(_("Reactivate"),
    #~ states='standby ended',owner=True,
    #~ help_text=_("Client has become active again after having been ended or standby."))
#~ CoachingStates.standby.add_workflow(states='active',owner=True)
#~ CoachingStates.ended.add_workflow(EndCoaching)
# CoachingStates.ended.add_workflow(_("End coaching"),
    # help_text=_("User no longer coaches this client."),
    # states='active standby',user_groups='integ',owner=True,notify=True)

#~ """
#~ CoachingStates.add_transition('suggested','refused',_("Refuse"),owner=True)
#~ CoachingStates.add_transition('suggested','active',_("Accept"),owner=True)
#~ CoachingStates.add_transition('active','standby',_("Standby"),owner=True)
#~ CoachingStates.add_transition('active','ended',_("End coaching"),owner=True)
#~ 
#~ """
    


class CoachingType(dd.BabelNamed):
    class Meta:
        verbose_name = _("Coaching type")
        verbose_name_plural = _('Coaching types')

class CoachingTypes(dd.Table):
    help_text = _("Liste des types d'accompagnement.")
    model = CoachingType
    column_names = 'name *'
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager')

#~ _("Integration"),'integ')     # DSBE
#~ _("General"),'general')       # ASD
#~ _("Debt mediation"),'debts')  # Schuldnerberatung
#~ _("Accounting"),'accounting') # Buchhaltung
#~ _("Human resources"),'human') # Personaldienst
#~ _("Human resources"),'human') # Altenheim
#~ _("Human resources"),'human') # Mosaik
#~ _("Human resources"),'human') # Sekretariat
#~ _("Human resources"),'human') # Häusliche Hilfe
#~ _("Human resources"),'human') # Energiedienst

#~ class CoachingTypes(ChoiceList):
    #~ label = _("Coaching type")
#~ add = CoachingTypes.add_item
#~ add('10', _("Primary coach"),'primary')
#~ add('20', _("Secondary coach"),'secondary')


class CoachingEnding(dd.BabelNamed,dd.Sequenced):
    class Meta:
        verbose_name = _("Reason of termination")
        verbose_name_plural = _('Coaching termination reasons')
        
    #~ name = models.CharField(_("designation"),max_length=200)
    type = dd.ForeignKey(CoachingType,
        blank=True,null=True,
        help_text=_("If not empty, allow this ending only on coachings of specified type."))
    
    #~ def __unicode__(self):
        #~ return unicode(self.name)
        
class CoachingEndings(dd.Table):
    help_text = _("A list of reasons expressing why a coaching was ended")
    required=dict(user_groups = ['integ'],user_level='manager')
    model = CoachingEnding
    column_names = 'seqno name type *'
    order_by = ['seqno']
    detail_layout = """
    id name seqno
    CoachingsByEnding
    """





#~ class Coaching(mixins.UserAuthored,mixins.ProjectRelated):
#~ class Coaching(mixins.UserAuthored,ImportedFields):
class Coaching(dd.Model,ImportedFields):
    """
A Coaching (Begleitung, accompagnement) 
is when a Client is being coached by a User (a social assistant) 
during a given period.
    """
    
    #~ required = dict(user_level='manager')
    class Meta:
        verbose_name = _("Coaching")
        verbose_name_plural = _("Coachings")
        
    user = models.ForeignKey(settings.SITE.user_model,
        verbose_name=_("Coach"),
        related_name="%(app_label)s_%(class)s_set_by_user",
        #~ blank=True,null=True
        )
        
    allow_cascaded_delete = ['client']
    workflow_state_field = 'state'
    
    client = models.ForeignKey(Client,related_name="coachings_by_client")
    start_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("Coached from"))
    end_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("until"))
    #~ state = CoachingStates.field(default=CoachingStates.active)
    #~ type = CoachingTypes.field()
    type = dd.ForeignKey(CoachingType,blank=True,null=True)
    primary = models.BooleanField(_("Primary"),
        help_text=_("""There's at most one primary coach per client. 
Enabling this field will automatically make the other coachings non-primary."""))

    ending = models.ForeignKey(CoachingEnding,
        related_name="%(app_label)s_%(class)s_set",
        blank=True,null=True)

    
    @classmethod
    def on_analyze(cls,site):
        super(Coaching,cls).on_analyze(site)
        #~ cls.declare_imported_fields('''client user primary start_date end_date''')
        cls.declare_imported_fields('''client user primary end_date''')
        
    @dd.chooser()
    def ending_choices(cls,type):
        Q = models.Q
        qs = CoachingEnding.objects.filter(
            Q(type__isnull=True) | Q(type=type))
        return qs.order_by("seqno")
        
    def disabled_fields(self,ar):
        if settings.SITE.is_imported_partner(self.client):
            if self.primary:
                return self._imported_fields
            return ['primary']
        return []
        
    def on_create(self,ar):
        """
        Default value for the `user` field is the requesting user.
        """
        if self.user_id is None:
            u = ar.get_user()
            if u is not None:
                self.user = u
        super(Coaching,self).on_create(ar)
        
    def disable_delete(self,ar):
        if ar is not None and settings.SITE.is_imported_partner(self.client):
            if self.primary:
                return _("Cannot delete companies and persons imported from TIM")
        return super(Coaching,self).disable_delete(ar)
        
    def before_ui_save(self,ar,**kw):
        #~ logger.info("20121011 before_ui_save %s",self)
        super(Coaching,self).before_ui_save(ar,**kw)
        if not self.type:
            self.type = ar.get_user().coaching_type
        if not self.start_date:
            self.start_date = datetime.date.today()
        if self.ending and not self.end_date:
            self.end_date = datetime.date.today()
            
    #~ def update_system_note(self,note):
        #~ note.project = self.client
            
    def __unicode__(self):
        #~ return _("Coaching of %(client)s by %(user)s") % dict(client=self.client,user=self.user)
        #~ return self.user.username+' / '+self.client.first_name+' '+self.client.last_name[0]
        return self.user.username+' / '+self.client.last_name+' '+self.client.first_name[0]
            
    def after_ui_save(self,ar,**kw):
        kw = super(Coaching,self).after_ui_save(ar,**kw)
        if self.primary:
            for c in self.client.coachings_by_client.exclude(id=self.id):
                if c.primary:
                    c.primary = False
                    c.save()
                    kw.update(refresh_all=True)
        return kw
        
    #~ def get_row_permission(self,user,state,ba):
        #~ """
        #~ """
        #~ logger.info("20121011 get_row_permission %s %s",self,ba)
        #~ if isinstance(ba.action,actions.SubmitInsert):
            #~ if not user.coaching_type:
                #~ return False
        #~ return super(Coaching,self).get_row_permission(user,state,ba)
      
      
        
    def full_clean(self,*args,**kw):
        if not isrange(self.start_date,self.end_date):
            raise ValidationError(_("Coaching period ends before it started."))
        if not self.start_date and not self.end_date:
            self.start_date = datetime.date.today()
        if not self.type and self.user:
            self.type = self.user.coaching_type
        super(Coaching,self).full_clean(*args,**kw)
        
    #~ def save(self,*args,**kw):
        #~ super(Coaching,self).save(*args,**kw)
        
    def summary_row(self,ar,**kw):
        return xghtml.E.p(ar.href_to(self.client)," (%s)" % self.state.text)
        
    def get_related_project(self,ar):
        return self.client
        
    def get_system_note_type(self,ar):
        return settings.SITE.site_config.system_note_type
        
    def get_system_note_recipients(self,ar,silent):
        yield "%s <%s>" % (unicode(self.user),self.user.email)
        for u in settings.SITE.user_model.objects.filter(coaching_supervisor=True):
            yield "%s <%s>" % (unicode(u),u.email)
            
#~ dd.update_field(Coaching,'user',verbose_name=_("Coach"))

class Coachings(dd.Table):
    required = dd.required(user_level='admin')
    help_text = _("Liste des accompagnements.")
    model = Coaching
    
    parameters = dd.ObservedPeriod(
        coached_by = models.ForeignKey(users.User,
            blank=True,null=True,
            verbose_name=_("Coached by"),help_text="""Nur Begleitungen dieses Benutzers."""),
        and_coached_by = models.ForeignKey(users.User,
            blank=True,null=True,
            verbose_name=_("and by"),help_text="""... und auch Begleitungen dieses Benutzers."""),
        #~ start_date = models.DateField(_("Period from"),
            #~ help_text="""Date début de la période observée"""),
        #~ end_date = models.DateField(_("until"),
            #~ help_text="""Date fin de la période observée"""),
        observed_event = CoachingEvents.field(blank=True,default=CoachingEvents.active),
        primary_coachings = dd.YesNo.field(_("Primary coachings"),
            blank=True,help_text="""Accompagnements primaires."""),
        coaching_type = models.ForeignKey(CoachingType,
            blank=True,null=True,
            help_text="""Nur Begleitungen dieses Dienstes."""),
        ending = models.ForeignKey(CoachingEnding,
            blank=True,null=True,
            help_text="""Nur Begleitungen mit diesem Beendigungsgrund."""),
        )
    params_layout = """
    start_date end_date observed_event coached_by and_coached_by 
    primary_coachings coaching_type ending 
    """
    params_panel_hidden = True
    
    #~ @classmethod
    #~ def param_defaults(self,ar,**kw):
        #~ kw = super(Coachings,self).param_defaults(ar,**kw)
        #~ D = datetime.date
        #~ kw.update(start_date = D.today())
        #~ kw.update(end_date = D.today())
        #~ return kw
        
        
    @classmethod
    def get_request_queryset(self,ar):
        qs = super(Coachings,self).get_request_queryset(ar)
        coaches = []
        for u in (ar.param_values.coached_by,ar.param_values.and_coached_by):
            if u is not None:
                coaches.append(u)
        if len(coaches):
            qs = qs.filter(user__in=coaches)
            
        ce = ar.param_values.observed_event
        if ar.param_values.start_date is None or ar.param_values.end_date is None:
            period = None
        else:
            period = (ar.param_values.start_date, ar.param_values.end_date)
        if ce is not None and period is not None:
            if ce == CoachingEvents.started:
                qs = qs.filter(start_date__gte=ar.param_values.start_date)
                qs = qs.filter(start_date__lte=ar.param_values.end_date)
            elif ce == CoachingEvents.ended:
                qs = qs.filter(end_date__isnull=False)
                qs = qs.filter(end_date__gte=ar.param_values.start_date)
                qs = qs.filter(end_date__lte=ar.param_values.end_date)
            elif ce == CoachingEvents.active:
                qs = qs.filter(start_date__lte=ar.param_values.end_date)
                qs = qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=ar.param_values.start_date))
                
        if ar.param_values.primary_coachings == dd.YesNo.yes:
            qs = qs.filter(primary=True)
        elif ar.param_values.primary_coachings == dd.YesNo.no:
            qs = qs.filter(primary=False)
        if ar.param_values.coaching_type is not None:
            qs = qs.filter(type=ar.param_values.coaching_type)
        if ar.param_values.ending is not None:
            qs = qs.filter(ending=ar.param_values.ending)
        return qs
        

    @classmethod
    def get_title_tags(self,ar):
        for t in super(Coachings,self).get_title_tags(ar):
            yield t
            
        if ar.param_values.observed_event:
            yield unicode(ar.param_values.observed_event)
            
        if ar.param_values.coached_by:
            s = unicode(self.parameters['coached_by'].verbose_name) + ' ' + unicode(ar.param_values.coached_by)
            if ar.param_values.and_coached_by:
                s += " %s %s" % (unicode(_('and')),ar.param_values.and_coached_by)
            yield s
        
        if ar.param_values.primary_coachings:
            yield unicode(self.parameters['primary_coachings'].verbose_name) + ' ' + unicode(ar.param_values.primary_coachings)
            
    
    @classmethod
    def get_create_permission(self,ar):
        #~ logger.info("20121011 Coachings.get_create_permission()")
        if not ar.get_user().coaching_type:
            return 
        return super(Coachings,self).get_create_permission(ar)
    
    
    

    
class CoachingsByClient(Coachings):
    """
    The :class:`Coachings` table in a :class:`Clients` detail.
    """
    required = dd.required()
    #~ debug_permissions = 20121016
    master_key = 'client'
    order_by = ['start_date']
    column_names = 'start_date end_date user:12 primary type:12 ending id'
    hidden_columns = 'id'
    auto_fit_column_widths = True

class CoachingsByUser(Coachings):
    required = dd.required()
    master_key = 'user'
    column_names = 'start_date end_date client type primary id'

class CoachingsByEnding(Coachings):
    master_key = 'ending'
    
#~ class MyCoachings(Coachings,mixins.ByUser):
    #~ column_names = 'start_date end_date client type primary id'

#~ class MySuggestedCoachings(MyCoachings):
    #~ label = _("Suggested coachings")
    #~ known_values = dict(state=CoachingStates.suggested)






class NotesByPerson(notes.Notes):
    required = dd.required()
    master_key = 'project'
    column_names = "date event_type type subject body user company *"
    order_by = ["-date"]
    #~ debug_permissions = 20120920

    
  
class NotesByCompany(notes.Notes):
    required = dd.required()
    master_key = 'company'
    column_names = "date project event_type type subject body user *"
    order_by = ["-date"]
    

if False:
    
    def customize_siteconfig():
        """
        Injects application-specific fields to :class:`SiteConfig <lino.ui.models.SiteConfig>`.
        """
        
        dd.inject_field('ui.SiteConfig',
            'coachingtype_social',
            models.ForeignKey('pcsw.CoachingType',
                blank=True,null=True,
                help_text="""L'objet qui représente le service social général."""))
        dd.inject_field('ui.SiteConfig',
            'coachingtype_integ',
            models.ForeignKey('pcsw.CoachingType',
                blank=True,null=True,
                help_text="""L'objet qui représente le service insertion."""))

    customize_siteconfig()



MODULE_LABEL = _("PCSW")

def setup_config_menu(site,ui,profile,m): 
    m  = m.add_menu("pcsw",MODULE_LABEL)
    #~ config_pcsw     = cfg.add_menu("pcsw",_("SIS"))
    #~ config_pcsw.add_action(self.modules.pcsw.PersonGroups)
    #~ config_pcsw.add_action(self.modules.pcsw.Activities)
    #~ config_pcsw.add_action(self.modules.pcsw.ExclusionTypes)
    #~ config_pcsw.add_action(self.modules.pcsw.AidTypes)
    m.add_action(PersonGroups)
    m.add_action(Activities)
    m.add_action(ExclusionTypes)
    m.add_action(CoachingTypes)
    m.add_action(CoachingEndings)
    m.add_action(DispenseReasons)
    m.add_action(ClientContactTypes)
    
    
def setup_explorer_menu(site,ui,profile,m):
    m  = m.add_menu("pcsw",MODULE_LABEL)
    m.add_action(Coachings)
    m.add_action(ClientContacts)
    m.add_action(Exclusions)
    #~ m.add_action(PersonSearches)
    m.add_action(CivilState)
    m.add_action(ClientStates)
    m.add_action(BeIdCardTypes)
    

INTEG_MODULE_LABEL = _("Integration")
JOBS_MODULE_LABEL = _("Art.60§7")

#~ def setup_my_menu(site,ui,profile,m): 
def setup_main_menu(site,ui,profile,m): 
    m = m.add_menu("integ",INTEG_MODULE_LABEL)
    m.add_action(IntegClients)
    #~ m.add_action(MyPersonSearches)

dd.add_user_group('integ',INTEG_MODULE_LABEL)
#~ dd.add_user_group('coach',INTEG_MODULE_LABEL)
