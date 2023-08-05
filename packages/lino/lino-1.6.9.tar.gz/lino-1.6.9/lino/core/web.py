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

"""

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import os
import cgi
import datetime
import inspect
import jinja2


from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
#~ from django.template.loaders import app_directories
from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist

from north import dbutils
from lino.utils import iif
from lino.utils.xmlgen import html as xghtml
E = xghtml.E
from jinja2.exceptions import TemplateNotFound

SUBDIR_NAME = 'templates_jinja'
    
def site_setup(sender,**kw):
    """
    Adds a `jinja_env` attribute to `settings.SITE`.
    This is being called from :func:`lino.ui.models.post_analyze`.
    
    Lino has an automatic and currently not configurable method 
    for building Jinja's template loader. It looks for 
    a "templates_jinja" 
    subfolder in the following places:
    
    - the directory where your settings.py is defined.
    
    """
    logger.debug("Setting up Jinja environment")
    self = sender
    from lino.utils import auth
    from django.utils.importlib import import_module
    
    paths = list(self.get_settings_subdirs(SUBDIR_NAME))
    
    loaders = []
    if len(paths) > 0:
        loaders.append(jinja2.FileSystemLoader(paths))
    
    for name in self.get_installed_apps():
        m = import_module(name)
        if os.path.isdir(os.path.join(os.path.dirname(m.__file__),SUBDIR_NAME)):
            loaders.append(jinja2.PackageLoader(name, SUBDIR_NAME))
    
    #~ loaders = reversed(loaders)
    #~ print 20130109, loaders
    
    self.jinja_env = jinja2.Environment(
        #~ extensions=['jinja2.ext.i18n'],
        loader=jinja2.ChoiceLoader(loaders))
    #~ jinja_env = jinja2.Environment(trim_blocks=False)

    #~ from django.utils import translation

    #~ jinja_env.install_gettext_translations(translation)


    def as_table(action_spec):
        a = settings.SITE.modules.resolve(action_spec)
        ar = a.request(user=auth.AnonymousUser.instance())
        ar.renderer = settings.SITE.ui.plain_renderer
        
        t = xghtml.Table()
        #~ t = doc.add_table()
        ar.ui.ar2html(ar,t,ar.sliced_data_iterator)
        
        #~ print ar.get_total_count()
        return E.tostring(t.as_element())
        #~ return E.tostring(E.ul(*[E.li(ar.summary_row(obj)) for obj in ar]),method="html")
          
    def as_ul(action_spec):
        a = settings.SITE.modules.resolve(action_spec)
        ar = a.request(user=auth.AnonymousUser.instance())
        ar.renderer = settings.SITE.ui.plain_renderer
        return E.tostring(E.ul(*[obj.as_list_item(ar) for obj in ar]))

    self.jinja_env.globals.update(
            settings=settings,
            # LINO=settings.SITE,
            #~ ui=settings.SITE.ui,
            site=self,
            dtos=dbutils.dtos,
            dtosl=dbutils.dtosl,
            as_ul=as_ul,
            as_table=as_table,
            iif=iif,
            unicode=unicode,
            len=len,
            E=E,
            _= _,
    )
    
    #~ print __file__, 20121231, self.jinja_env.list_templates('.html')


def extend_context(context):
    def parse(s):
        #~ print 20121221, s
        #~ return Template(s).render(**context)
        return settings.SITE.jinja_env.from_string(s).render(**context)
    context.update(
        now=datetime.datetime.now(),
        parse=parse,
        requested_language=get_language(),
        )

from lino.core import requests

def render_from_request(request,template_name,**context):
    extend_context(context)
    context.update(request=request)
    ar = requests.BaseRequest(
        renderer=settings.SITE.ui.ext_renderer,
        request=request)
    context.update(ar=ar)
    template = settings.SITE.jinja_env.get_template(template_name)
    return template.render(**context)


#~ jinja_env.extract_translations()


class DjangoJinjaTemplate:
  
    def __init__(self,jt):
        self.jt = jt
  
    def render(self, context):
        # flatten the Django Context into a single dictionary.
        #~ logger.info("20130118 %s",context)
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        extend_context(context_dict)
        context_dict.setdefault('request',None)
        #~ logger.info("20130118 %s",context_dict.keys())
        return self.jt.render(context_dict)  
  
  

#~ class Loader(app_directories.Loader):  
class Loader(BaseLoader):  
  
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        #~ source, origin = self.load_template_source(template_name, template_dirs)
        try:
            jt = settings.SITE.jinja_env.get_template(template_name)
        except TemplateNotFound as e:
            raise TemplateDoesNotExist(template_name)
        template = DjangoJinjaTemplate(jt)
        return template, None
          
          
    #~ get_template_from_string
