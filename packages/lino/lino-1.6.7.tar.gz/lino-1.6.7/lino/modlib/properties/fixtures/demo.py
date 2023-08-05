# -*- coding: UTF-8 -*-
## Copyright 2011 Luc Saffre
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


from django.utils.translation import ugettext as _

from lino.utils.instantiator import Instantiator
from north.dbutils import babel_values

def objects():
    ptype = Instantiator('properties.PropType').build
    
    division = ptype(**babel_values('name',**dict(en="Division",fr="Division",de=u"Abteilung")))
    yield division
    divchoice = Instantiator('properties.PropChoice','value',type=division).build
    yield divchoice('1',**babel_values('text',**dict(en="Furniture",de=u"Möbel",fr=u"Meubles")))
    yield divchoice('2',**babel_values('text',**dict(en="Web hosting",de=u"Hosting",fr=u"Hosting")))
  
