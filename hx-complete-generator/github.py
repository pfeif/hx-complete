import xml.etree.ElementTree

import requests


def get_latest_release_version(atom_feed_url: str) -> str:
    """
    Retrieve the latest release identifier from a project's GitHub releases Atom feed.

    :returns: the identifier string
    """
    try:
        response = requests.get(atom_feed_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        raise SystemExit(error) from error

    feed_root = xml.etree.ElementTree.fromstring(response.text)
    latest_entry = feed_root.find('{http://www.w3.org/2005/Atom}entry')
    release_version = latest_entry.find('{http://www.w3.org/2005/Atom}title')  # type: ignore

    version = release_version.text  # type: ignore

    if not version:
        raise SystemExit

    return version


def download_release_archive(archive_url: str) -> bytes:
    """
    Download an GitHub release archive.

    :param str version: the version identifier for the htmx release

    :returns: a binary release file
    """
    try:
        response = requests.get(archive_url, timeout=10)
        response.raise_for_status()

        return response.content
    except requests.RequestException as error:
        raise SystemExit(error) from error
