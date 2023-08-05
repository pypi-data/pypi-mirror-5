# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from osbuild import distro
from osbuild import utils

config_dir = None
docs_dir = None
logs_dir = None
install_dir = None
lib_dir = None
share_dir = None
bin_dir = None
etc_dir = None
libexec_dir = None
package_files = None
system_lib_dirs = None
home_dir = None
build_state_dir = None
log_path = None
git_user_name = None
git_email = None

_source_dir = None
_prefs_path = None


class Module:
    def __init__(self, info):
        self.name = info["name"]
        self.repo = info["repo"]
        self.branch = info.get("branch", "master")
        self.tag = info.get("tag", None)
        self.auto_install = info.get("auto-install", False)
        self.options = info.get("options", [])
        self.options_evaluated = info.get("options_evaluated", [])
        self.has_checks = info.get("has_checks", False)
        self.no_libdir = info.get("no_libdir", False)
        self.makefile_name = info.get("makefile_name", "Makefile")
        self.has_docs = info.get("has_docs", False)
        self.docs_dir = info.get("docs_dir", self.name)

    def get_source_dir(self):
        return os.path.join(get_source_dir(), self.name)

    def get_build_system(self):
        source_dir = self.get_source_dir()

        package_json = os.path.join(source_dir, "package.json")

        if os.path.exists(package_json):
            with open(package_json) as f:
                parsed_json = json.load(f)
                if "volo" in parsed_json:
                    return "volo"
                else:
                    return "npm"
        elif os.path.exists(os.path.join(source_dir, "setup.py")):
            return "distutils"
        elif (os.path.exists(os.path.join(source_dir, "autogen.sh")) or
              os.path.exists(os.path.join(source_dir, "configure"))):
            return "autotools"
        else:
            return None

def setup(**kwargs):
    global config_dir
    config_dir = kwargs.get("config_dir", None)

    global docs_dir
    docs_dir = kwargs["docs_dir"]

    global logs_dir
    logs_dir = kwargs["logs_dir"]
    utils.ensure_dir(logs_dir)

    global _prefs_path
    _prefs_path = kwargs.get("prefs_path", None)

    global _source_dir
    _source_dir = kwargs["source_dir"]

    _setup_state_dir(kwargs["state_dir"])
    _setup_install_dir(kwargs["install_dir"])

    global log_path
    if "log_name" in kwargs:
        log_path = _create_log(kwargs["log_name"])

    if "git_user_name" in kwargs:
        global git_user_name
        git_user_name = kwargs["git_user_name"]

    if "git_email" in kwargs:
        global git_email
        git_email = kwargs["git_email"]


def get_source_dir():
    global _source_dir
    utils.ensure_dir(_source_dir)
    return _source_dir


def get_pref(name):
    defaults = {"PROFILE": "default"}

    prefs = _read_prefs()
    return prefs.get(name, defaults.get(name, None))


def set_pref(name, value):
    prefs = _read_prefs()
    prefs[name] = value
    _save_prefs(prefs)


def get_full_build():
    with open(os.path.join(config_dir, "config.json")) as f:
        config = json.load(f)

    return config["full_build"]


def load_packages():
    with open(os.path.join(config_dir, "packages.json")) as f:
        return json.load(f)


def load_prerequisites():
    with open(os.path.join(config_dir, "prerequisites.json")) as f:
        return json.load(f)


def load_checks():
    with open(os.path.join(config_dir, "dependencies.json")) as f:
        return filter(_filter_if, json.load(f))


def load_modules():
    with open(os.path.join(config_dir, "modules.json")) as f:
        return [Module(info) for info in filter(_filter_if, json.load(f))]


def _create_log(prefix):
    logfile_path = None
    number = 0

    while logfile_path is None:
        name = "%s-%d.log" % (prefix, number)
        path = os.path.join(logs_dir, name)

        if not os.path.exists(path):
            logfile_path = path

        number = number + 1

    link_path = os.path.join(logs_dir, "%s.log" % prefix)

    try:
        os.unlink(link_path)
    except OSError:
        pass

    os.symlink(logfile_path, link_path)

    return logfile_path


def _filter_if(item):
    if "if" not in item:
        return True

    distro_info = distro.get_distro_info()
    globals = {"gnome_version": distro_info.gnome_version,
               "distro": "%s-%s" % (distro_info.name, distro_info.version)}

    return eval(item["if"], globals)


def _setup_state_dir(state_dir):
    utils.ensure_dir(state_dir)

    global build_state_dir
    build_state_dir = os.path.join(state_dir, "build")
    utils.ensure_dir(build_state_dir)

    base_home_dir = os.path.join(state_dir, "home")
    utils.ensure_dir(base_home_dir)

    global home_dir
    home_dir = os.path.join(base_home_dir, get_pref("PROFILE"))
    utils.ensure_dir(home_dir)


def _setup_install_dir(dir, relocatable=False):
    global system_lib_dirs
    global install_dir
    global share_dir
    global bin_dir
    global etc_dir
    global lib_dir
    global libexec_dir

    install_dir = dir
    utils.ensure_dir(install_dir)

    share_dir = os.path.join(install_dir, "share")
    bin_dir = os.path.join(install_dir, "bin")
    etc_dir = os.path.join(install_dir, "etc")
    libexec_dir = os.path.join(install_dir, "libexec")

    distro_info = distro.get_distro_info()

    relative_lib_dir = distro_info.lib_dir
    if relative_lib_dir is None:
        relative_lib_dir = "lib"

    lib_dir = os.path.join(install_dir, relative_lib_dir)

    system_lib_dirs = ["/usr/lib"]
    if distro_info.lib_dir is not None:
        system_lib_dirs.append(os.path.join("/usr", distro_info.lib_dir))


def _read_prefs():
    global _prefs_path

    if _prefs_path is None or not os.path.exists(_prefs_path):
        return {}

    prefs = {}
    with open(_prefs_path) as f:
        for line in f.readlines():
            splitted = line.strip().split("=")
            if len(splitted) == 2:
                prefs[splitted[0]] = splitted[1]

    return prefs


def _save_prefs(prefs):
    global _prefs_path

    if _prefs_path is None:
        return

    with open(_prefs_path, "w") as f:
        for pref in prefs.items():
            f.write("%s\n" % "=".join(pref))
