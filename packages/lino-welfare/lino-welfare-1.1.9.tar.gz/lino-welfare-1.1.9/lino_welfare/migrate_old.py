# -*- coding: UTF-8 -*-
## Copyright 2011-2012 Luc Saffre
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
The migrations in this module are no longer being used 
but archived here as historic examples.


"""

import datetime
from decimal import Decimal
from django.conf import settings
from lino.core.dbutils import resolve_model
from lino.utils import mti
from lino.utils import dblogger

def install(globals_dict):
    "Backward compat when loading dumpy fixtures created before 1.4.4"
    settings.SITE.install_migrations(globals_dict)


def migrate_from_1_1_16(globals_dict):
    NATIVES = []
    Person = resolve_model("contacts.Person")
    LanguageKnowledge = resolve_model("dsbe.LanguageKnowledge")


    def create_contacts_person(country_id, city_id, name, addr1, street_prefix, street, street_no, street_box, addr2, zip_code, region, language, email, url, phone, gsm, fax, remarks, first_name, last_name, title, id, is_active, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, sex, birth_date, birth_date_circa, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, native_language_id, obstacles, skills, job_agents, job_office_contact_id):
        p = Person(country_id=country_id,city_id=city_id,name=name,addr1=addr1,street_prefix=street_prefix,street=street,street_no=street_no,street_box=street_box,addr2=addr2,zip_code=zip_code,region=region,language=language,email=email,url=url,phone=phone,gsm=gsm,fax=fax,remarks=remarks,first_name=first_name,last_name=last_name,title=title,id=id,is_active=is_active,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,is_senior=is_senior,group_id=group_id,coached_from=coached_from,coached_until=coached_until,coach1_id=coach1_id,coach2_id=coach2_id,sex=sex,birth_date=birth_date,birth_date_circa=birth_date_circa,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,national_id=national_id,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,job_office_contact_id=job_office_contact_id)
        if native_language_id:
            NATIVES.append((native_language_id,p))
        return p

    def after_load():
        for native_language_id,p in NATIVES:
            try:
                lk = p.languageknowledge_set.get(language__id=native_language_id)
            except LanguageKnowledge.DoesNotExist:
                lk = p.languageknowledge_set.create(language_id=native_language_id,native=True)
            else:
                lk.native = True
            lk.save()
  
    globals_dict.update(create_contacts_person=create_contacts_person)
    globals_dict.update(after_load=after_load)
    return '1.1.17'
        
def migrate_from_1_1_17(globals_dict):
  
    from lino.modlib.cal.models import migrate_reminder
    from lino.modlib.jobs.models import Job, Contract, JobProvider, \
      ContractEnding, ExamPolicy, ContractType
    
    Company = resolve_model("contacts.Company")
    Upload = resolve_model("uploads.Upload")
    Link = resolve_model("links.Link")
    Note = resolve_model("notes.Note")
    
    
    def get_or_create_job(provider_id,contract_type_id):
        try:
            return Job.objects.get(provider__id=provider_id,contract_type__id=contract_type_id)
        except Job.DoesNotExist:
            if provider_id is None:
                provider = None
            else:
                try:
                    provider = JobProvider.objects.get(pk=provider_id)
                except JobProvider.DoesNotExist:
                    company = Company.objects.get(pk=provider_id)
                    provider = mti.insert_child(company,JobProvider)
                    provider.save()
            if provider is None:
                name = 'Stelle%s(intern)' % contract_type_id
            else:
                name = 'Stelle%s@%s' % (contract_type_id,provider)
            job = Job(
                provider=provider,
                contract_type_id=contract_type_id,
                name=name
                )
            job.save()
            return job
            
    CONTRACTS = []
    REMINDERS = []
    UPLOADS = []
    
    def create_dsbe_contract(id, user_id, reminder_date, reminder_text, 
        delay_value, delay_type, reminder_done, must_build, person_id, 
        company_id, contact_id, language, type_id, applies_from, 
        applies_until, date_decided, date_issued, duration, regime, 
        schedule, hourly_rate, refund_rate, reference_person, 
        responsibilities, stages, goals, duties_asd, duties_dsbe, 
        duties_company, duties_person, user_asd_id, exam_policy_id, 
        ending_id, date_ended):
        job = get_or_create_job(company_id,type_id)
        obj = Contract(id=id,user_id=user_id,
          #~ reminder_date=reminder_date,
          #~ reminder_text=reminder_text,delay_value=delay_value,
          #~ delay_type=delay_type,reminder_done=reminder_done,
          must_build=must_build,person_id=person_id,
          job=job,
          provider_id=company_id,
          contact_id=contact_id,language=language,type_id=type_id,
          applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,duration=duration,regime=regime,schedule=schedule,hourly_rate=hourly_rate,refund_rate=refund_rate,reference_person=reference_person,responsibilities=responsibilities,stages=stages,goals=goals,duties_asd=duties_asd,duties_dsbe=duties_dsbe,duties_company=duties_company,duties_person=duties_person,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended)
        REMINDERS.append((obj,(reminder_date,reminder_text,delay_value,delay_type,reminder_done)))
        return obj
          
    def delayed_create_dsbe_contract(*args):
        CONTRACTS.append(args)
        
    def create_links_link(id, user_id, reminder_date, reminder_text, delay_value, delay_type, reminder_done, person_id, company_id, type_id, date, url, name):
        obj = Link(id=id,user_id=user_id,
          #~ reminder_date=reminder_date,reminder_text=reminder_text,
          #~ delay_value=delay_value,delay_type=delay_type,
          #~ reminder_done=reminder_done,
          person_id=person_id,company_id=company_id,type_id=type_id,date=date,url=url,name=name)
        REMINDERS.append((obj,(reminder_date,reminder_text,delay_value,delay_type,reminder_done)))
        return obj
        
    def create_notes_note(id, user_id, reminder_date, reminder_text, delay_value, delay_type, reminder_done, must_build, person_id, company_id, date, type_id, event_type_id, subject, body, language):
        obj = Note(id=id,user_id=user_id,
          #~ reminder_date=reminder_date,reminder_text=reminder_text,
          #~ delay_value=delay_value,delay_type=delay_type,
          #~ reminder_done=reminder_done,
          must_build=must_build,person_id=person_id,company_id=company_id,date=date,type_id=type_id,event_type_id=event_type_id,subject=subject,body=body,language=language)
        REMINDERS.append((obj,(reminder_date,reminder_text,delay_value,delay_type,reminder_done)))
        return obj
        
    def create_uploads_upload(id, user_id, owner_type_id, owner_id, reminder_date, reminder_text, delay_value, delay_type, reminder_done, file, mimetype, created, modified, description, type_id):
        obj = Upload(id=id,user_id=user_id,
          owner_type_id=owner_type_id,owner_id=owner_id,
          valid_until=reminder_date,
          #~ reminder_date=reminder_date,reminder_text=reminder_text,
          #~ delay_value=delay_value,delay_type=delay_type,
          #~ reminder_done=reminder_done,
          file=file,mimetype=mimetype,
          created=created,modified=modified,description=description,type_id=type_id)
        #~ REMINDERS.append((obj,(reminder_date,reminder_text,delay_value,delay_type,reminder_done)))
        # must relay the saving of uploads because owner is a generic foreign key 
        # which doesn't fail to save the instance but returns None for the owner if it doesn't yet 
        # exist.
        UPLOADS.append(obj)
        #~ return obj
                        

    def after_load():
        for args in CONTRACTS:
            obj = create_dsbe_contract(*args)
            obj.full_clean()
            obj.save()
        for obj,args in REMINDERS:
            migrate_reminder(obj,*args)
        for obj in UPLOADS:
            obj.save()
            
    globals_dict.update(create_dsbe_contract=delayed_create_dsbe_contract)
    globals_dict.update(Contract=Contract)
    globals_dict.update(ContractEnding=ContractEnding)
    globals_dict.update(ContractType=ContractType)
    globals_dict.update(ExamPolicy=ExamPolicy)
    globals_dict.update(create_uploads_upload=create_uploads_upload)
    globals_dict.update(create_notes_note=create_notes_note)
    globals_dict.update(create_links_link=create_links_link)
    globals_dict.update(after_load=after_load)
    #~ globals_dict.update(create_jobs_contracttype=globals_dict['create_dsbe_contracttype'])
    #~ globals_dict.update(create_jobs_exampolicy=globals_dict['create_dsbe_exampolicy'])
    return '1.2.0'
        
  
def migrate_from_1_2_0(globals_dict):
    return '1.2.1'
  
def migrate_from_1_2_1(globals_dict):
    """
    - rename model contacts.ContactType to contacts.RoleType
    - rename model contacts.Contact to contacts.Role 
      (and field company to parent, person to child)
    - change the id of existing users because User is now subclass of Contact
      and modify SiteConfig.next_partner_id
    - part of module jobs has been split to isip
    """
    
    old_contenttypes = """\
    39;activity;dsbe;activity
    43;aid type;dsbe;aidtype
    31;Attendance;cal;attendance
    67;Attendee;cal;attendee
    68;Attendee Role;cal;attendeerole
    65;calendar;cal;calendar
    8;city;countries;city
    20;Company;contacts;company
    16;company type;contacts;companytype
    18;contact;contacts;contact
    59;Contact Person;contacts;role
    17;contact type;contacts;contacttype
    2;content type;contenttypes;contenttype
    54;Contract;jobs;contract
    53;Contract Ending;jobs;contractending
    51;Contract Type;jobs;contracttype
    58;Contracts Situation;jobs;contractssituation
    7;country;countries;country
    46;Course;dsbe;course
    45;Course Content;dsbe;coursecontent
    42;Course Ending;dsbe;courseending
    44;course provider;dsbe;courseprovider
    47;Course Requests;dsbe;courserequest
    4;Data Control Listing;lino;datacontrollisting
    32;Event;cal;event
    22;Event Type;notes;eventtype
    30;Event Type;cal;eventtype
    23;Event/Note;notes;note
    52;examination policy;jobs;exampolicy
    41;exclusion;dsbe;exclusion
    40;exclusion type;dsbe;exclusiontype
    60;Incoming Mail;mails;inmail
    34;Integration Phase;dsbe;persongroup
    56;Job;jobs;job
    38;job experience;dsbe;jobexperience
    50;Job Provider;jobs;jobprovider
    57;Job Requests;jobs;jobrequest
    55;Job Type;jobs;jobtype
    6;Language;countries;language
    37;language knowledge;dsbe;languageknowledge
    25;link;links;link
    24;link type;links;linktype
    61;mail;mails;mail
    21;Note Type;notes;notetype
    63;Outgoing Mail;mails;outmail
    19;Person;contacts;person
    48;Person Search;dsbe;personsearch
    29;place;cal;place
    12;Property;properties;property
    13;Property;properties;personproperty
    10;Property Choice;properties;propchoice
    11;Property Group;properties;propgroup
    9;Property Type;properties;proptype
    62;Recipient;mails;recipient
    66;recurrence set;cal;recurrenceset
    64;Role Type;contacts;roletype
    3;site config;lino;siteconfig
    36;study or education;dsbe;study
    35;study type;dsbe;studytype
    33;Task;cal;task
    5;Text Field Template;lino;textfieldtemplate
    28;Third Party;thirds;third
    15;Unwanted property;properties;unwantedskill
    27;Upload;uploads;upload
    26;upload type;uploads;uploadtype
    1;User;users;user
    49;wanted language knowledge;dsbe;wantedlanguageknowledge
    14;Wanted property;properties;wantedskill"""
    contenttypes_dict = {}
    for ln in old_contenttypes.splitlines():
        ln = ln.strip()
        if ln:
            a = ln.split(';')
            if len(a) != 4:
                raise Exception("%r : invalid format!" % ln)
            tst = a[2] + '.' + a[3]
            if tst == 'contacts.contacttype':
                a[3] = 'roletype'
            elif tst == 'jobs.exampolicy':
                a[2] = 'isip'
                a[3] = 'contract' 
                """existing data was affected  by the "dpy & contenttypes" bug:
                (Tasks 487,488, 489, 490, 491, 492, 493, 494) had wrongly owner_type 
                exampolicy 
                """
            elif tst == 'jobs.contractending':
                a[2] = 'isip'
            contenttypes_dict[int(a[0])] = (a[2],a[3])
            
    from lino.modlib.isip import models as isip
    from lino.modlib.jobs import models as jobs
    
    Role = resolve_model("contacts.Role")
    RoleType = resolve_model("contacts.RoleType")
    from django.contrib.contenttypes.models import ContentType
    #~ ContentType = resolve_model("contenttypes.ContentType")
    def new_contenttype(old_id):
        label,name = contenttypes_dict.get(old_id)
        try:
            return ContentType.objects.get(app_label=label,model=name).pk
        except ContentType.DoesNotExist:
            raise Exception("No ContentType %s.%s" % (label,name))
    
    
    Event = resolve_model("cal.Event")
    Task = resolve_model("cal.Task")
    Person = resolve_model("contacts.Person")
    Company = resolve_model("contacts.Company")
    #~ Contract = resolve_model("jobs.Contract")
    Job = resolve_model("jobs.Job")
    Link = resolve_model("links.Link")
    SiteConfig = resolve_model("lino.SiteConfig")
    TextFieldTemplate = resolve_model("lino.TextFieldTemplate")
    Note = resolve_model("notes.Note")
    Upload = resolve_model("uploads.Upload")
    User = resolve_model("users.User")
    PersonSearch = resolve_model("dsbe.PersonSearch")
    WantedLanguageKnowledge = resolve_model("dsbe.WantedLanguageKnowledge")
    LanguageKnowledge = resolve_model("dsbe.LanguageKnowledge")
    Study = resolve_model("dsbe.Study")
    PersonProperty = resolve_model("properties.PersonProperty")
    
    globals_dict.update(ExamPolicy = resolve_model("isip.ExamPolicy"))
    globals_dict.update(ContractEnding = resolve_model("isip.ContractEnding"))
    
    #~ ISIP_CTYPES = {}
    #~ JOBS_CTYPES = {}
    CONTRACT_TYPES = {}
    
    
    
    scl = list(globals_dict.get('lino_siteconfig_objects')())
    assert len(scl) == 1
    global new_next_partner_id
    new_next_partner_id = user_id_offset = scl[0].next_partner_id
    def new_user_id(old_id):
        if old_id is None: return None
        global new_next_partner_id
        i = old_id + user_id_offset
        new_next_partner_id = max(new_next_partner_id,i+1)
        return i

    def create_lino_siteconfig(id, default_build_method, site_company_id, job_office_id, propgroup_skills_id, propgroup_softskills_id, propgroup_obstacles_id, residence_permit_upload_type_id, work_permit_upload_type_id, driving_licence_upload_type_id, next_partner_id):
        next_partner_id = new_next_partner_id
        return SiteConfig(id=id,default_build_method=default_build_method,site_company_id=site_company_id,job_office_id=job_office_id,propgroup_skills_id=propgroup_skills_id,propgroup_softskills_id=propgroup_softskills_id,propgroup_obstacles_id=propgroup_obstacles_id,residence_permit_upload_type_id=residence_permit_upload_type_id,work_permit_upload_type_id=work_permit_upload_type_id,driving_licence_upload_type_id=driving_licence_upload_type_id,next_partner_id=next_partner_id)
    globals_dict.update(create_lino_siteconfig=create_lino_siteconfig)

    def create_dsbe_study(id, country_id, city_id, person_id, type_id, content, started, stopped, success, language_id, school, remarks):
        if school is None: school = ''
        if remarks is None: remarks = ''
        if content is None: content = ''
        return Study(id=id,country_id=country_id,city_id=city_id,person_id=person_id,type_id=type_id,content=content,started=started,stopped=stopped,success=success,language_id=language_id,school=school,remarks=remarks)        
    globals_dict.update(create_dsbe_study=create_dsbe_study)
    
    
    def create_properties_personproperty(id, group_id, property_id, value, person_id, remark):
        if remark is None: remark = ''
        return PersonProperty(id=id,group_id=group_id,property_id=property_id,value=value,person_id=person_id,remark=remark)    
    globals_dict.update(create_properties_personproperty=create_properties_personproperty)
        
    
    def create_users_user(id, username, first_name, last_name, email, is_staff, is_expert, is_active, is_superuser, last_login, date_joined):
        if email is None: email = ''
        return User(id=new_user_id(id),username=username,first_name=first_name,last_name=last_name,email=email,is_staff=is_staff,is_expert=is_expert,is_active=is_active,is_superuser=is_superuser,last_login=last_login,date_joined=date_joined)
    globals_dict.update(create_users_user=create_users_user)
    
    def create_uploads_upload(id, user_id, owner_type_id, owner_id, file, mimetype, created, modified, description, type_id, valid_until):
        if description is None: description = ''
        owner_type_id = new_contenttype(owner_type_id)
        return Upload(id=id,user_id=new_user_id(user_id),owner_type_id=owner_type_id,owner_id=owner_id,file=file,mimetype=mimetype,created=created,modified=modified,description=description,type_id=type_id,valid_until=valid_until)
    globals_dict.update(create_uploads_upload=create_uploads_upload)
    
    def create_notes_note(id, user_id, must_build, person_id, company_id, date, type_id, event_type_id, subject, body, language):
        if subject is None: subject = ''
        return Note(id=id,user_id=new_user_id(user_id),must_build=must_build,person_id=person_id,company_id=company_id,date=date,type_id=type_id,event_type_id=event_type_id,subject=subject,body=body,language=language)
    globals_dict.update(create_notes_note=create_notes_note)
    
    def create_contacts_contacttype(id, name, name_fr, name_en):
        #~ return ContactType(id=id,name=name,name_fr=name_fr,name_en=name_en)
        return RoleType(id=id,name=name,name_fr=name_fr,name_en=name_en)
    globals_dict.update(create_contacts_contacttype=create_contacts_contacttype)
    
    def create_lino_textfieldtemplate(id, user_id, name, description, text):
        return TextFieldTemplate(id=id,user_id=new_user_id(user_id),name=name,description=description,text=text)
    globals_dict.update(create_lino_textfieldtemplate=create_lino_textfieldtemplate)
    
    def create_links_link(id, user_id, person_id, company_id, type_id, date, url, name):
        return Link(id=id,user_id=new_user_id(user_id),person_id=person_id,company_id=company_id,type_id=type_id,date=date,url=url,name=name)
    globals_dict.update(create_links_link=create_links_link)
    
    def create_jobs_contract(id, user_id, must_build, person_id, provider_id, contact_id, language, job_id, type_id, applies_from, applies_until, date_decided, date_issued, duration, regime, schedule, hourly_rate, refund_rate, reference_person, responsibilities, stages, goals, duties_asd, duties_dsbe, duties_company, duties_person, user_asd_id, exam_policy_id, ending_id, date_ended):
        if regime is None: regime = ''
        if schedule is None: schedule = ''
        if refund_rate is None: refund_rate = ''
        if reference_person is None: reference_person = ''
        user_asd_id = new_user_id(user_asd_id)
        ctype = CONTRACT_TYPES.get(type_id)
        if ctype.name.startswith('VSE'):
            #~ type_id = ISIP_CTYPES.get(type_id).pk
            return isip.Contract(id=id,user_id=new_user_id(user_id),
              must_build=must_build,person_id=person_id,
              company_id=provider_id,contact_id=contact_id,
              language=language,
              type_id=type_id,applies_from=applies_from,applies_until=applies_until,
              date_decided=date_decided,date_issued=date_issued,
              stages=stages,goals=goals,duties_asd=duties_asd,
              duties_dsbe=duties_dsbe,duties_company=duties_company,
              duties_person=duties_person,user_asd_id=user_asd_id,
              exam_policy_id=exam_policy_id,
              ending_id=ending_id,date_ended=date_ended)
        else:
            #~ type_id = JOBS_CTYPES.get(type_id).pk
            return jobs.Contract(id=id,user_id=new_user_id(user_id),must_build=must_build,
              person_id=person_id,provider_id=provider_id,
              contact_id=contact_id,language=language,job_id=job_id,
              type_id=type_id,applies_from=applies_from,applies_until=applies_until,
              date_decided=date_decided,date_issued=date_issued,
              duration=duration,regime=regime,schedule=schedule,hourly_rate=hourly_rate,
              refund_rate=refund_rate,reference_person=reference_person,
              responsibilities=responsibilities,
              #~ stages=stages,goals=goals,duties_asd=duties_asd,duties_dsbe=duties_dsbe,
              #~ duties_company=duties_company,duties_person=duties_person,
              user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,
              ending_id=ending_id,date_ended=date_ended)
    globals_dict.update(create_jobs_contract=create_jobs_contract)
    
    def create_dsbe_personsearch(id, user_id, title, aged_from, aged_to, sex, only_my_persons, coached_by_id, period_from, period_until):
        user_id = new_user_id(user_id)
        if sex is None: sex = ''
        coached_by_id = new_user_id(coached_by_id)
        return PersonSearch(id=id,user_id=user_id,title=title,aged_from=aged_from,aged_to=aged_to,sex=sex,only_my_persons=only_my_persons,coached_by_id=coached_by_id,period_from=period_from,period_until=period_until)
    globals_dict.update(create_dsbe_personsearch=create_dsbe_personsearch)
    
    def create_contacts_company(country_id, city_id, name, addr1, street_prefix, street, street_no, street_box, addr2, zip_code, region, language, email, url, phone, gsm, fax, remarks, vat_id, type_id, id, is_active, activity_id, bank_account1, bank_account2, prefix, hourly_rate):
        if email is None: email = ''
        if remarks is None: remarks = ''
        if bank_account1 is None: bank_account1 = ''
        if bank_account2 is None: bank_account2 = ''
        return Company(country_id=country_id,city_id=city_id,name=name,addr1=addr1,street_prefix=street_prefix,street=street,street_no=street_no,street_box=street_box,addr2=addr2,zip_code=zip_code,region=region,language=language,email=email,url=url,phone=phone,gsm=gsm,fax=fax,remarks=remarks,vat_id=vat_id,type_id=type_id,id=id,is_active=is_active,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,prefix=prefix,hourly_rate=hourly_rate)    
    globals_dict.update(create_contacts_company=create_contacts_company)

    def create_contacts_person(country_id, city_id, name, addr1, street_prefix, street, street_no, street_box, addr2, zip_code, region, language, email, url, phone, gsm, fax, remarks, first_name, last_name, title, sex, id, is_active, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, birth_date, birth_date_circa, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, obstacles, skills, job_agents, job_office_contact_id):
        if email is None: email = ''
        if remarks is None: remarks = ''
        if remarks2 is None: remarks2 = ''
        if bank_account1 is None: bank_account1 = ''
        if bank_account2 is None: bank_account2 = ''
        if birth_place is None: birth_place = ''
        if civil_state is None: civil_state = ''
        if sex is None: sex = ''
        if gesdos_id is None: gesdos_id = ''
        if card_number is None: card_number = ''
        if card_type is None: card_type = ''
        if card_issuer is None: card_issuer = ''
        if noble_condition is None: noble_condition = ''
        if unavailable_why is None: unavailable_why = ''
        if job_agents is None: job_agents = ''
        coach1_id = new_user_id(coach1_id)
        coach2_id = new_user_id(coach2_id)
        return Person(country_id=country_id,city_id=city_id,name=name,addr1=addr1,street_prefix=street_prefix,street=street,street_no=street_no,street_box=street_box,addr2=addr2,zip_code=zip_code,region=region,language=language,email=email,url=url,phone=phone,gsm=gsm,fax=fax,remarks=remarks,first_name=first_name,last_name=last_name,title=title,sex=sex,
          # Person pk is now contact_ptr_id, and FakeDeserializedObject.try_save tests this to decided whether
          # it can defer the save 
          id=id,
          contact_ptr_id=id,
          is_active=is_active,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,is_senior=is_senior,group_id=group_id,coached_from=coached_from,coached_until=coached_until,coach1_id=coach1_id,coach2_id=coach2_id,birth_date=birth_date,birth_date_circa=birth_date_circa,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,national_id=national_id,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,job_office_contact_id=job_office_contact_id)
    globals_dict.update(create_contacts_person=create_contacts_person)
    
    def create_contacts_contact(id, person_id, company_id, type_id):
        #~ return Contact(id=id,person_id=person_id,company_id=company_id,type_id=type_id)
        if not company_id: return None # field was nullable
        return Role(id=id,child_id=person_id,parent_id=company_id,type_id=type_id)
    globals_dict.update(create_contacts_contact=create_contacts_contact)
    
    def create_dsbe_wantedlanguageknowledge(id, search_id, language_id, spoken, written):
        if spoken is None: spoken = ''
        if written is None: written = ''
        return WantedLanguageKnowledge(id=id,search_id=search_id,language_id=language_id,spoken=spoken,written=written)
    globals_dict.update(create_dsbe_wantedlanguageknowledge=create_dsbe_wantedlanguageknowledge)
    
    def create_dsbe_languageknowledge(id, person_id, language_id, spoken, written, native, cef_level):
        if spoken is None: spoken = ''
        if written is None: written = ''
        if cef_level is None: cef_level = ''
        return LanguageKnowledge(id=id,person_id=person_id,language_id=language_id,spoken=spoken,written=written,native=native,cef_level=cef_level)
    globals_dict.update(create_dsbe_languageknowledge=create_dsbe_languageknowledge)
    
    def create_cal_task(id, user_id, created, modified, owner_type_id, owner_id, person_id, company_id, start_date, start_time, summary, description, access_class, sequence, alarm_value, alarm_unit, dt_alarm, due_date, due_time, done, percent, status, auto_type):
        owner_type_id = new_contenttype(owner_type_id)
        user_id = new_user_id(user_id)
        if access_class is None: access_class = ''
        if alarm_unit is None: alarm_unit = ''
        if summary is None: summary = ''
        if status is None: status = ''
        if person_id:
            project_id=person_id
            if company_id:
                dblogger.warning("create_cal_task looses company_id %s for task #%",company_id,id)
        else:
            project_id=company_id
        return Task(id=id,user_id=user_id,created=created,modified=modified,owner_type_id=owner_type_id,owner_id=owner_id,project_id=project_id,start_date=start_date,start_time=start_time,summary=summary,description=description,access_class=access_class,sequence=sequence,alarm_value=alarm_value,alarm_unit=alarm_unit,dt_alarm=dt_alarm,due_date=due_date,due_time=due_time,done=done,percent=percent,status=status,auto_type=auto_type)
    globals_dict.update(create_cal_task=create_cal_task)
    
    def create_jobs_contracttype(id, build_method, template, ref, name, name_fr, name_en):
        if name.startswith('VSE'):
            obj = isip.ContractType(id=id,build_method=build_method,template=template,ref=ref,name=name,name_fr=name_fr,name_en=name_en)    
        else:
            obj = jobs.ContractType(id=id,build_method=build_method,template=template,ref=ref,name=name,name_fr=name_fr,name_en=name_en)    
        CONTRACT_TYPES[id] = obj
        return obj
    globals_dict.update(create_jobs_contracttype=create_jobs_contracttype)
    def create_jobs_job(id, name, type_id, provider_id, contract_type_id, hourly_rate, capacity, remark):
        ctype = CONTRACT_TYPES.get(contract_type_id)
        if ctype.__class__ != jobs.ContractType:
            dblogger.warning("Dropping VSE Job %s" % 
                list((id, name, type_id, provider_id, contract_type_id, hourly_rate, capacity, remark)))
            return None
        if remark is None: remark = ''
        return Job(id=id,name=name,type_id=type_id,provider_id=provider_id,contract_type_id=contract_type_id,hourly_rate=hourly_rate,capacity=capacity,remark=remark)    
    globals_dict.update(create_jobs_job=create_jobs_job)

    def create_cal_event(id, user_id, created, modified, must_build, person_id, company_id, start_date, start_time, summary, description, access_class, sequence, alarm_value, alarm_unit, dt_alarm, end_date, end_time, transparent, type_id, place_id, priority, status, duration_value, duration_unit, repeat_value, repeat_unit):
        user_id = new_user_id(user_id)
        return Event(id=id,user_id=user_id,created=created,modified=modified,must_build=must_build,person_id=person_id,company_id=company_id,start_date=start_date,start_time=start_time,summary=summary,description=description,access_class=access_class,sequence=sequence,alarm_value=alarm_value,alarm_unit=alarm_unit,dt_alarm=dt_alarm,end_date=end_date,end_time=end_time,transparent=transparent,type_id=type_id,place_id=place_id,priority=priority,status=status,duration_value=duration_value,duration_unit=duration_unit,repeat_value=repeat_value,repeat_unit=repeat_unit)
    globals_dict.update(create_cal_event=create_cal_event)
  
    return '1.2.2'
    
def migrate_from_1_2_2(globals_dict):
    """
    - Moved Study, StudyType and JobExperience from `dsbe` to `jobs`
      (see :blogref:`20110915`).
    - Swap content of notes_NoteType and note.EventType
      (see :blogref:`20110928`).
    """
    
    globals_dict.update(dsbe_Study = resolve_model("jobs.Study"))
    globals_dict.update(dsbe_StudyType = resolve_model("jobs.StudyType"))
    globals_dict.update(dsbe_JobExperience = resolve_model("jobs.Experience"))
    
    notes_EventType = resolve_model("notes.EventType")
    notes_Note = resolve_model("notes.Note")
    notes_NoteType = resolve_model("notes.NoteType")
    def create_notes_eventtype(id, name, remark, name_fr, name_en):
        return notes_NoteType(id=id,name=name,remark=remark,name_fr=name_fr,name_en=name_en)    
        #~ return notes_EventType(id=id,name=name,remark=remark,name_fr=name_fr,name_en=name_en)
    globals_dict.update(create_notes_eventtype=create_notes_eventtype)
    def create_notes_notetype(id, build_method, template, name, important, remark):
        return notes_EventType(id=id,name=name,remark=remark)
        #~ return notes_NoteType(id=id,build_method=build_method,template=template,name=name,important=important,remark=remark)    
    globals_dict.update(create_notes_notetype=create_notes_notetype)
    def create_notes_note(id, user_id, must_build, person_id, company_id, date, type_id, event_type_id, subject, body, language):
        type_id, event_type_id = event_type_id, type_id
        return notes_Note(id=id,user_id=user_id,must_build=must_build,person_id=person_id,company_id=company_id,date=date,type_id=type_id,event_type_id=event_type_id,subject=subject,body=body,language=language)
    globals_dict.update(create_notes_note=create_notes_note)
    
    jobs_JobRequest = resolve_model("jobs.Candidature")
    def create_jobs_jobrequest(id, person_id, job_id, date_submitted, contract_id, remark):
        return jobs_JobRequest(id=id,person_id=person_id,job_id=job_id,date_submitted=date_submitted,contract_id=contract_id,remark=remark)    
    globals_dict.update(create_jobs_jobrequest=create_jobs_jobrequest)

    
    return '1.2.3'
    
def migrate_from_1_2_3(globals_dict):
    """
    - removed jobs.Wish
    """
    jobs_Candidature = resolve_model("jobs.Candidature")

    def create_jobs_candidature(id, person_id, job_id, date_submitted, contract_id, remark):
        return jobs_Candidature(id=id,person_id=person_id,job_id=job_id,date_submitted=date_submitted,remark=remark)
    globals_dict.update(create_jobs_candidature=create_jobs_candidature)
    
    return '1.2.4'
    
def migrate_from_1_2_4(globals_dict):
    """
    - removed alarm fields from cal.Event and cal.Task
    - new model CourseOffer. 
      For each Course instance, create a corresponding CourseOffer instance.
    """
    cal_Event = resolve_model("cal.Event")
    def create_cal_event(id, user_id, created, modified, project_id, must_build, calendar_id, uid, start_date, start_time, summary, description, access_class, sequence, alarm_value, alarm_unit, dt_alarm, user_modified, rset_id, end_date, end_time, transparent, type_id, place_id, priority, status, duration_value, duration_unit):
        return cal_Event(id=id,user_id=user_id,created=created,modified=modified,project_id=project_id,must_build=must_build,calendar_id=calendar_id,uid=uid,start_date=start_date,start_time=start_time,summary=summary,description=description,access_class=access_class,sequence=sequence,user_modified=user_modified,rset_id=rset_id,end_date=end_date,end_time=end_time,transparent=transparent,type_id=type_id,place_id=place_id,priority=priority,status=status,duration_value=duration_value,duration_unit=duration_unit)    
    globals_dict.update(create_cal_event=create_cal_event)
    
    cal_Task = resolve_model("cal.Task")
    new_content_type_id = globals_dict['new_content_type_id']
    def create_cal_task(id, user_id, created, modified, owner_type_id, owner_id, project_id, calendar_id, uid, start_date, start_time, summary, description, access_class, sequence, alarm_value, alarm_unit, dt_alarm, user_modified, rset_id, due_date, due_time, done, percent, status, auto_type):
        owner_type_id = new_content_type_id(owner_type_id)
        return cal_Task(id=id,user_id=user_id,created=created,modified=modified,owner_type_id=owner_type_id,owner_id=owner_id,project_id=project_id,calendar_id=calendar_id,uid=uid,start_date=start_date,start_time=start_time,summary=summary,description=description,access_class=access_class,sequence=sequence,user_modified=user_modified,rset_id=rset_id,due_date=due_date,due_time=due_time,done=done,percent=percent,status=status,auto_type=auto_type)    
    globals_dict.update(create_cal_task=create_cal_task)
    
    from lino.utils.instantiator import i2d
    dsbe_CourseOffer = resolve_model("dsbe.CourseOffer")
    dsbe_Course = resolve_model("dsbe.Course")
    def create_dsbe_course(id, title, content_id, provider_id, start_date, remark):
        o = dsbe_CourseOffer(id=id,title=title,content_id=content_id,provider_id=provider_id,description=remark)
        o.full_clean()
        o.save()
        if start_date is None:
            start_date = i2d(20110901)
        return dsbe_Course(id=id,offer=o,start_date=start_date)
        #~ return dsbe_Course(id=id,title=title,content_id=content_id,provider_id=provider_id,start_date=start_date,remark=remark)    
    globals_dict.update(create_dsbe_course=create_dsbe_course)
    
    dsbe_CourseRequest = resolve_model("dsbe.CourseRequest")
    def create_dsbe_courserequest(id, person_id, content_id, date_submitted, course_id, remark, date_ended, ending_id):
        return dsbe_CourseRequest(id=id,person_id=person_id,content_id=content_id,date_submitted=date_submitted,course_id=course_id,
            offer_id=course_id,
            remark=remark,date_ended=date_ended,ending_id=ending_id)    
    globals_dict.update(create_dsbe_courserequest=create_dsbe_courserequest)
    
    return '1.2.5'
    
def migrate_from_1_2_5(globals_dict): return '1.2.6'
  
def migrate_from_1_2_6(globals_dict):    
    """
    - Rename fields `sex` to `gender` 
      in `contacts.Person`, `users.User`, `dsbe.PersonSearch`.
    - add previously hard-coded objects from 
      :mod:`lino.modlib.cal.fixtures.std`
    """
    from lino.utils.mti import insert_child
    contacts_Contact = resolve_model("contacts.Contact")
    contacts_Person = resolve_model("contacts.Person")
    users_User = resolve_model("users.User")
    dsbe_PersonSearch = resolve_model("dsbe.PersonSearch")
    cal_Event = resolve_model("cal.Event")
    cal_Task = resolve_model("cal.Task")
    cal_AccessClass = resolve_model("cal.AccessClass")
    cal_Priority = resolve_model("cal.Priority")
    cal_TaskStatus = resolve_model("cal.TaskStatus")
    cal_EventStatus = resolve_model("cal.EventStatus")
    new_content_type_id = globals_dict['new_content_type_id']
    
    def create_contacts_person(contact_ptr_id, first_name, last_name, title, sex, birth_date, birth_date_circa, is_active, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, obstacles, skills, job_agents, job_office_contact_id):
        return insert_child(contacts_Contact.objects.get(pk=contact_ptr_id),
            contacts_Person,first_name=first_name,last_name=last_name,
            title=title,gender=sex,birth_date=birth_date,birth_date_circa=birth_date_circa,is_active=is_active,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,is_senior=is_senior,group_id=group_id,coached_from=coached_from,coached_until=coached_until,coach1_id=coach1_id,coach2_id=coach2_id,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,national_id=national_id,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,job_office_contact_id=job_office_contact_id)
    globals_dict.update(create_contacts_person=create_contacts_person)
    
    def create_users_user(contact_ptr_id, first_name, last_name, title, sex, username, is_staff, is_expert, is_active, is_superuser, last_login, date_joined, is_spis):
        return insert_child(contacts_Contact.objects.get(pk=contact_ptr_id),users_User,
            first_name=first_name,last_name=last_name,title=title,
            gender=sex,
            username=username,is_staff=is_staff,is_expert=is_expert,is_active=is_active,is_superuser=is_superuser,last_login=last_login,date_joined=date_joined,is_spis=is_spis)
    globals_dict.update(create_users_user=create_users_user)
    
    def create_dsbe_personsearch(id, user_id, title, aged_from, aged_to, sex, only_my_persons, coached_by_id, period_from, period_until):
        return dsbe_PersonSearch(id=id,user_id=user_id,title=title,
          aged_from=aged_from,aged_to=aged_to,gender=sex,
          only_my_persons=only_my_persons,coached_by_id=coached_by_id,period_from=period_from,period_until=period_until)
    globals_dict.update(create_dsbe_personsearch=create_dsbe_personsearch)
    
    def get_it_or_none(m,ref):
        try:
            return m.objects.get(ref=ref)
        except m.DoesNotExist:
            return None
        
    
    def create_cal_event(id, user_id, created, modified, project_id, must_build, calendar_id, uid, start_date, start_time, summary, description, access_class, sequence, user_modified, rset_id, end_date, end_time, transparent, type_id, place_id, priority, status, duration_value, duration_unit):
        status = get_it_or_none(cal_EventStatus,status)
        priority = get_it_or_none(cal_Priority,priority)
        access_class = get_it_or_none(cal_AccessClass,access_class)
      
        return cal_Event(id=id,user_id=user_id,created=created,modified=modified,
          project_id=project_id,must_build=must_build,calendar_id=calendar_id,
          uid=uid,start_date=start_date,start_time=start_time,
          summary=summary,description=description,
          access_class=access_class,
          sequence=sequence,user_modified=user_modified,
          rset_id=rset_id,end_date=end_date,end_time=end_time,
          transparent=transparent,type_id=type_id,place_id=place_id,
          priority=priority,
          status=status,
          duration_value=duration_value,duration_unit=duration_unit)
    globals_dict.update(create_cal_event=create_cal_event)
    
    def create_cal_task(id, user_id, created, modified, owner_type_id, owner_id, project_id, calendar_id, uid, start_date, start_time, summary, description, access_class, sequence, user_modified, rset_id, due_date, due_time, done, percent, status, auto_type):
        owner_type_id = new_content_type_id(owner_type_id)
        status = get_it_or_none(cal_TaskStatus,status)
        access_class = get_it_or_none(cal_AccessClass,access_class)
        return cal_Task(id=id,user_id=user_id,created=created,
            modified=modified,owner_type_id=owner_type_id,owner_id=owner_id,
            project_id=project_id,calendar_id=calendar_id,uid=uid,
            start_date=start_date,start_time=start_time,summary=summary,
            description=description,
            access_class=access_class,
            sequence=sequence,user_modified=user_modified,rset_id=rset_id,
            due_date=due_date,due_time=due_time,done=done,
            percent=percent,status=status,auto_type=auto_type)
    globals_dict.update(create_cal_task=create_cal_task)
    
    
    objects = globals_dict['objects']
    def new_objects():
        from lino.modlib.cal.fixtures import std
        yield std.objects()
        yield objects()
    globals_dict.update(objects=new_objects)
    
    #~ raise Exception("todo: sex -> gender in Person, PersonSearch")
    return '1.2.7'
  
def migrate_from_1_2_7(globals_dict):    
    """Convert `birth_date` fields to the new :class:`lino.fields.IncompleteDate` type.
    See :blogref:`20111119`.
    """
    from lino.utils.mti import insert_child
    contacts_Contact = resolve_model("contacts.Contact")
    contacts_Person = resolve_model("contacts.Person")
  
    def create_contacts_person(contact_ptr_id, birth_date, birth_date_circa, first_name, last_name, title, gender, is_active, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, obstacles, skills, job_agents, job_office_contact_id):
        if birth_date_circa:
            raise Exception("birth_date_circa for %s %s %s" % (contact_ptr_id,first_name,last_name))
        return insert_child(contacts_Contact.objects.get(pk=contact_ptr_id),contacts_Person,birth_date=birth_date,first_name=first_name,last_name=last_name,title=title,gender=gender,is_active=is_active,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,is_senior=is_senior,group_id=group_id,coached_from=coached_from,coached_until=coached_until,coach1_id=coach1_id,coach2_id=coach2_id,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,national_id=national_id,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,job_office_contact_id=job_office_contact_id)
    globals_dict.update(create_contacts_person=create_contacts_person)
  
    return '1.2.8'

def migrate_from_1_2_8(globals_dict):    
    """
Convert Schedule and Regime fields in contracts.
NOT Convert Roles to Links (and RoleTypes to LinkTypes).
Needs manual adaption of dpy file:

- Replace line ``from lino.utils.mti import insert_child`` 
  by ``from lino.utils.mti import create_child as insert_child``
  
- Replace lines like 
  ``insert_child(contacts_Contact.objects.get(pk=contact_ptr_id),...)``
  by
  ``insert_child(contacts_Contact,contact_ptr_id,...)``
- 
    """
    jobs_Contract = resolve_model("jobs.Contract")
    Schedule = resolve_model("jobs.Schedule")
    Regime = resolve_model("jobs.Regime")
    def convert(cl,name):
        if not name: return None
        try:
            return cl.objects.get(name=name)
        except cl.DoesNotExist:
            obj = cl(name=name)
            obj.save()
            return obj
    def create_jobs_contract(id, user_id, must_build, person_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, provider_id, job_id, duration, regime, schedule, hourly_rate, refund_rate, reference_person, responsibilities, remark):
        schedule = convert(Schedule,schedule)
        regime = convert(Regime,regime)
        return jobs_Contract(id=id,user_id=user_id,must_build=must_build,person_id=person_id,contact_id=contact_id,language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,provider_id=provider_id,job_id=job_id,duration=duration,regime=regime,schedule=schedule,hourly_rate=hourly_rate,refund_rate=refund_rate,reference_person=reference_person,responsibilities=responsibilities,remark=remark)
    globals_dict.update(create_jobs_contract=create_jobs_contract)
    
    #~ contacts_Role = resolve_model("links.Link")
    #~ contacts_RoleType = resolve_model("links.LinkType")
    
    #~ from django.contrib.contenttypes.models import ContentType
    #~ Person = resolve_model('contacts.Person')
    #~ Company = resolve_model('contacts.Company')
    #~ a_type = ContentType.objects.get_for_model(Company)
    #~ b_type = ContentType.objects.get_for_model(Person)
    #~ DEFAULT_LINKTYPE = contacts_RoleType(name='*',a_type=a_type,b_type=b_type,id=99)
    #~ DEFAULT_LINKTYPE.save()
    
    #~ def create_contacts_roletype(id, name, name_fr, name_en, use_in_contracts):
        #~ return contacts_RoleType(id=id,name=name,name_fr=name_fr,name_en=name_en,
            #~ a_type=a_type,b_type=b_type,
            #~ use_in_contracts=use_in_contracts)    
    #~ globals_dict.update(create_contacts_roletype=create_contacts_roletype)
    
    #~ def create_contacts_role(id, parent_id, child_id, type_id):
        #~ if type_id is None:
            #~ type_id = DEFAULT_LINKTYPE.pk
        #~ return contacts_Role(id=id,a_id=parent_id,b_id=child_id,type_id=type_id)
    #~ globals_dict.update(create_contacts_role=create_contacts_role)
    
    contacts_Role = resolve_model("contacts.Role")
    def create_contacts_role(id, parent_id, child_id, type_id):
        return contacts_Role(id=id,company_id=parent_id,person_id=child_id,type_id=type_id)
    globals_dict.update(create_contacts_role=create_contacts_role)
    
    #~ ignore any data from previous links module:
    
    def create_links_link(id, user_id, person_id, company_id, type_id, date, url, name):
        return None
    globals_dict.update(create_links_link=create_links_link)
    def create_links_linktype(id, name):
        return None
    globals_dict.update(create_links_linktype=create_links_linktype)
    del globals_dict['links_LinkType']
    del globals_dict['links_Link']
    
    #~ Discovered that due to a bug in previous dpy versions
    #~ there were some Upload records on Role and RoleType 
    #~ in a customer's database. That's why we need to redefine also the 
    #~ global variables contacts_Role and contacts_RoleType:
    
    #~ globals_dict.update(contacts_Role=contacts_Role)
    #~ globals_dict.update(contacts_RoleType=contacts_RoleType)
    
    #~ add previously hard-coded jobs.Regime and jobs.Schedule from fixture
    
    objects = globals_dict['objects']
    def new_objects():
        from lino.modlib.jobs.fixtures import std
        yield std.objects()
        yield objects()
    globals_dict.update(objects=new_objects)
    
    
    #~ from lino.utils.mti import create_child
    #~ globals_dict.update(insert_child=create_child)
  
    return '1.3.0'
    
def migrate_from_1_3_0(globals_dict): return '1.3.1'
  
def migrate_from_1_3_1(globals_dict): return '1.3.2'
  
def migrate_from_1_3_2(globals_dict):
    """
    - new field `isip.ExamPolicy.every_unit` 
    - new `dsbe.PersonGroup.active`
    - In :class:`lino.mixins.printable.CachedPrintable`,
      BooleanField `must_build` has been replaced by a DateTimeField `build_time`.
      
    """
    cal_Event = resolve_model('cal.Event')
    cal_Guest = resolve_model('cal.Guest')
    isip_Contract = resolve_model('isip.Contract')
    jobs_Contract = resolve_model('jobs.Contract')
    jobs_ContractsSituation = resolve_model('jobs.ContractsSituation')
    lino_DataControlListing = resolve_model('lino.DataControlListing')
    mails_Mail = resolve_model('mails.Mail')
    notes_Note = resolve_model('notes.Note')
    new_content_type_id = globals_dict.get('new_content_type_id')
    def create_cal_event(id, user_id, created, modified, owner_type_id, owner_id, project_id, must_build, calendar_id, uid, start_date, start_time, summary, description, access_class_id, sequence, auto_type, user_modified, rset_id, end_date, end_time, transparent, type_id, place_id, priority_id, status_id, duration_value, duration_unit):
        owner_type_id = new_content_type_id(owner_type_id)
        obj = cal_Event(id=id,user_id=user_id,created=created,modified=modified,owner_type_id=owner_type_id,owner_id=owner_id,project_id=project_id,
          #~ must_build=must_build,
          calendar_id=calendar_id,uid=uid,start_date=start_date,start_time=start_time,summary=summary,description=description,access_class_id=access_class_id,sequence=sequence,auto_type=auto_type,user_modified=user_modified,rset_id=rset_id,end_date=end_date,end_time=end_time,transparent=transparent,type_id=type_id,place_id=place_id,priority_id=priority_id,status_id=status_id,duration_value=duration_value,duration_unit=duration_unit)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_cal_event=create_cal_event)
    def create_cal_guest(id, must_build, contact_id, language, event_id, role_id, status_id, remark):
        obj = cal_Guest(id=id,
          #~ must_build=must_build,
          contact_id=contact_id,language=language,event_id=event_id,role_id=role_id,status_id=status_id,remark=remark)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_cal_guest=create_cal_guest)
    def create_isip_contract(id, user_id, must_build, person_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, company_id, stages, goals, duties_asd, duties_dsbe, duties_company, duties_person):
        obj = isip_Contract(id=id,user_id=user_id,
          #~ must_build=must_build,
          person_id=person_id,contact_id=contact_id,language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,company_id=company_id,stages=stages,goals=goals,duties_asd=duties_asd,duties_dsbe=duties_dsbe,duties_company=duties_company,duties_person=duties_person)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_isip_contract=create_isip_contract)
    def create_jobs_contract(id, user_id, must_build, person_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, provider_id, job_id, duration, regime_id, schedule_id, hourly_rate, refund_rate, reference_person, responsibilities, remark):
        obj = jobs_Contract(id=id,user_id=user_id,
          #~ must_build=must_build,
          person_id=person_id,contact_id=contact_id,language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,provider_id=provider_id,job_id=job_id,duration=duration,regime_id=regime_id,schedule_id=schedule_id,hourly_rate=hourly_rate,refund_rate=refund_rate,reference_person=reference_person,responsibilities=responsibilities,remark=remark)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_jobs_contract=create_jobs_contract)
    def create_jobs_contractssituation(id, must_build, date, contract_type_id, job_type_id):
        obj = jobs_ContractsSituation(id=id,
          #~ must_build=must_build,
          date=date,contract_type_id=contract_type_id,job_type_id=job_type_id)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_jobs_contractssituation=create_jobs_contractssituation)
    def create_lino_datacontrollisting(id, must_build, date):
        obj = lino_DataControlListing(id=id,
          #~ must_build=must_build,
          date=date)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_lino_datacontrollisting=create_lino_datacontrollisting)
    def create_mails_mail(id, must_build, type_id, sender_id, subject, body, received, sent):
        obj = mails_Mail(id=id,
          #~ must_build=must_build,
          type_id=type_id,sender_id=sender_id,subject=subject,body=body,received=received,sent=sent)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_mails_mail=create_mails_mail)
    def create_notes_note(id, user_id, must_build, person_id, company_id, date, type_id, event_type_id, subject, body, language):
        obj = notes_Note(id=id,user_id=user_id,
          #~ must_build=must_build,
          person_id=person_id,company_id=company_id,date=date,type_id=type_id,event_type_id=event_type_id,subject=subject,body=body,language=language)
        obj.build_time = obj.get_cache_mtime()
        return obj
    globals_dict.update(create_notes_note=create_notes_note)
    
    
    return '1.3.3'

def migrate_from_1_3_3(globals_dict):
    """
    Convert Person.residence_type data type from INT to CHAR.
    """
    
    contacts_Contact = resolve_model("contacts.Contact")
    contacts_Person = resolve_model("contacts.Person")
    from lino.utils.mti import create_child
    
    def create_contacts_person(contact_ptr_id, birth_date, first_name, last_name, title, gender, is_active, newcomer, is_deprecated, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, obstacles, skills, job_agents, job_office_contact_id):
        residence_type = str(residence_type)
        return create_child(contacts_Contact,contact_ptr_id,contacts_Person,birth_date=birth_date,first_name=first_name,last_name=last_name,title=title,gender=gender,is_active=is_active,newcomer=newcomer,is_deprecated=is_deprecated,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,is_senior=is_senior,group_id=group_id,coached_from=coached_from,coached_until=coached_until,coach1_id=coach1_id,coach2_id=coach2_id,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,national_id=national_id,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,job_office_contact_id=job_office_contact_id)    
    globals_dict.update(create_contacts_person=create_contacts_person)
    
    return '1.3.4'
  

def migrate_from_1_3_4(globals_dict): return '1.3.5'
def migrate_from_1_3_5(globals_dict): return '1.3.6'
  
def migrate_from_1_3_6(globals_dict):
    """\
Adds new fields Person.broker, Person.faculty, User.is_newcomer, User.newcomer_quota
and new models Broker and Faculty, Competence."""
    return '1.3.7'

def migrate_from_1_3_7(globals_dict): 
    """
    - Remove field newcomers.Faculty.body
    - Add field dsbe.CourseRequest.urgent
    """
    newcomers_Faculty = resolve_model("newcomers.Faculty")
    def create_newcomers_faculty(id, name, body, body_fr, body_en, name_fr, name_en):
        return newcomers_Faculty(id=id,name=name,name_fr=name_fr,name_en=name_en)
    globals_dict.update(create_newcomers_faculty=create_newcomers_faculty)
    return '1.3.8'

def migrate_from_1_3_8(globals_dict): 
    """
    - Remove fields `cal.Event.duration_value` and `cal.Event.duration_unit`
    """
    cal_Event = resolve_model("cal.Event")
    new_content_type_id = globals_dict['new_content_type_id']
    def create_cal_event(id, user_id, created, modified, owner_type_id, owner_id, project_id, build_time, calendar_id, uid, start_date, start_time, summary, description, access_class_id, sequence, auto_type, user_modified, rset_id, end_date, end_time, transparent, type_id, place_id, priority_id, status_id, duration_value, duration_unit):
        owner_type_id = new_content_type_id(owner_type_id)
        return cal_Event(id=id,user_id=user_id,created=created,modified=modified,
          owner_type_id=owner_type_id,owner_id=owner_id,project_id=project_id,
          build_time=build_time,calendar_id=calendar_id,
          uid=uid,start_date=start_date,start_time=start_time,
          summary=summary,description=description,access_class_id=access_class_id,
          sequence=sequence,auto_type=auto_type,
          user_modified=user_modified,rset_id=rset_id,end_date=end_date,end_time=end_time,
          transparent=transparent,type_id=type_id,place_id=place_id,
          priority_id=priority_id,status_id=status_id
          #~ ,duration_value=duration_value,duration_unit=duration_unit
          )    
    globals_dict.update(create_cal_event=create_cal_event)
    return '1.3.9'

def migrate_from_1_3_9(globals_dict): 
    """
    - remove tables lino_datacontrollisting and jobs_contractssituation
    """
    def lino_datacontrollisting_objects(): return None
    globals_dict.update(lino_datacontrollisting_objects=lino_datacontrollisting_objects)
    def jobs_contractssituation_objects(): return None
    globals_dict.update(jobs_contractssituation_objects=jobs_contractssituation_objects)
    return '1.4.0'
    
def migrate_from_1_4_0(globals_dict): 
    """
    No database changes.
    """
    return '1.4.1'
    
def migrate_from_1_4_1(globals_dict): 
    """
    Some new fields in IdentifyPersonRequest with default values.
    """
    return '1.4.2'

def migrate_from_1_4_2(globals_dict): 
    """
    Field `jobs.contract.provider` renamed to company
    """
    jobs_Contract = resolve_model("jobs.Contract")
    def create_jobs_contract(id, user_id, build_time, person_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, provider_id, job_id, duration, regime_id, schedule_id, hourly_rate, refund_rate, reference_person, responsibilities, remark):
        return jobs_Contract(id=id,user_id=user_id,build_time=build_time,
          person_id=person_id,contact_id=contact_id,
          language=language,applies_from=applies_from,
          applies_until=applies_until,date_decided=date_decided,
          date_issued=date_issued,user_asd_id=user_asd_id,
          exam_policy_id=exam_policy_id,ending_id=ending_id,
          date_ended=date_ended,type_id=type_id,
          #~ provider_id=provider_id,
          company_id=provider_id,
          job_id=job_id,duration=duration,regime_id=regime_id,schedule_id=schedule_id,hourly_rate=hourly_rate,refund_rate=refund_rate,reference_person=reference_person,responsibilities=responsibilities,remark=remark)    
    globals_dict.update(create_jobs_contract=create_jobs_contract)
    return '1.4.3'


def migrate_from_1_4_3(globals_dict): 
    """
    - :mod:`lino.modlib.contacts` : renamed "Contact" to "Partner".
    - :mod:`lino.modlib.outbox` : renamed "Mail.contact" to "Mail.partner".
    - renamed "bcss" to "cbss"
    - renamed "lino.apps.dsbe" to "lino.apps.pcsw"
    - cal.Event.rset
    - new user permissions system (fields like `is_staff` replaced by `level`)
    - manually handle invalid contracts and persons. See :blogref:`20120418`.
    - removed field `title` from bcss.IdentifyPersonRequest
    - Users are no longer MTI subclass of Partner but have a FK `partner`. 
    - `cbss.IdentifyPersonRequest`: field `project` replaced by `person`.
    - convert Person.civil_state to choicelist CivilState
    - new tables cbss.Purpose and cbss.Sector
    - add default data from library fixtures (debts, households, purposes)
    - convert Companies with prefix == 'Eheleute' to a Household
    - convert tables cal.EventStatus, cal.TaskStatus and cal.GuestStatus to choicelists.
    - table thirds.Third no longer exists
    - new fields MailableType to cal.EventType and notes.NoteType
    - severe test in isip.Contract
    - added workflow to modules courses and cal
    - notes.Note is now ProjectRelated 
      (and field `company` is injected by lino.apps.pcsw)
    """
    from lino.core.dbutils import resolve_model
    from lino.utils.mti import create_child
    from lino.modlib.users.models import UserProfiles
    #~ from lino.utils import mti
    #~ from lino.utils import dblogger
    
    contacts_Contact = resolve_model("contacts.Partner")
    users_User = resolve_model("users.User")
    globals_dict.update(contacts_Contact=contacts_Contact)
    globals_dict.update(bcss_IdentifyPersonRequest = resolve_model("cbss.IdentifyPersonRequest"))
    globals_dict.update(dsbe_Activity = resolve_model("pcsw.Activity"))
    globals_dict.update(dsbe_AidType = resolve_model("pcsw.AidType"))
    globals_dict.update(dsbe_Course = resolve_model("courses.Course"))
    globals_dict.update(dsbe_CourseContent = resolve_model("courses.CourseContent"))
    #~ globals_dict.update(dsbe_CourseEnding = resolve_model("courses.CourseEnding"))
    globals_dict.update(dsbe_CourseOffer = resolve_model("courses.CourseOffer"))
    globals_dict.update(dsbe_CourseProvider = resolve_model("courses.CourseProvider"))
    globals_dict.update(dsbe_CourseRequest = resolve_model("courses.CourseRequest"))
    globals_dict.update(dsbe_Exclusion = resolve_model("pcsw.Exclusion"))
    globals_dict.update(dsbe_ExclusionType = resolve_model("pcsw.ExclusionType"))
    globals_dict.update(dsbe_LanguageKnowledge = resolve_model("cv.LanguageKnowledge"))
    globals_dict.update(dsbe_PersonGroup = resolve_model("pcsw.PersonGroup"))
    globals_dict.update(dsbe_PersonSearch = resolve_model("pcsw.PersonSearch"))
    globals_dict.update(dsbe_WantedLanguageKnowledge = resolve_model("pcsw.WantedLanguageKnowledge"))
    
    mails_Recipient = resolve_model("mails.Recipient")
    def create_mails_recipient(id, mail_id, contact_id, type, address, name):
        return mails_Recipient(id=id,mail_id=mail_id,partner_id=contact_id,type=type,address=address,name=name)
    globals_dict.update(create_mails_recipient=create_mails_recipient)
    
    cal_Event = resolve_model("cal.Event")
    from lino.modlib.cal.utils import EventStates, TaskState, GuestState
    new_content_type_id = globals_dict['new_content_type_id']
    def create_cal_event(id, user_id, created, modified, owner_type_id, owner_id, project_id, build_time, calendar_id, uid, start_date, start_time, summary, description, access_class_id, sequence, auto_type, user_modified, rset_id, end_date, end_time, transparent, type_id, place_id, priority_id, status_id):
        owner_type_id = new_content_type_id(owner_type_id)
        state = EventStates.migrate(status_id)
        if state is None:
            if start_date < datetime.date.today():
                state = EventStates.obsolete
            elif user_modified:
                state = EventStates.draft
        calendar_id = type_id or 2
        return cal_Event(id=id,user_id=user_id,created=created,modified=modified,owner_type_id=owner_type_id,owner_id=owner_id,project_id=project_id,build_time=build_time,calendar_id=calendar_id,uid=uid,start_date=start_date,start_time=start_time,summary=summary,description=description,
            #~ access_class_id=access_class_id,
            sequence=sequence,auto_type=auto_type,
            #~ user_modified=user_modified,
            #~ rset_id=rset_id,
            end_date=end_date,end_time=end_time,transparent=transparent,
            #~ type_id=type_id,
            place_id=place_id,priority_id=priority_id,state=state)
    globals_dict.update(create_cal_event=create_cal_event)
    
    cal_Task = resolve_model("cal.Task")
    def create_cal_task(id, user_id, created, modified, owner_type_id, owner_id, project_id, calendar_id, uid, start_date, start_time, summary, description, access_class_id, sequence, auto_type, user_modified, rset_id, due_date, due_time, done, percent, status_id):
        owner_type_id = new_content_type_id(owner_type_id)
        state = TaskState.migrate(status_id)
        if done:
            state = TaskState.done
        elif state is None and user_modified:
            state = TaskState.todo
        calendar_id = None
        return cal_Task(id=id,user_id=user_id,created=created,modified=modified,owner_type_id=owner_type_id,owner_id=owner_id,
            project_id=project_id,calendar_id=calendar_id,uid=uid,start_date=start_date,start_time=start_time,summary=summary,description=description,
            #~ access_class_id=access_class_id,
            sequence=sequence,auto_type=auto_type,
            #~ user_modified=user_modified,
            #~ rset_id=rset_id,
            due_date=due_date,due_time=due_time,
            #done=done,
            percent=percent,
            state=state)
    globals_dict.update(create_cal_task=create_cal_task)
    
    cal_Guest = resolve_model("cal.Guest")
    def create_cal_guest(id, build_time, contact_id, language, event_id, role_id, status_id, remark):
        return cal_Guest(id=id,build_time=build_time,contact_id=contact_id,language=language,
            event_id=event_id,role_id=role_id,
            #~ status_id=GuestState.migrate(status_id),
            remark=remark)    
    globals_dict.update(create_cal_guest=create_cal_guest)
    
    def create_users_user(contact_ptr_id, first_name, last_name, title, gender, username, is_staff, is_expert, is_active, is_superuser, last_login, date_joined, is_spis, is_newcomers, newcomer_quota):
        kw = dict()
        #~ if is_staff or is_expert or is_superuser:
            # level = UserLevels.manager
            #~ kw.update(profile=UserProfiles.gerd)
            # kw.update(level=level)
        #~ else:
            #~ level = UserLevel.user
        #~ if is_spis:
            #~ kw.update(level=level)
            #~ kw.update(integ_level = level)
            #~ kw.update(cbss_level = level)
        #~ if is_newcomers:
            #~ kw.update(level=level)
            #~ kw.update(newcomers_level = level)
        if username in ('gerd','lsaffre'):
            kw.update(profile='900') # UserProfiles.admin)
        elif username in ('hubert','alicia','uwe'):
            kw.update(profile='100') # UserProfiles.hubert)
        #~ elif username == 'gerd':
            #~ kw.update(debts_level=UserLevel.manager)
        elif username == 'kerstin':
            kw.update(profile='300') # UserProfiles.kerstin)
        elif username == 'caroline':
            kw.update(profile='200') # UserProfiles.caroline)
            #~ kw.update(debts_level=UserLevel.user)
            #~ kw.update(level=UserLevel.user)
        #~ return create_child(contacts_Contact,contact_ptr_id,users_User,
        if not date_joined:
            date_joined = datetime.datetime.now()
        return users_User(partner_id=contact_ptr_id,
          id=contact_ptr_id,
          first_name=first_name,last_name=last_name,
          email=contacts_Contact.objects.get(pk=contact_ptr_id).email,
          #~ title=title,gender=gender,
          username=username,
          #~ is_staff=is_staff,is_expert=is_expert,is_active=is_active,is_superuser=is_superuser,
          #~ last_login=last_login,date_joined=date_joined,
          created=date_joined,
          modified=date_joined,
          #~ is_spis=is_spis,is_newcomers=is_newcomers,
          newcomer_quota=newcomer_quota,**kw)
    globals_dict.update(create_users_user=create_users_user)
    
    #~ from django.core.exceptions import ValidationError
    
    isip_Contract = resolve_model("isip.Contract")
    def create_isip_contract(id, user_id, build_time, person_id, company_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, stages, goals, duties_asd, duties_dsbe, duties_company, duties_person):
        #~ - isip.Contract [u'Contracts ends before it started.'] (3 object(s), e.g. Contract(id=62,user=200085,person=21936,langua
        #~ ge=u'de',applies_from=datetime.date(2009, 12, 19),date_decided=datetime.date(2010, 1, 14),date_issued=datetime.date(2010
        #~ , 1, 14),ending=2,date_ended=datetime.date(2009, 8, 31),type=9,stages=u'Abitur'))      
        if id == 62: 
            date_ended = applies_from
            
        #~ - isip.Contract [u'Contracts ends before it started.'] (2 object(s), e.g. Contract(id=204,user=200096,person=22287,langu
        #~ age=u'de',applies_from=datetime.date(2011, 12, 1),applies_until=datetime.date(2011, 8, 1),user_asd=200088,exam_policy=1,
        #~ type=7))            
        if id == 204: 
            applies_from = applies_until
            #~ applies_until = None
            
        #~ - isip.Contract [u'Contracts ends before it started.'] (1 object(s), e.g. Contract(id=325,user=200099,build_time=datetim
        #~ e.datetime(2012, 4, 12, 9, 51, 19),person=22423,language=u'de',applies_from=datetime.date(2012, 4, 1),applies_until=date
        #~ time.date(2011, 7, 31),date_decided=datetime.date(2012, 4, 12),date_issued=datetime.date(2012, 4, 12),user_asd=200097,ex
        #~ '))            
        if id == 325: 
            applies_until = None
            #~ applies_until = None
        return isip_Contract(pk=id,user_id=user_id,build_time=build_time,person_id=person_id,company_id=company_id,contact_id=contact_id,language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,stages=stages,goals=goals,duties_asd=duties_asd,duties_dsbe=duties_dsbe,duties_company=duties_company,duties_person=duties_person)
    #~ 20120604 globals_dict.update(create_isip_contract=create_isip_contract)
    
    jobs_Contract = resolve_model("jobs.Contract")
    def create_jobs_contract(id, user_id, build_time, person_id, company_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, job_id, duration, regime_id, schedule_id, hourly_rate, refund_rate, reference_person, responsibilities, remark):
        if id == 153: # VSE#62 : [u'Contracts ends before it started.
            applies_until = applies_from # was 31.08.-01.09.2011, now 01.09.-01.09.2011
            #~ applies_until = None
        return jobs_Contract(id=id,user_id=user_id,build_time=build_time,person_id=person_id,company_id=company_id,contact_id=contact_id,language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,job_id=job_id,duration=duration,regime_id=regime_id,schedule_id=schedule_id,hourly_rate=hourly_rate,refund_rate=refund_rate,reference_person=reference_person,responsibilities=responsibilities,remark=remark)
    #~ 20120604 globals_dict.update(create_jobs_contract=create_jobs_contract)
    
    bcss_IdentifyPersonRequest = resolve_model("cbss.IdentifyPersonRequest")
    def create_bcss_identifypersonrequest(id, user_id, project_id, birth_date, first_name, last_name, title, gender, sent, status, request_xml, response_xml, national_id, middle_name, tolerance):
        if not birth_date:
            return None
        return bcss_IdentifyPersonRequest(id=id,user_id=user_id,person_id=project_id,
            birth_date=birth_date,first_name=first_name,last_name=last_name,
            gender=gender,sent=sent,status=status,request_xml=request_xml,response_xml=response_xml,national_id=national_id,middle_name=middle_name,tolerance=tolerance)    
    globals_dict.update(create_bcss_identifypersonrequest=create_bcss_identifypersonrequest)
    
    
    from lino.modlib.courses.models import CourseRequestStates
    #~ courses_CourseRequest = resolve_model("courses.CourseRequest")
    dsbe_CourseRequest = resolve_model("courses.CourseRequest")
    def create_dsbe_courserequest(id, person_id, offer_id, content_id, date_submitted, urgent, course_id, remark, date_ended, ending_id):
        state=CourseRequestStates.migrate(ending_id)
        if course_id is not None and state == CourseRequestStates.candidate:
            state = CourseRequestStates.registered
        return dsbe_CourseRequest(id=id,person_id=person_id,offer_id=offer_id,content_id=content_id,date_submitted=date_submitted,
            urgent=urgent,
            course_id=course_id,remark=remark,date_ended=date_ended,
            state=state)
            #~ ending_id=ending_id)    
    globals_dict.update(create_dsbe_courserequest=create_dsbe_courserequest)
    
    from lino.apps.pcsw.models import CivilState
    contacts_Person = resolve_model("contacts.Person")
    def create_contacts_person(contact_ptr_id, birth_date, first_name, last_name, title, gender, is_active, newcomer, is_deprecated, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, obstacles, skills, job_agents, job_office_contact_id, broker_id, faculty_id):
        civil_state = CivilState.old2new(civil_state)
        if title in ("Herr","Herrn","Frau",u"Fräulein","Madame"):
            title = ''
        
        return create_child(contacts_Contact,contact_ptr_id,contacts_Person,birth_date=birth_date,first_name=first_name,last_name=last_name,title=title,gender=gender,is_active=is_active,newcomer=newcomer,is_deprecated=is_deprecated,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,is_senior=is_senior,group_id=group_id,coached_from=coached_from,coached_until=coached_until,coach1_id=coach1_id,coach2_id=coach2_id,birth_place=birth_place,birth_country_id=birth_country_id,civil_state=civil_state,national_id=national_id,health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,job_office_contact_id=job_office_contact_id,broker_id=broker_id,faculty_id=faculty_id)    
    globals_dict.update(create_contacts_person=create_contacts_person)
    
    contacts_Company = resolve_model("contacts.Company")
    households_Household = resolve_model("households.Household")
    households_Type = resolve_model("households.Type")
    def create_contacts_company(contact_ptr_id, prefix, vat_id, type_id, is_active, newcomer, is_deprecated, activity_id, bank_account1, bank_account2, hourly_rate):
        if prefix == 'Eheleute' and vat_id.endswith('.999'):
            type = households_Type.objects.get(pk=1)
            return create_child(contacts_Contact,contact_ptr_id,households_Household,type=type,is_active=is_active,newcomer=newcomer,is_deprecated=is_deprecated,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2)    
        return create_child(contacts_Contact,contact_ptr_id,contacts_Company,prefix=prefix,vat_id=vat_id,type_id=type_id,is_active=is_active,newcomer=newcomer,is_deprecated=is_deprecated,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,hourly_rate=hourly_rate)
    globals_dict.update(create_contacts_company=create_contacts_company)
    
    def create_cal_taskstatus(id, name, ref, name_fr, name_en):
        pass
    globals_dict.update(create_cal_taskstatus=create_cal_taskstatus)
    def create_cal_eventstatus(id, name, ref, reminder, name_fr, name_en): 
        pass
    globals_dict.update(create_cal_eventstatus=create_cal_eventstatus)
    def create_cal_gueststatus(id, name, ref, name_fr, name_en):    
        pass
    globals_dict.update(create_cal_gueststatus=create_cal_gueststatus)
    
    def create_thirds_third(*args):
        dblogger.info("Ignored thirds.Third %r",args)
        return None
    globals_dict.update(create_thirds_third=create_thirds_third)
    
    def create_dsbe_courseending(*args):
        dblogger.info("Ignored dsbe.CourseEnding %r",args)
        return None
    globals_dict.update(create_dsbe_courseending=create_dsbe_courseending)
    
    notes_NoteType = resolve_model("notes.NoteType")
    def create_notes_notetype(id, name, build_method, template, important, remark, name_fr, name_en):
        return notes_NoteType(id=id,name=name,build_method=build_method,
          email_template='Default.eml.html',
          template=template,important=important,remark=remark,name_fr=name_fr,
          name_en=name_en)
    globals_dict.update(create_notes_notetype=create_notes_notetype)
    
    notes_Note = resolve_model("notes.Note")
    def create_notes_note(id, user_id, build_time, person_id, company_id, date, type_id, event_type_id, subject, body, language):
        return notes_Note(id=id,user_id=user_id,build_time=build_time,
          #~ person_id=person_id,
          project_id=person_id,
          company_id=company_id,date=date,type_id=type_id,event_type_id=event_type_id,subject=subject,body=body,language=language)    
    globals_dict.update(create_notes_note=create_notes_note)
    
    #~ cal_EventType = resolve_model("cal.EventType")
    #~ def create_cal_eventtype(id, name, build_method, template, name_fr, name_en):
        #~ return cal_EventType(id=id,name=name,build_method=build_method,template=template,
          #~ email_template='Default.eml.html',
          #~ name_fr=name_fr,name_en=name_en)    
    #~ globals_dict.update(create_cal_eventtype=create_cal_eventtype)
    
    #~ cal_Calendar= resolve_model("cal.Calendar")
    #~ def create_cal_calendar(id, user_id, type, name, description, 
        #~ url_template, username, password, readonly, is_default, is_hidden, start_date, color):
        #~ return cal_Calendar(id=id,user_id=user_id,type=type,name=name,description=description,url_template=url_template,username=username,password=password,readonly=readonly,is_default=is_default,is_private=is_hidden,start_date=start_date,color=color)    
    #~ globals_dict.update(create_cal_calendar=create_cal_calendar)
    
    
    cal_Calendar= resolve_model("cal.Calendar")
    #~ cal_EventType = resolve_model("cal.EventType")
    def create_cal_eventtype(id, name, build_method, template, name_fr, name_en):
        return cal_Calendar(id=id,name=name,build_method=build_method,template=template,
          email_template='Default.eml.html',
          name_fr=name_fr,name_en=name_en)    
    globals_dict.update(create_cal_eventtype=create_cal_eventtype)
    
    def create_cal_calendar(id, user_id, type, name, description, 
        url_template, username, password, readonly, is_default, is_hidden, start_date, color):
        return None
        #~ return cal_Calendar(id=id,user_id=user_id,type=type,name=name,description=description,url_template=url_template,username=username,password=password,readonly=readonly,is_default=is_default,is_private=is_hidden,start_date=start_date,color=color)    
    globals_dict.update(create_cal_calendar=create_cal_calendar)
    
    def create_cal_accessclass(*args):
        return None
    globals_dict.update(create_cal_accessclass=create_cal_accessclass)
    
    
    objects = globals_dict['objects']
    def new_objects():
        from lino.modlib.households.fixtures import std
        yield std.objects()
        from lino.modlib.debts.fixtures import std
        yield std.objects()
        yield objects()
        from lino.modlib.cbss.fixtures import cbss
        yield cbss.objects()
        #~ from lino.modlib.cbss.fixtures import purposes
        #~ yield purposes.objects()
        #~ from lino.modlib.cbss.fixtures import inscodes
        #~ yield inscodes.objects()
    globals_dict.update(objects=new_objects)
    
    return '1.4.4'
            
def migrate_from_1_4_4(globals_dict): return '1.4.5'
def migrate_from_1_4_5(globals_dict): return '1.4.6'
def migrate_from_1_4_6(globals_dict): return '1.4.7'
def migrate_from_1_4_7(globals_dict): return '1.4.8'
def migrate_from_1_4_8(globals_dict): return '1.4.9'
def migrate_from_1_4_9(globals_dict): return '1.4.10'

