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

import os
import site
import sys

import jinja2


def _get_template_dirs(type="plugin"):
    """Return a list of directories where templates may be located.
    """
    template_dirs = [
        os.path.expanduser(os.path.join("~", ".rapport", "templates", type)),
        os.path.join("rapport", "templates", type)  # Local dev tree
    ] + map(lambda d: os.path.join(d, "rapport", "templates", type), site.getsitepackages())
    return template_dirs


_JINJA2_ENV = {}


def init():
    for type in ["plugin", "email", "web"]:
        loader = jinja2.FileSystemLoader(_get_template_dirs(type))
        env = jinja2.Environment(loader=loader,
                                 extensions=["jinja2.ext.i18n", "jinja2.ext.loopcontrols"],
                                 line_statement_prefix="%%",
                                 line_comment_prefix="##",
                                 trim_blocks=True)
        env.install_null_translations(newstyle=False)
        _JINJA2_ENV[type] = env


def get_template(name, format="text", type="plugin"):
    if not _JINJA2_ENV:
        init()
    template_name = "{0}.{1}.jinja2".format(name, format)
    try:
        return _JINJA2_ENV[type].get_template(template_name)
    except jinja2.TemplateNotFound as e:
        print >>sys.stderr, "Missing template {0}/{1}!".format(type, template_name)
