import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('../'))
from conf import *

html_context = {**html_context, 'conf_py_path': '/main/'}
