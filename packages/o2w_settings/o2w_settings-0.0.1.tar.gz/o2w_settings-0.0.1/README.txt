===========
Default settings
===========

# In app/settings/common.py

#encoding:utf-8
import sys
from os.path import abspath, dirname, join, normpath
######### PATH CONFIGURATION
# Absolute filesystem path to this Django project directory.
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Add all necessary filesystem paths to our system path so that we can use
# python import statements.
sys.path.append(dirname(DJANGO_ROOT))
sys.path.append(normpath(join(DJANGO_ROOT, '../apps')))
sys.path.append(normpath(join(DJANGO_ROOT, '../libs')))
sys.path.append(normpath(join(DJANGO_ROOT, "lib", "python2.7", "site-packages")))
########## END PATH CONFIGURATION

import o2w.settings
o2w.settings.DJANGO_ROOT = DJANGO_ROOT
from o2w.settings.common import *




# In app/settings/dev.py

from common import *
from o2w.settings.dev import *


# In app/settings/prod.py

from common import *
from o2w.settings.prod import *
