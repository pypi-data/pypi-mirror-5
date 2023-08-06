# Copyright 2011 Isotoma Limited
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

from yaybu.provisioner import provider
from yaybu import error
from yaybu.provisioner import resources
from yaybu.provisioner.changes import ShellCommand


def is_installed(context, resource):
    # work out if the package is already installed
    command = ["dpkg-query", "-W", "-f='${Status}'", resource.name.as_string()]

    try:
        rc, stdout, stderr = context.transport.execute(command)
    except error.SystemError as exc:
        if exc.returncode == 1:
            return False
        # if the return code is anything but zero or one, we have a problem
        raise error.DpkgError("%s search failed with return code %s" % (resource, exc.returncode))

    # if the return code is 0, dpkg is aware of the package
    if "install ok installed" in stdout:
        return True

    return False


class AptInstall(provider.Provider):

    policies = (resources.package.PackageInstallPolicy,)

    def apply(self, context, output):
        if is_installed(context, self.resource):
            return False

        env = {
            "DEBIAN_FRONTEND": "noninteractive",
            }

        # the search returned 1, package is not installed, continue and install it
        command = ["apt-get", "install", "-q", "-y", self.resource.name.as_string()]

        try:
            context.change(ShellCommand(command, env=env))
        except error.SystemError as exc:
            raise error.AptError("%s failed with return code %d" % (self.resource, exc.returncode))

        return True


class AptUninstall(provider.Provider):

    policies = (resources.package.PackageUninstallPolicy,)

    def apply(self, context, output):
        if not is_installed(context, self.resource):
            return False

        env = {
            "DEBIAN_FRONTEND": "noninteractive",
            }

        command = ["apt-get", "remove", "-q", "-y"]
        if self.resource.purge.as_bool():
            command.append("--purge")
        command.append(self.resource.name.as_string())

        try:
            context.change(ShellCommand(command, env=env))
        except error.SystemError as exc:
            raise error.AptError("%s failed to uninstall with return code %d" % (self.resource, exc.returncode))

        return True
