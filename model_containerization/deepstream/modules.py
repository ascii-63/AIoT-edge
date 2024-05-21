import sys
sys.path.append('../')

import gi
import configparser

gi.require_version('Gst', '1.0')
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst ,GstRtspServer

from os import path
import os.path
import os
import pyds
from common.FPS import PERF_DATA
from common.bus_call import bus_call
from common.is_aarch_64 import is_aarch64
from common.utils import long_to_uint64

import math
from ctypes import *
import shutil
from datetime import datetime

import config
import metadata