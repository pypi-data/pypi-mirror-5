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
        self._test = test
        self._interactive = interactive

    def install_packages(self, packages):
        args = ["yum"]

        if not self._interactive:
            args.append("-y")

        args.append("install")
        args.extend(packages)

        command.run_with_sudo(args, test=self._test,
                              interactive=self._interactive)

    def remove_packages(self, packages):
        args = ["rpm", "-e"]
        args.extend(packages)

        command.run_with_sudo(args, test=self._test)

    def update(self):
        args = ["yum"]

        if not self._interactive:
            args.append("-y")

        args.append("update")

        command.run_with_sudo(args, test=self._test,
                              interactive=self._interactive)

    def find_all(self):
        query_format = "--queryformat=[%{NAME} ]"
        all = subprocess.check_output(["rpm", "-qa", query_format]).strip()
        return all.split(" ")

    def find_with_deps(self, packages):
        result = []

        for package in packages:
            if package not in result:
                result.append(package)

            self._find_deps(package, result)

        return result

    def _find_deps(self, package, result):
        query_format = "--queryformat=[%{REQUIRENAME} ]"

        try:
            capabilities = subprocess.check_output(["rpm", "-q",
                                                    query_format,
                                                    package]).strip()
        except subprocess.CalledProcessError:
            print("Package %s not installed" % package)
            return

        filtered = [cap for cap in capabilities.split(" ")
                    if not cap.startswith("rpmlib")]

        if capabilities and filtered:
            args = ["rpm", "-q",
                    "--queryformat=[%{NAME} ]",
                    "--whatprovides"]
            args.extend(filtered)

            deps_packages = subprocess.check_output(args).strip()
            for dep_package in deps_packages.split(" "):
                if dep_package not in result:
                    result.append(dep_package)
                    self._find_deps(dep_package, result)

distro.register_package_manager("fedora", PackageManager)


class DistroInfo(interfaces.DistroInfo):
    _FEDORA_RELEASE_PATH = "/etc/fedora-release"

    def __init__(self):
        arch = self._get_architecture()

        self.name = "fedora"
        self.version = "unknown"
        self.valid = True
        self.supported = (arch in ["i386", "i686", "x86_64"])
        self.lib_dir = None

        if arch == "x86_64":
            self.lib_dir = "lib64"

        try:
            release = open(self._FEDORA_RELEASE_PATH).read().strip()
        except IOError:
            release = None
            self.valid = False

        if release == "Fedora release 18 (Spherical Cow)":
            self.version = "18"
            self.gnome_version = "3.6"
        elif release == "Fedora release 19 (Schrödinger’s Cat)":
            self.version = "19"
            self.gnome_version = "3.8"
        else:
            self.supported = False

    def _get_architecture(self):
        return subprocess.check_output(["uname", "-i"]).strip()

distro.register_distro_info(DistroInfo)
