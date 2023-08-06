# -*- coding: UTF-8 -*-
## Copyright 2011,2013 Luc Saffre
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

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from lino.utils.instantiator import Instantiator, i2d
from north.dbutils import babelkw, babelitem

def objects():
    from lino import dd
    pcsw = dd.resolve_app('pcsw')
    
    #~ persongroup = Instantiator('pcsw.PersonGroup','name').build
    yield pcsw.PersonGroup(ref_name='1',name=_("Bilan"))
    yield pcsw.PersonGroup(ref_name='2',name=_("Formation"))
    yield pcsw.PersonGroup(ref_name='4',name=_("Recherche"))
    yield pcsw.PersonGroup(ref_name='4bis',name=_("Travail"))
    yield pcsw.PersonGroup(ref_name='9',name=_("Standby"))
    #~ yield persongroup(u"Bilan",ref_name='1')
    #~ yield persongroup(u"Formation",ref_name='2')
    #~ yield persongroup(u"Recherche",ref_name='4')
    #~ yield persongroup(u"Travail",ref_name='4bis')
    #~ yield persongroup(u"Standby",ref_name='9',active=False)

    yield pcsw.CoachingEnding(**babelkw('name',de="Übergabe an Kollege",fr="Transfert vers collègue"))
    yield pcsw.CoachingEnding(**babelkw('name',de="Einstellung des Anrechts auf SH",fr="Arret du droit à l'aide sociale"))
    yield pcsw.CoachingEnding(**babelkw('name',de="Umzug in andere Gemeinde",fr="Déménagement vers autre commune"))
    yield pcsw.CoachingEnding(**babelkw('name',de="Hat selber Arbeit gefunden",fr="A trouvé du travail"))
    
    yield pcsw.DispenseReason(**babelkw('name',de="Gesundheitlich",fr="Santé"))
    yield pcsw.DispenseReason(**babelkw('name',de="Studium/Ausbildung",fr="Etude/Formation"))
    yield pcsw.DispenseReason(**babelkw('name',de="Familiär",fr="Cause familiale"))
    yield pcsw.DispenseReason(**babelkw('name',de="Sonstige",fr="Autre"))
