""" Hacky web scraper for the atlassian marketplace
"""

import requests
from bs4 import BeautifulSoup
from furl import furl

VERSION_HISTORY_URL = "https://marketplace.atlassian.com/apps/{}/WILDCARD/version-history"


class MpacAppNotFoundError(ValueError):
    pass


class MpacAppVersionNotFoundError(ValueError):
    pass


def download_link_by_marketplace_id(marketplace_id: int, version: str = "latest") -> furl:
    response = requests.get(VERSION_HISTORY_URL.format(marketplace_id))
    soup = BeautifulSoup(response.content, "html5lib")

    body_dom = soup.select_one("body")
    if "error-page" in body_dom.get("class"):
        raise MpacAppNotFoundError("Can't find any app with this app marketplace id")

    plugin_versions_dom = soup.select_one(".plugin-versions")
    plugins_dom = plugin_versions_dom.select(".version-row")
    selected_row = None
    if version == "latest" and len(plugins_dom) > 0:
        selected_row = plugins_dom[0]
    else:
        filtered = list(filter(lambda x: x.select_one("span.version").text == version, plugins_dom))
        if len(filtered) > 0:
            selected_row = filtered[0]
    if selected_row is None:
        raise MpacAppVersionNotFoundError("Can't find version")

    return furl(selected_row.select_one(".download-link")["href"])
