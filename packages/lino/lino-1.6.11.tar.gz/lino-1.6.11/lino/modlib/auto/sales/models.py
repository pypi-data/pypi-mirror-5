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
Deserves a docstring.
"""

from __future__ import unicode_literals


import logging
logger = logging.getLogger(__name__)

import os
import datetime

from django.db import models
from django.db.models import Q
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils.translation import string_concat
from django.utils.encoding import force_unicode 
from django.utils.functional import lazy

from django.contrib.contenttypes.models import ContentType

#~ import lino
#~ logger.debug(__file__+' : started')
#~ from django.utils import translation


#~ from lino import reports
from lino import dd

#~ sales = dd.resolve_app('sales')
#~ contacts = dd.resolve_app('contacts')

#~ dd.extends_app('lino.modlib.sales',globals())

from lino.modlib.sales.models import *
#~ PARENT_APP = 'lino.modlib.sales'

#~ from lino.modlib.sales import models as PARENT_APP
#~ from lino.modlib.sales import models as sales
#~ from lino.modlib.sales import models as CONFIG_PARENT
#~ CONFIG_PARENT = sales # inherit `config` subdir


class Invoiceable(dd.Model):
    """
    Mixin for things that are "invoiceable", i.e. for which a customer
    is going to get an invoice.
    """
    invoiceable_date_field = ''
    """
    The name of the field which holds the invoiceable date.
    """
    
    invoiceable_partner_field = ''
    """
    The name of the field which holds the invoiceable partner.
    """
    
    class Meta:
        abstract = True
        
    invoice = dd.ForeignKey('sales.Invoice',
        #~ verbose_name=_("Invoice"),
        blank=True,null=True)

    def get_invoiceable_product(self): return None
    def get_invoiceable_qty(self): return None
    def get_invoiceable_title(self): return unicode(self)
        
    @classmethod
    def get_invoiceables_for(cls,partner,max_date=None):
        #~ logger.info('20130711 get_invoiceables_for (%s,%s)', partner, max_date)
        for m in dd.models_by_base(cls):
            fkw = dict()
            fkw[m.invoiceable_partner_field] = partner
            fkw.update(invoice__isnull=True)
            #~ if max_date is not None:
                #~ fkw["%s__lte" % m.invoiceable_date_field] = max_date
            #~ logger.info('20130711 %s %s', m, fkw)
            for obj in m.objects.filter(**fkw).order_by(m.invoiceable_date_field):
                yield obj
        
    @classmethod
    def get_invoiceables_count(cls,partner,max_date=None):
        #~ logger.info('20130711 get_invoiceables_count (%s,%s)', partner, max_date)
        n = 0
        for m in dd.models_by_base(cls):
            fkw = dict()
            fkw[m.invoiceable_partner_field] = partner
            fkw.update(invoice__isnull=True)
            #~ if max_date is not None:
                #~ fkw["%s__lte" % m.invoiceable_date_field] = max_date
            #~ logger.info('20130711 %s %s', m, fkw)
            n += m.objects.filter(**fkw).count()
        return n
        



#~ class FillInvoice(dd.RowAction):
    #~ label = _("Fill")
    #~ help_text = _("Fill this invoice using invoiceable items")
    #~ 
    #~ def run_from_ui(self,obj,ar,**kw):
        #~ L = list(Invoiceable.get_invoiceables_for(obj.partner,obj.date))
        #~ if len(L) == 0:
            #~ return ar.error(_("No invoiceables found for %s.") % obj.partner)
        #~ def ok():
            #~ for ii in L:
                #~ i = InvoiceItem(voucher=obj,invoiceable=ii,
                    #~ product=ii.get_invoiceable_product(),
                    #~ qty=ii.get_invoiceable_qty())
                #~ i.product_changed(ar)
                #~ i.full_clean()
                #~ i.save()
            #~ kw.update(refresh=True)
            #~ return kw
        #~ msg = _("This will add %d invoice items.") % len(L)
        #~ return ar.confirm(ok, msg, _("Are you sure?"))
        
class CreateInvoiceForPartner(dd.RowAction):
    "CreateInvoiceForPartner"
    label = _("Create invoice")
    help_text = _("Create invoice for this partner using invoiceable items")
    
    def run_from_ui(self,obj,ar,**kw):
        L = list(Invoiceable.get_invoiceables_for(obj))
        if len(L) == 0:
            return ar.error(_("No invoiceables found for %s.") % obj)
        def ok():
            jnl = Invoice.get_journals()[0]
            invoice = Invoice(partner=obj,journal=jnl,date=datetime.date.today())
            invoice.save()
            for ii in L:
                i = InvoiceItem(voucher=invoice,invoiceable=ii,
                    product=ii.get_invoiceable_product(),
                    qty=ii.get_invoiceable_qty())
                i.product_changed(ar)
                i.full_clean()
                i.save()
            #~ kw.update(refresh=True)
            js = ar.renderer.instance_handler(ar,invoice)
            kw.update(eval_js=js)
            return kw
        msg = _("This will create an invoice for %s.") % obj
        return ar.confirm(ok, msg, _("Are you sure?"))
        
    
    
class Invoice(Invoice): # 20130709
    
    #~ fill_invoice = FillInvoice()
    
    class Meta(Invoice.Meta): # 20130709
        #~ app_label = 'sales'
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        
    def register(self,ar):
        for i in self.items.filter(invoiceable_id__isnull=False):
            if i.invoiceable.invoice != self:
                i.invoiceable.invoice = self
                i.invoiceable.save()
                #~ logger.info("20130711 %s now invoiced",i.invoiceable)
        return super(Invoice,self).register(ar)
        
    def deregister(self,ar):
        for i in self.items.filter(invoiceable_id__isnull=False):
            if i.invoiceable.invoice != self:
                logger.warning("Oops: i.invoiceable.invoice != self in %s",self)
            i.invoiceable.invoice = None
            i.invoiceable.save()
            #~ logger.info("20130711 %s no longer invoiced",i.invoiceable)
        return super(Invoice,self).deregister(ar)
        
    
class InvoiceItem(InvoiceItem): # 20130709
    
    invoiceable_label = _("Invoiceable")
    
    class Meta(InvoiceItem.Meta): # 20130709
        #~ app_label = 'sales'
        verbose_name = _("Voucher item")
        verbose_name_plural = _("Voucher items")
    
    
    invoiceable_type = dd.ForeignKey(ContentType,
        editable=False,blank=True,null=True,
        verbose_name=string_concat(invoiceable_label,' ',_('(type)')))
    invoiceable_id = dd.GenericForeignKeyIdField(
        invoiceable_type,
        editable=False,blank=True,null=True,
        verbose_name=string_concat(invoiceable_label,' ',_('(object)')))
    invoiceable = dd.GenericForeignKey(
        'invoiceable_type', 'invoiceable_id',
        verbose_name=invoiceable_label)
    
    #~ @dd.chooser()
    #~ def enrolment_choices(self,voucher):
        #~ Enrolment = dd.resolve_model('school.Enrolment')
        #~ # print 20130605, voucher.partner.pk
        #~ return Enrolment.objects.filter(pupil__id=voucher.partner.pk).order_by('request_date')
        #~ 
    #~ def enrolment_changed(self,ar):
        #~ if self.enrolment is not None and self.enrolment.course is not None:
            #~ self.product = self.enrolment.course.tariff
        #~ self.product_changed(ar)
        
    def product_changed(self,ar):
        super(InvoiceItem,self).product_changed(ar)
        if self.invoiceable:
            self.title = self.invoiceable.get_invoiceable_title()
        
    
class ItemsByInvoice(ItemsByInvoice): # 20130709
    #~ app_label = 'sales' # we want to "override" the original table

    column_names = "invoiceable product title description:20x1 discount unit_price qty total_incl total_base total_vat"
    
    #~ @classmethod
    #~ def get_choices_text(self,obj,request,field):
        #~ if field.name == 'enrolment':
            #~ return unicode(obj.course)
        #~ # raise Exception("20130607 field.name is %r" % field.name)
        #~ return super(ItemsByInvoice,self).get_choices_text(obj,field,request)
    
class InvoicingsByInvoiceable(InvoiceItemsByProduct): # 20130709
    #~ app_label = 'sales'
    master_key = 'invoiceable'
    editable = False
    
#~ sales.ItemsByInvoice.column_names = "enrolment product title description:20x1 discount unit_price qty total_incl total_base total_vat"
    


contacts = dd.resolve_app('contacts')

#~ contacts.Partners.

class InvoiceablePartners(contacts.Partners):
    """
    TODO: read https://docs.djangoproject.com/en/dev/topics/db/aggregation/
    """
    label = _("Invoiceable partners")
    help_text = _("Table of all partners who have at least one invoiceable item.")
    model = 'contacts.Partner'
    create_invoice = CreateInvoiceForPartner()
    
    #~ @classmethod
    #~ def get_data_rows(self,ar):
        #~ qs = settings.SITE.modules.contacts.Partner.objects.all()
        #~ lst = []
        #~ for obj in qs:
            #~ if Invoiceable.get_invoiceables_count(obj) > 0:
                #~ lst.append(obj)
        #~ return lst
        
    @classmethod
    def get_request_queryset(self,ar):
        qs = super(InvoiceablePartners,self).get_request_queryset(ar)
        flt = Q()
        for m in dd.models_by_base(Invoiceable):
            subquery = m.objects.filter(invoice__isnull=True).values(m.invoiceable_partner_field+'__id')
            flt = flt | Q(id__in=subquery)
        return qs.filter(flt)
        
        #~ for m in dd.models_by_base(Invoiceable):
            #~ mname = full_model_name(m,'_')
            #~ qs = qs.annotate(mname+'_count'=Count(mname))
            #~ flt = flt | Q(**{mname+'_count__gt':0})
        #~ qs = qs.filter(flt)
            #~ fkw = dict()
            #~ fkw[m.invoiceable_partner_field] = partner
            #~ fkw.update(invoice__isnull=True)
            #~ items = m.objects.filter(**fkw).aggregate(models.Count())
        
        #~ return qs
    
class InvoiceablesByPartner(dd.VirtualTable):
    label = _("Invoiceables")
    #~ app_label = 'sales'
    master = 'contacts.Partner'
    column_names = 'date info'
    
    @classmethod
    def get_data_rows(self,ar):
        rows = []
        mi = ar.master_instance
        if mi is None:
            return rows
        for obj in Invoiceable.get_invoiceables_for(mi):
            rows.append((getattr(obj,obj.invoiceable_date_field),obj))
        
        #~ for m in dd.models_by_base(Invoiceable):
            #~ fkw = {m.invoiceable_partner_field:mi}
            #~ for obj in m.objects.filter(**fkw).order_by(m.invoiceable_date_field):
                #~ rows.append((getattr(obj,m.invoiceable_date_field),obj))
        def f(a,b): return cmp(a[0],b[0])
        rows.sort(f)
        return rows
        
    @dd.virtualfield(models.DateField(_("Date")))
    def date(self,row,ar):
        return row[0]
    
    @dd.displayfield(_("Invoiceable"))
    def info(self,row,ar):
        return ar.obj2html(row[1])
    



#~ f = setup_main_menu
def setup_main_menu(site,ui,profile,m): 
    #~ f(site,ui,profile,m)
    m = m.add_menu("sales",MODULE_LABEL)
    m.add_action('sales.InvoiceablePartners')
