# Copyright 2013 Gridcentric Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys
import glob
from distutils.core import setup

VERSION = os.environ.get("VERSION", '0.1')

setup(name='canary_python_novaclient_ext',
      version=VERSION,
      description='Monitoring tools for Nova hosts.',
      author='Gridcentric Inc.',
      author_email='support@gridcentric.com',
      url='http://www.gridcentric.com/',
      packages=['canary_python_novaclient_ext'])
