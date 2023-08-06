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


import os
import locale
import gettext

os.environ.setdefault("LANG", "en_GB.UTF-8")

lc, encoding = locale.getdefaultlocale()

mo_location = os.path.join(os.path.dirname(__file__), "i18n")
languages = [lc, ]

gettext.install(True, localedir=None, unicode=1)
gettext.find("Yaybu", mo_location)
gettext.textdomain("Yaybu")
gettext.bind_textdomain_codeset("Yaybu", "UTF-8")

language = gettext.translation(
    "Yaybu", mo_location, languages=languages, fallback=True)

_ = language.ugettext
