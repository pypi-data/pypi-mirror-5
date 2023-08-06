# -*- coding: UTF-8 -*-
## Copyright 2013 Luc Saffre
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
"""

import os
import cgi
import datetime

from django.db import models
#~ from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


from lino import mixins
from lino import dd

concepts = dd.resolve_app('concepts')

#~ contacts = dd.resolve_app('contacts')
#~ sales = dd.resolve_app('sales')

#~ class Person(contacts.Person,sales.Customer):
    #~ class Meta(contacts.Person.Meta):
        #~ app_label = 'contacts'

#~ class Company(contacts.Company,sales.Customer):
    #~ class Meta(contacts.Company.Meta):
        #~ app_label = 'contacts'

#~ def site_setup(site):
    #~ site.description = 
    
class Main(concepts.TopLevelConcepts):
    pass
    
    
def site_setup(site):
    site.modules.countries.Cities.required = dd.required(auth=False)
    site.modules.countries.Countries.required = dd.required(auth=False)
    site.modules.concepts.Concepts.required = dd.required(auth=False)
    
    site.modules.countries.Cities.set_detail_layout("""
    name country inscode 
    parent type id
    CitiesByCity
    """)
    
    site.modules.countries.Countries.set_detail_layout("""
    isocode name short_code inscode
    countries.CitiesByCountry
    """)
    
    