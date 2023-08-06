# -*- coding: UTF-8 -*-
## Copyright 2012-2013 Luc Saffre
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


from lino.utils.instantiator import Instantiator, i2d
from lino.utils import Cycler
from lino.core.dbutils import resolve_model
# from django.utils.translation import ugettext_lazy as _

#~ from django.db import models
from north.dbutils import babel_values
#~ from lino.core.perms import UserProfiles

from lino import dd

def objects():
  
    #~ from lino.modlib.users.models import 
    from lino_welfare.modlib.newcomers.models import Broker, Faculty, Competence
    from lino_welfare.modlib.contacts.models import Person
    from lino_welfare.modlib.pcsw import models as pcsw
    
    I = Instantiator(Broker).build
    #~ yield I(**babel_values('name',
        #~ de=u"Polizei", fr=u"Police",en=u"Police"))
    #~ yield I(**babel_values('name',
        #~ de=u"Jugendgericht", fr=u"Jugendgericht",en=u"Jugendgericht"))
    yield I(name="Police")
    yield I(name="Other PCSW")

    I = Instantiator(Faculty).build
    yield I(weight=10,**babel_values('name', de=u"Eingliederungseinkommen (EiEi)", fr=u"Revenu d'intégration sociale (RIS)",  en=u"EiEi"))
    yield I(weight=5,**babel_values('name', de=u"DSBE",                    fr=u"Service d'insertion socio-professionnelle",   en=u"DSBE"))
    yield I(weight=4,**babel_values('name', de=u"Ausländerbeihilfe",       fr=u"Aide sociale équivalente (pour étrangers)",en=u"Ausländerbeihilfe"))
    yield I(weight=6,**babel_values('name', de=u"Finanzielle Begleitung",  fr=u"Accompagnement budgétaire",     en=u"Finanzielle Begleitung"))
    yield I(weight=2,**babel_values('name', de=u"Laufende Beihilfe",       fr=u"Aide complémenataire",       en=u"Laufende Beihilfe"))
    
    
    #~ User = resolve_model('users.User')
    #~ yield User(username="caroline",
        #~ first_name="Caroline",last_name="Carnol",
        #~ profile='200') # UserProfiles.caroline)
    
    #~ FACULTIES = Cycler(Faculty.objects.all())
    #~ profiles = [p for p in UserProfiles.items() if p.integ_level]
    #~ USERS = Cycler(User.objects.filter(profile__in=profiles))
    #~ for i in range(7):
        #~ yield Competence(user=USERS.pop(),faculty=FACULTIES.pop())
    #~ for p in pcsw.Client.objects.filter(client_state=pcsw.ClientStates.new):
        #~ p.faculty = FACULTIES.pop()
        #~ p.save()
        
        
        
    newcomers = dd.resolve_app('newcomers')
    users = dd.resolve_app('users')
    
    QUOTAS = Cycler(100,60,50,20)
    FACULTIES = Cycler(newcomers.Faculty.objects.all())
    
    profiles = [p for p in dd.UserProfiles.items() if p.integ_level and p.level < dd.UserLevels.admin]
    qs = users.User.objects.filter(profile__in=profiles)
    for u in qs:
        u.newcomer_quota = QUOTAS.pop()
        yield u
        
    USERS = Cycler(qs)
    for i in range(7):
        yield newcomers.Competence(user=USERS.pop(),faculty=FACULTIES.pop())
        
    for p in pcsw.Client.objects.exclude(client_state=pcsw.ClientStates.former):
        p.faculty = FACULTIES.pop()
        p.save()

        
