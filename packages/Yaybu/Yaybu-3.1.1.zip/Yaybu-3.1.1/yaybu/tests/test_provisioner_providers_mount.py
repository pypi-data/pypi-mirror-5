# Copyright 2013 Isotoma Limited
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


from yaybu.tests.provisioner_fixture import TestCase, ChangeStillOutstanding


class TestMount(TestCase):

    def test_mount_bind(self):
        self.transport.put("/bin/mount", "#! /usr/bin/env python")
        self.transport.execute(["chmod", "755", "/bin/mount"])

        self.assertRaises(ChangeStillOutstanding, self.check_apply, """
            resources:
              - Mount:
                  name: /mnt
                  fs_type: bind
                  device: /bin
                  options: hello
            """)
