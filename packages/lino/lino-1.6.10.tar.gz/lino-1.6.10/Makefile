#~ DJANGO_ADMIN = python l:/snapshots/django/django/bin/django-admin.py
#~ DJANGO_ADMIN = `python -c 'import os; from django import bin;print os.path.dirname(bin.__file__)'`/django-admin.py
DJANGO_ADMIN=python $(shell python -c "from os.path import join,dirname; from django import bin;print join(dirname(bin.__file__),'django-admin.py')")
DJANGO_ADMIN := $(shell cygpath -m $(DJANGO_ADMIN))
LINO_ROOT=$(shell python -c "from os.path import join,dirname,abspath; import lino;print abspath(join(dirname(lino.__file__),'..'))")
#LINO_ROOT := /cygdrive/t/hgwork/lino
#LINO_ROOT := `cygpath -m $(LINO_ROOT)`
LINO_ROOT := $(shell cygpath -m $(LINO_ROOT))
APPS = cosi 
MODULES = vat accounts ledger households outbox \
  cal products properties contacts countries notes \
  sales finan uploads users postings about concepts
TESTS_OPTIONS = --verbosity=2 --traceback
MMOPTS := -s -a --settings lino.projects.sphinxdocs.settings
CMOPTS := --settings lino.projects.sphinxdocs.settings

.PHONY: mm cm makedocs tests sdist

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  mm     run django-admin makemessages on modlib"
	@echo "  cm     run django-admin compilemessages on modlib"
	@echo "  tests  run Lino test suite"
  

mm:
	pwd
	cd $(LINO_ROOT)/lino && $(DJANGO_ADMIN) makemessages -i 'sandbox*' -i 'modlib*' -i 'apps*' -i 'test_apps*' $(MMOPTS)
	for MOD in $(MODULES); do \
	  cd $(LINO_ROOT)/lino/modlib/$$MOD && pwd && $(DJANGO_ADMIN) makemessages $(MMOPTS); \
	done
	for i in $(APPS); do \
    cd $(LINO_ROOT)/lino/projects/$$i && pwd && $(DJANGO_ADMIN) makemessages $(MMOPTS); \
	done
  

cm:  
	cd $(LINO_ROOT)/lino && $(DJANGO_ADMIN) compilemessages $(CMOPTS)
	@for MOD in $(MODULES); \
	do \
	  cd $(LINO_ROOT)/lino/modlib/$$MOD && $(DJANGO_ADMIN) compilemessages $(CMOPTS); \
	done
	for i in $(APPS); do \
	  cd $(LINO_ROOT)/lino/projects/$$i && $(DJANGO_ADMIN) compilemessages $(CMOPTS); \
	done
  
tests:  
	#~ python lino/utils/__init__.py
	#~ python lino/utils/sphinx.py
	#~ python lino/utils/rstgen.py
	python lino/utils/html2odf.py
	python lino/utils/memo.py
	python lino/modlib/contacts/utils.py
	python lino/utils/html2xhtml.py
	python lino/utils/demonames.py
	python lino/utils/odsreader.py
	export DJANGO_SETTINGS_MODULE=lino.projects.std.settings ; python lino/utils/ssin.py
	export DJANGO_SETTINGS_MODULE=lino.projects.std.settings ; python lino/core/choicelists.py
	export DJANGO_SETTINGS_MODULE=lino.projects.std.settings ; python lino/utils/jsgen.py
	export DJANGO_SETTINGS_MODULE=lino.projects.std.settings ; python lino/utils/ranges.py
	export DJANGO_SETTINGS_MODULE=lino.projects.std.settings ; python lino/modlib/ledger/utils.py
	export DJANGO_SETTINGS_MODULE=lino.projects.std.settings ; python lino/modlib/accounts/utils.py
	#~ $(DJANGO_ADMIN) test --settings=lino.test_apps.mti.settings  $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.test_apps.nomti.settings  $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.test_apps.20100212.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.test_apps.integer_pk.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.test_apps.quantityfield.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.test_apps.human.settings $(TESTS_OPTIONS)
	#~ $(DJANGO_ADMIN) test --settings=lino.projects.std.settings
	#~ $(DJANGO_ADMIN) test --settings=lino.projects.pcsw.settings $(TESTS_OPTIONS)
	#~ $(DJANGO_ADMIN) test --settings=lino.projects.igen.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.cosi.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.presto.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.babel_tutorial.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.polls_tutorial.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.belref.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.events.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.homeworkschool.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.min1.settings $(TESTS_OPTIONS)
	$(DJANGO_ADMIN) test --settings=lino.projects.min2.settings $(TESTS_OPTIONS)
	#~ cd $(LINO_ROOT)/lino/projects/uiless && export DJANGO_SETTINGS_MODULE= && pwd && python manage.py test

qt:  
	cd $(LINO_ROOT)/lino/projects/uiless && export DJANGO_SETTINGS_MODULE= && pwd && python manage.py test

unused_appdocs:
	$(DJANGO_ADMIN) makedocs --settings lino.projects.pcsw.settings docs/pcsw/appdocs
	$(DJANGO_ADMIN) makedocs --settings lino.projects.igen.settings docs/igen/appdocs

sdist:
	python setup.py sdist --formats=gztar,zip --dist-dir=docs/dl
	#~ python setup.py register sdist --formats=gztar,zip --dist-dir=docs/dist upload 
	#~ python setup.py sdist --formats=gztar,zip --dist-dir=docs/dist
  
upload:
	python setup.py sdist --formats=gztar,zip --dist-dir=docs/dl upload 
