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

from libcloud.dns.types import RecordType

from yaybu import error
from yaybu.tests.base import TestCase
from yaybu.tests.mocks.libcloud_dns import MockDNSDriver, MockDNSDriverArgless
from yaybu.tests.mocks.libcloud_compute import MockNodeDriver


class TestZone(TestCase):

    def setUp(self):
        MockDNSDriver.install(self)
        self.driver = MockDNSDriver("", "")

    def test_validate_driver_id(self):
        self.assertRaises(error.ValueError, self.up, """
            new Zone as myzone:
                    driver:
                        id: DUMMYY
                        api_key: dummykey
                        secret: dummysecret
                    domain: example.com
                    records: []
            """)

    def test_empty_records_list(self):
        self.assertEqual(len(self.driver.list_zones()), 0)
        self.up("""
            new Zone as myzone:
                    driver:
                        id: DUMMY
                        api_key: dummykey
                        secret: dummysecret
                    domain: example.com
                    records: []
            """)
        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 1)
        # FIXME: Investigate rstrip...
        self.assertEqual(zones[0].domain.rstrip("."), "example.com")
        self.assertEqual(zones[0].list_records(), [])

    def test_add_records(self):
        self.assertEqual(len(self.driver.list_zones()), 0)
        self.up("""
            new Zone as myzone:
                    driver:
                        id: DUMMY
                        api_key: dummykey
                        secret: dummysecret
                    domain: example.com
                    records:
                      - name: www
                        data: 127.0.0.1
            """)
        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 1)

        records = zones[0].list_records()
        self.assertEqual(len(records), 1)

        self.assertEqual(records[0].name, "www")
        self.assertEqual(records[0].type, RecordType.A)
        self.assertEqual(records[0].data, "127.0.0.1")

    def test_cleans_up_existing_zone_not_shared(self):
        z = self.driver.create_zone("example.com.", "master", 0)
        z.create_record("www", type=RecordType.A, data='127.0.0.1')

        self.up("""
            new Zone as myzone:
                    driver:
                        id: DUMMY
                        api_key: dummykey
                        secret: dummysecret
                    domain: example.com
                    records: []
                    shared: 0
            """)

        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 1)
        self.assertEqual(zones[0].list_records(), [])

    def test_cleans_up_existing_zone_shared(self):
        z = self.driver.create_zone("example.com.", "master", 0)
        z.create_record("www", type=RecordType.A, data='127.0.0.1')

        self.assertRaises(error.NothingChanged, self.up, """
            new Zone as myzone:
                    driver:
                        id: DUMMY
                        api_key: dummykey
                        secret: dummysecret
                    domain: example.com
                    records: []
            """)

        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 1)
        self.assertEqual(len(zones[0].list_records()), 1)


class TestZoneWithCompute(TestCase):

    def setUp(self):
        MockDNSDriver.install(self)
        MockNodeDriver.install(self)
        self.driver = MockDNSDriver("", "")

    def test_dns_consumes_data_from_compute(self):
        self.up("""
            new Compute as mycompute:
                name: hello
                driver:
                    id: DUMMY
                    api_key: dummy
                    secret: dummy
                image: 1
                size: 2

            new Zone as myzone:
                    driver:
                        id: DUMMY
                        api_key: dummykey
                        secret: dummysecret
                    domain: example.com
                    records:
                      - name: www
                        data: {{ mycompute.public_ip }}
            """)

        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 1)

        records = zones[0].list_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].name, "www")
        self.assertEqual(records[0].data, "127.0.0.1")


class TestZoneArglessDriver(TestCase):

    def setUp(self):
        MockDNSDriverArgless.install(self)
        self.driver = MockDNSDriverArgless()

    def test_empty_records_list(self):
        self.assertEqual(len(self.driver.list_zones()), 0)
        self.up("""
            new Zone as myzone:
                    driver: DUMMY
                    domain: example.com
                    records: []
            """)
        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 1)
        # FIXME: Investigate rstrip...
        self.assertEqual(zones[0].domain.rstrip("."), "example.com")
        self.assertEqual(zones[0].list_records(), [])
