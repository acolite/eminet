from .nc_write import nc_write
from .nc_read import *
from .eminet_models import eminet_models

import os
path = os.path.dirname(os.path.abspath(__file__))

config = {'data_path':'{}/data'.format(os.path.dirname(path))}
