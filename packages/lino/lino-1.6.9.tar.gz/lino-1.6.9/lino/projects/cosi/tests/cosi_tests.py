# -*- coding: utf-8 -*-
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
This module contains "quick" tests that are run on a demo database 
without any fixture. You can run only these tests by issuing::

  python manage.py test ui.QuickTest

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import six

from django.conf import settings

from django.utils import translation
from django.utils.encoding import force_unicode
from django.core.exceptions import ValidationError

from lino import dd

from djangosite.utils.djangotest import RemoteAuthTestCase

partners = dd.resolve_app(settings.SITE.partners_app_label)

class QuickTest(RemoteAuthTestCase):
    
    def test00(self):
        """
        Initialization.
        """
        #~ print "20130321 test00 started"
        self.user_root = settings.SITE.user_model(username='root',language='en',profile='900')
        self.user_root.save()
        
                
        #~ def test01(self):
        self.assertEqual(1+1,2)
        o1 = partners.Organisation(name="Example")
        o1.save()
        o2 = partners.Organisation(name="Example")
        o2.save()
        
        p1 = partners.Person(first_name="John",last_name="Doe")
        p1.save()
        p2 = partners.Person(first_name="Johny",last_name="Doe")
        p2.save()
        
        partners.Contact(person=p1,organisation=o1).save()
        partners.Contact(person=p2,organisation=o2).save()
        
        s = partners.ContactsByOrganisation.request(o1).to_rst()
        #~ six.print_('\n'+s)
        self.assertEqual(s,"""\
========== ================ ====
 Person     Contact Person   ID
---------- ---------------- ----
 Doe John                    1
========== ================ ====
""")
        
        s = partners.ContactsByOrganisation.request(o2).to_rst()
        #~ six.print_('\n'+s)
        self.assertEqual(s,"""\
=========== ================ ====
 Person      Contact Person   ID
----------- ---------------- ----
 Doe Johny                    2
=========== ================ ====
""")
        url = "/api/partners/Persons/115?fv=115&fv=fff&an=merge_row"
        #~ self.fail("TODO: execute a merge action using the web interface")
        res = self.client.get(url,REMOTE_USER='root')
        

        """
        20130418 server traceback caused when a pdf view of a table was 
        requested through the web interface.
        TypeError: get_handle() takes exactly 1 argument (2 given)
        """
        url = settings.SITE.build_admin_url('api/countries/Countries?cw=189&cw=189&cw=189&cw=45&cw=45&cw=36&ch=&ch=&ch=&ch=&ch=&ch=&ci=name&ci=name_de&ci=name_fr&ci=isocode&ci=short_code&ci=iso3&name=0&fmt=pdf')
        msg = 'Using remote authentication, but no user credentials found.'
        try:
            response = self.client.get(url) 
            self.fail("Expected '%s'" % msg)
        except Exception as e:
            self.assertEqual(str(e),msg)
            
        response = self.client.get(url,REMOTE_USER='foo') 
        self.assertEqual(response.status_code,403,"Status code for anonymous on GET %s" % url)
        from appy.pod import PodError

        try:
            response = self.client.get(url,REMOTE_USER='root')
            result = self.check_json_result(response,'',url)
            print result
        except PodError as e: 
            pass
            #~ self.assertEqual(str(e), PodError: Extension of result file is "pdf".



