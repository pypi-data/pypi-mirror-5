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

from osbuild import distro
from osbuild.plugins import interfaces
from osbuild.plugins import debian

distro.register_package_manager("ubuntu", debian.PackageManager)


class DistroInfo(interfaces.DistroInfo):
    _OS_RELEASE_PATH = "/etc/os-release"

    def __init__(self):
        arch = self._get_architecture()

        self.name = "ubuntu"
        self.version = "unknown"
        self.gnome_version = "3.4"
        self.valid = True
        self.supported = (arch in ["i386", "i686", "x86_64"])
        self.lib_dir = None

        if arch in ["i386", "i686"]:
            self.lib_dir = "lib/i386-linux-gnu"
        elif arch == "x86_64":
            self.lib_dir = "lib/x86_64-linux-gnu"

        os_info = {}

        try:
            release = open(self._OS_RELEASE_PATH).read().strip()
            for line in release.split("\n"):
                split = line.strip().split("=")
                os_info[split[0]] = split[1].replace("\"", "")
        except IOError:
            release = None
            self.valid = False

        if os_info.get("ID", None) != "ubuntu":
            self.valid = False

        self.version = os_info.get("VERSION_ID", None)

        if self.version == "13.04":
            self.gnome_version = "3.6"
        elif self.version == "13.10":
            self.gnome_version = "3.6"
        else:
            self.supported = False

    def _get_architecture(self):
        return subprocess.check_output(["uname", "-i"]).strip()

distro.register_distro_info(DistroInfo)
