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

Inspired by Frederik Lundh's ElementTree Builder
<http://effbot.org/zone/element-builder.htm>


>>> ns = Namespace('http://my.ns',
...    "bar baz bar-o-baz foo-bar class def")

>>> bob = ns.bar_o_baz()
>>> baz = ns.add_child(bob,'baz',class_='first')
>>> print ns.tostring(baz)
<baz xmlns="http://my.ns" class="first" />

>>> bob = ns.bar_o_baz('Hello',class_='first',foo_bar="3")
>>> print ns.tostring(bob)
<bar-o-baz xmlns="http://my.ns" class="first" foo-bar="3">Hello</bar-o-baz>


"""

import datetime
from functools import partial

#~ from xml.etree import ElementTree as ET
from lino.utils.xmlgen import etree
#~ from lino.utils import Warning
from django.utils.functional import Promise
from django.utils.encoding import force_unicode


def pretty_print(elem):
    """Return a pretty-printed XML string for the Element.
    """
    return prettify(etree.tostring(elem, 'utf-8'))
    # the following also indented:
    # from http://renesd.blogspot.com/2007/05/pretty-print-xml-with-python.html
    # via http://broadcast.oreilly.com/2010/03/pymotw-creating-xml-documents.html
    #~ from xml.dom import minidom
    #~ rough_string = etree.tostring(elem, 'utf-8')
    #~ reparsed = minidom.parseString(rough_string)
    #~ return reparsed.toprettyxml(indent="  ")

def prettify(s):
    return s.replace('><','>\n<')


RESERVED_WORDS = frozenset("""
and       del       from      not       while
as        elif      global    or        with
assert    else      if        pass      yield
break     except    import    print
class     exec      in        raise
continue  finally   is        return
def       for       lambda    try
""".split())

TYPEMAP = {
  #~ datetime.datetime: py2str,
  #~ IncompleteDate : lambda e,v : str(v),
  datetime.datetime: lambda e,v : v.strftime("%Y%m%dT%H%M%S"),
  datetime.date: lambda e,v : v.strftime("%Y-%m-%d"),
  int: lambda e,v : str(v),
}




class Namespace(object):
    """
    """
    prefix = None
    targetNamespace = None
    names = None
    
    def __init__(self,targetNamespace=None,names=None,prefix=None):
        #~ if prefix is not None:
            #~ self.prefix = prefix
        #~ kw.setdefault('typemap',TYPEMAP)
        #~ kw.setdefault('makeelement',self.makeelement)
        #~ nsmap = kw.setdefault('nsmap',{})
        
        
        if prefix is not None:
            self.prefix = prefix
        if names is not None:
            self.names = names
        if targetNamespace is not None:
            self.targetNamespace = targetNamespace
        if self.targetNamespace is not None:
            #~ kw.update(namespace=self.targetNamespace)
            
            self._ns = '{' + self.targetNamespace + '}'
            if self.prefix is not None:
                etree.register_namespace(self.prefix,self.targetNamespace)
            #~ if prefix:
            #~ nsmap[prefix] = self.targetNamespace
        #~ if used_namespaces is not None:
            #~ self.used_namespaces = used_namespaces
        #~ if self.used_namespaces is not None:
            #~ for ns in self.used_namespaces:
                #~ nsmap[ns.prefix] = ns.targetNamespace
        #~ self._element_maker = ElementMaker(**kw)
        #~ self._source_elements = {}
        if self.names is not None:
            self.define_names(self.names)
        self.setup_namespace()
        
    def iselement(self,*args,**kw):
        return etree.iselement(*args,**kw)

    def setup_namespace(self):
        pass
        
    def tostring(self,element,*args,**kw):
        class dummy:
            pass
        data = []
        file = dummy()
        file.write = data.append
        if self.targetNamespace is not None:
            kw.setdefault('default_namespace',self.targetNamespace)
        etree.ElementTree(element).write(file,*args,**kw)
        return "".join(data)
        
    def tostring_pretty(self,*args,**kw):
        #~ kw.setdefault('xml_declaration',False)
        #~ kw.setdefault('encoding','utf-8')
        #~ kw.update(xml_declaration=False)
        #~ kw.update(encoding='utf-8')
        s = self.tostring(*args,**kw)
        #~ return s
        #~ return minidom.parseString(s).toprettyxml(indent="  ")
        return prettify(s)
        
        
        
    def addns(self,tag):
        if self.targetNamespace is None or tag[0] == "{":
            return tag
        return self._ns + tag
        
    def makeattribs(self,**kw):
        #~ ns = self._element_maker._namespace
        #~ if ns is None: return kw
        xkw = dict()
        for k,v in kw.items():
            k = getattr(self,k).args[0] # convert iname to tagname
            xkw[self.addns(k)] = v
        return xkw
        
    def create_element(self, tag, *children, **attrib):
        nsattrib = self.makeattribs(**attrib)
        tag = self.addns(tag)
        elem = etree.Element(tag, nsattrib)
        for item in children:
            if isinstance(item, Promise):
                item = force_unicode(item)
            if isinstance(item, dict):
                elem.attrib.update(self.makeattribs(**item))
            elif isinstance(item, basestring):
                if len(elem):
                    elem[-1].tail = (elem[-1].tail or "") + item
                else:
                    elem.text = (elem.text or "") + item
            elif etree.iselement(item):
                elem.append(item)
            else:
                raise TypeError("bad argument: %r" % item)
        return elem
        
    
    def define_names(self,names):
        for tag in names.split():
            iname = tag.replace("-","_")
            iname = iname.replace(".","_")
            #~ if iname in ('class','for','in','def'):
            if iname in RESERVED_WORDS:
                iname += "_"
            #~ setattr(self,iname,getattr(self._element_maker,name))
            p = partial(self.create_element, tag)
            setattr(self,iname,p)

    def getnsattr(self,elem,name):
        #~ if self.targetNamespace is None or name.startswith('{'):
            #~ return elem.get(name)
        return elem.get(self._element_maker._namespace + name)
        
        
    #~ def update_attribs(self,root,**kw):
    def update(self,root,**kw):
        root.attrib.update(self.makeattribs(**kw))
            
    def add_child(self,parent,_name,*args,**kw):
        ecl = getattr(self,_name)
        #~ kw = self.makeattribs(**kw)
        #~ print 20120420, kw
        e = ecl(*args,**kw)
        parent.append(e)
        return e
        
RAW = etree.XML



def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

