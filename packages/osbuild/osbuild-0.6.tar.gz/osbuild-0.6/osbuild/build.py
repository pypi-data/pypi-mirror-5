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

import fnmatch
import os
import multiprocessing
import shutil
import subprocess

from osbuild import command
from osbuild import config
from osbuild import state
from osbuild import utils
from osbuild import git

_builders = {}
_distributors = {}


def build_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _build_module(module)

    return False


def pull_one(module_name):
    for module in config.load_modules():
        if module.name == module_name:
            return _pull_module(module)

    return False


def pull(revisions={}, lazy=False):
    to_pull = []
    for module in config.load_modules():
        git_module = git.get_module(module)
        if not lazy or not os.path.exists(git_module.local):
            to_pull.append(module)

    if to_pull:
        print("\n= Pulling =\n")

    for module in to_pull:
        revision = revisions.get(module.name, None)
        if not _pull_module(module, revision):
            return False

    return True


def build(full=False):
    to_build = []
    for module in config.load_modules():
        if not state.built_module_is_unchanged(module):
            to_build.append(module)

    if not to_build:
        return True

    print("\n= Building =\n")

    _ccache_reset()

    for module in to_build:
        if not _build_module(module):
            return False

    _ccache_print_stats()

    return True


def clean():
    print("* Emptying install directory")
    _empty_dir(config.install_dir)

    for module in config.load_modules():
        print("* Cleaning %s" % module.name)

        git_module = git.get_module(module)

        if git_module.exists():
            git_module.stash()

        git_module.clean()


def _ccache_reset():
    subprocess.check_call(["ccache", "-z"], stdout=utils.devnull)


def _ccache_print_stats():
    print("\n= ccache statistics =\n")
    subprocess.check_call(["ccache", "-s"])


def _unlink_libtool_files():
    def func(arg, dirname, fnames):
        for fname in fnmatch.filter(fnames, "*.la"):
            os.unlink(os.path.join(dirname, fname))

    os.path.walk(config.lib_dir, func, None)


def _pull_module(module, revision=None):
    print("* Pulling %s" % module.name)

    git_module = git.get_module(module)

    if git_module.exists():
        git_module.stash()

    try:
        git_module.update(revision)
    except subprocess.CalledProcessError:
        return False

    return True


def _eval_option(option):
    return eval(option, {"prefix": config.install_dir})


def _build_autotools(module, log):
    # Workaround for aclocal 1.11 (fixed in 1.12)
    aclocal_path = os.path.join(config.share_dir, "aclocal")
    utils.ensure_dir(aclocal_path)

    makefile_path = os.path.join(module.get_source_dir(), module.makefile_name)

    if not os.path.exists(makefile_path):
        configure = os.path.join(module.get_source_dir(), "autogen.sh")
        if not os.path.exists(configure):
            configure = os.path.join(module.get_source_dir(), "configure")

        args = [configure, "--prefix", config.install_dir]

        if not module.no_libdir:
            args.extend(["--libdir", config.lib_dir])

        args.extend(module.options)

        for option in module.options_evaluated:
            args.append(_eval_option(option))

        command.run(args, log)

    jobs = multiprocessing.cpu_count() * 2

    command.run(["make", "-j", "%d" % jobs], log)
    command.run(["make", "install"], log)

    _unlink_libtool_files()

_builders["autotools"] = _build_autotools


def _build_distutils(module, log):
    setup = os.path.join(module.get_source_dir(), "setup.py")
    command.run(["python", setup, "install", "--prefix",
                 config.install_dir], log)

_builders["distutils"] = _build_distutils


def _build_volo(module, log):
    pass

_builders["volo"] = _build_volo


def _build_npm(module, log):
    command.run(["npm", "install", "-g", "--prefix", config.install_dir], log)

_builders["npm"] = _build_npm


def _build_module(module, log=None):
    print("* Building %s" % module.name)

    source_dir = module.get_source_dir()

    if not os.path.exists(source_dir):
        print("Source directory does not exist. Please pull the sources "
              "before building.")
        return False

    os.chdir(source_dir)

    try:
        build_system = module.get_build_system()
        if build_system:
            _builders[build_system](module, log)
    except subprocess.CalledProcessError:
        return False

    state.built_module_touch(module)

    return True


def _empty_dir(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)
    os.mkdir(dir_path)
