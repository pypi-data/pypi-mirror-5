# coding=utf-8

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

import subprocess

from osbuild import command
from osbuild import distro
from osbuild.plugins import interfaces


class PackageManager(interfaces.PackageManager):
    def __init__(self, test=False, interactive=True):
        import apt

        self._test = test
        self._interactive = interactive

        self._cache = apt.cache.Cache()

    def install_packages(self, packages):
        args = ["apt-get", "--no-install-recommends"]

        if not self._interactive:
            args.append("-y")

        args.append("install")
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def remove_packages(self, packages):
        args = ["dpkg", "-P"]
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def update(self):
        command.run_with_sudo(["apt-get", "dist-upgrade"], test=self._test)

        args = ["apt-get"]

        if not self._interactive:
            args.append("-y")

        args.append("upgrade")

        command.run_with_sudo(args, test=self._test)

    def find_all(self):
        return [package.name for package in self._cache
                if package.installed is not None]

    def _find_deps(self, package, result):
        if self._cache.is_virtual_package(package):
            for providing in self._cache.get_providing_packages(package):
                self._find_deps(providing.name, result)
            return

        if package not in self._cache:
            print("Package %s not in cache" % package)
            return

        installed = self._cache[package].installed
        if installed is None:
            print("Package %s not installed" % package)
            return

        for dependency in installed.dependencies:
            for base_dependency in dependency.or_dependencies:
                dependency_name = base_dependency.name
                if dependency_name not in result:
                    result.append(dependency_name)
                    self._find_deps(dependency_name, result)

    def find_with_deps(self, package_names):
        result = []

        for package in package_names:
            if package is not None:
                self._find_deps(package, result)
                if package not in result:
                    result.append(package)

        return result


distro.register_package_manager("debian", PackageManager)


class DistroInfo(interfaces.DistroInfo):
    _DEBIAN_VERSION_PATH = "/etc/debian_version"

    def __init__(self):
        arch = self._get_architecture()

        self.name = "debian"
        self.version = "unknown"
        self.gnome_version = "3.4"
        self.valid = True
        self.supported = (arch in ["i686", "x86_64"])
        self.lib_dir = None

        if arch == "i686":
            self.lib_dir = "lib/i386-linux-gnu"
        elif arch == "x86_64":
            self.lib_dir = "lib/x86_64-linux-gnu"

        try:
            with open(self._DEBIAN_VERSION_PATH) as f:
                debian_version = f.read().strip()
        except IOError:
            debian_version = None

        if debian_version is None:
            self.valid = False

        if debian_version and debian_version == "jessie/sid":
            self.version = "jessie"
        else:
            self.supported = False

    def _get_architecture(self):
        return subprocess.check_output(["arch"]).strip()

distro.register_distro_info(DistroInfo)
