from lino.projects.presto.settings import *
SITE = Site(globals(),no_local=True,remote_user_header='REMOTE_USER') 
DEBUG=True
#~ SITE.remote_user_header = 'REMOTE_USER'


