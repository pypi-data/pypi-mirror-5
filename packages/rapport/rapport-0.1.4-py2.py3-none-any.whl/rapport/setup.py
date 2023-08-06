# Copyright 2013 Sascha Peilicke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os
import re
import shutil
import subprocess
import sys
from distutils.core import Command


class PEP257Command(Command):
    description = "Run pep257 with custom options"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.call("find rapport -type f -name \"*.py\" | xargs pep257", shell=True)


class CleanupCommand(Command):
    patterns = [".coverage", ".tox", ".venv", "build", "dist", "*.egg", "*.egg-info"]
    description = "Clean up project directory"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for pattern in CleanupCommand.patterns:
            for f in glob.glob(pattern):
                if os.path.isdir(f):
                    shutil.rmtree(f, ignore_errors=True)
                else:
                    os.remove(f)


def get_cmdclass():
    """Dictionary of all distutils commands defined in this module.
    """
    return {"cleanup": CleanupCommand,
            "pep257": PEP257Command}


def parse_requirements(requirements_file='requirements.txt'):
    requirements = []
    with open(requirements_file, 'r') as f:
        for line in f:
            # For the requirements list, we need to inject only the portion
            # after egg= so that distutils knows the package it's looking for
            # such as:
            # -e git://github.com/openstack/nova/master#egg=nova
            if re.match(r'\s*-e\s+', line):
                requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1',
                                    line))
            # such as:
            # http://github.com/openstack/nova/zipball/master#egg=nova
            elif re.match(r'\s*https?:', line):
                requirements.append(re.sub(r'\s*https?:.*#egg=(.*)$', r'\1',
                                    line))
            # -f lines are for index locations, and don't get used here
            elif re.match(r'\s*-f\s+', line):
                pass
            # -r lines are for including other files, and don't get used here
            elif re.match(r'\s*-r\s+', line):
                pass
            # argparse is part of the standard library starting with 2.7
            # adding it to the requirements list screws distro installs
            elif line == 'argparse' and sys.version_info >= (2, 7):
                pass
            else:
                requirements.append(line.strip())
    return requirements
