# Vyper ASPM
#
# Copyright (C) 2026 Pedro
#
# This file is part of Vyper ASPM.
#
# Vyper ASPM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Vyper ASPM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Vyper ASPM. If not, see <https://www.gnu.org/licenses/>.

import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = (
    "http://127.0.0.1:8080/"
    "JSON/spider/action/scan/"
)

params = {
    "url": "https://public-firing-range.appspot.com/",
    "apikey": os.getenv("ZAP_API_KEY")
}

response = requests.get(
    url,
    params=params,
    proxies={
        "http": None,
        "https": None
    }
)

print(response.status_code)
print(response.text)