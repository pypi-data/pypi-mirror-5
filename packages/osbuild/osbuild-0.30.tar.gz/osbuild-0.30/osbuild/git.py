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

import os
import subprocess

from osbuild import command
from osbuild import config


def _chdir(func):
    def wrapped(*args, **kwargs):
        orig_cwd = os.getcwd()

        os.chdir(args[0].local)
        result = func(*args, **kwargs)
        os.chdir(orig_cwd)

        return result

    return wrapped


class Module:
    def __init__(self, path=None, name=None, remote=None,
                 branch="master", tag=None, retry=10):
        if path is None or name is None or remote is None:
            raise RuntimeError("path, name and remote are required")

        self.remote = remote
        self.local = os.path.join(path, name)
        self.tag = tag

        self._path = path
        self._name = name
        self._branch = branch
        self._retry = 10

    def _clone(self):
        os.chdir(self._path)

        command.run(["git", "clone", "--progress", self.remote, self._name],
                    retry=self._retry)

        os.chdir(self.local)

        if config.git_user_name:
            command.run(["git", "config", "user.name", config.git_user_name])

        if config.git_email:
            command.run(["git", "config", "user.email", config.git_email])

        if self.tag:
            command.run(["git", "checkout", self.tag])
        else:
            command.run(["git", "checkout", self._branch])

    def exists(self):
        return os.path.exists(os.path.join(self.local, ".git"))

    def update(self, revision=None):
        if not self.exists():
            self._clone()
            return

        orig_cwd = os.getcwd()
        os.chdir(self.local)

        if revision is None:
            if self.tag and self._head_has_tag(self.tag):
                os.chdir(orig_cwd)
                return

            revision = self.tag

        if revision == self._get_commit_id():
            os.chdir(orig_cwd)
            return

        command.run(["git", "remote", "set-url", "origin", self.remote])
        command.run(["git", "fetch"], retry=self._retry)

        if revision:
            command.run(["git", "checkout", revision])
        else:
            command.run(["git", "merge", "--ff-only",
                         "origin/%s" % self._branch])

        os.chdir(orig_cwd)

    @_chdir
    def checkout(self, revision=None):
        if revision is None:
            revision = self.tag
            if revision is None:
                revision = self._branch

        command.run(["git", "checkout", revision])

    @_chdir
    def describe(self):
        return subprocess.check_output(["git", "describe"]).strip()

    @_chdir
    def get_annotation(self, tag):
        # FIXME this is fragile, there must be a better way

        show = subprocess.check_output(["git", "show", tag])

        annotation = []
        for line in show.split("\n"):
            ignore = False
            for start in ["tag ", "Tagger: ", "Date: "]:
                if line.startswith(start):
                    ignore = True

            if line.startswith("commit "):
                break

            if not ignore:
                annotation.append(line)

        return "\n".join(annotation)

    def clean(self, new_files=False):
        try:
            os.chdir(self.local)
        except OSError:
            return False

        options = "-fd"
        if new_files:
            options = options + "x"
        else:
            options = options + "X"

        command.run(["git", "clean", options])

        return True

    def _get_commit_id(self):
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()

    def _head_has_tag(self, tag):
        tags = subprocess.check_output(["git", "tag", "--points-at", "HEAD"])
        return tag in tags.split("\n")


def get_module(module):
    return Module(path=config.get_source_dir(),
                  name=module.name,
                  remote=module.repo,
                  branch=module.branch,
                  tag=module.tag,
                  retry=10)
