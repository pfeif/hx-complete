import json
import os
import xml.etree.ElementTree
import zipfile
from io import BytesIO
from typing import NamedTuple

import requests


def main():
    # TODO: Use dataclasses next time.

    release_version = get_release_version()
    release_archive = download_release(release_version)
    attribute_names = get_attribute_names(release_archive)
    attributes_with_descriptions = get_descriptions(attribute_names, release_archive)
    global_attributes = get_global_attributes(attributes_with_descriptions)
    value_sets = get_value_sets()
    write_output(global_attributes, value_sets)


def get_release_version() -> str:
    """
    Retrieve the latest htmx release identifier from the project's GitHub releases Atom feed.

    :returns: a version string in the format 'vX.X.X'
    :rtype: str
    """
    try:
        response = requests.get('https://github.com/bigskysoftware/htmx/releases.atom', timeout=10)
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


def download_release(version: str) -> bytes:
    """
    Download an htmx release's ZIP archive.

    :param str version: the version identifier for the htmx release

    :returns: a binary release ZIP file
    :rtype: bytes
    """
    try:
        response = requests.get(f'https://github.com/bigskysoftware/htmx/archive/refs/tags/{version}.zip', timeout=10)
        response.raise_for_status()

        return response.content
    except requests.RequestException as error:
        raise SystemExit(error) from error


def get_attribute_names(archive: bytes) -> list[str]:
    """
    Extract the htmx attribute names from the release's web docs.

    :param bytes archive: a binary release ZIP file

    :returns: a list of htmx attributes
    :rtype: list[str]
    """
    attributes: list[str] = []

    with zipfile.ZipFile(BytesIO(archive)) as source_code:
        for zip_info in source_code.filelist:
            if (
                'attributes' in zip_info.filename
                and zip_info.filename.endswith('.md')
                and '_index' not in zip_info.filename
            ):
                attribute = zipfile.Path(source_code, zip_info.filename).name.removesuffix('.md')
                attributes.append(attribute)

    if not attributes:
        raise SystemExit

    return attributes


def get_descriptions(attributes: list[str], archive: bytes) -> dict[str, str]:
    """
    Extract descriptions for htmx attributes from the reference section of the release's web docs,
    and pair them with their attributes.

    :param list[str] attributes: a list of htmx attributes
    :param bytes archive: a binary release ZIP file

    :returns: a dictionary where the keys are attributes and the values are attribute descriptions
    :rtype: dict[str, str]
    """
    lines: list[str] = []

    with zipfile.ZipFile(BytesIO(archive)) as source_code:
        for zip_info in source_code.filelist:
            if zip_info.filename.endswith('www/content/reference.md'):
                path = zipfile.Path(source_code, zip_info.filename)
                with path.open(encoding='utf-8') as file:
                    lines = file.readlines()
                break

    remaining_attributes = attributes.copy()
    descriptions: dict[str, str] = {}

    for line in lines:
        if not line.strip().startswith('| ['):
            continue

        for attribute in remaining_attributes:
            if line.strip().startswith(f'| [`{attribute}'):
                descriptions[attribute] = line.split('|')[2].strip()
                remaining_attributes.remove(attribute)
                break

        if not remaining_attributes:
            break

    if not descriptions:
        raise SystemExit

    return descriptions


def get_global_attributes(attributes: dict[str, str]) -> list[dict[str, str | list[dict[str, str]]]]:
    """
    Create the global attributes for the extension's `html-data.json` file.

    :param dict[str, str] attributes: an htmx attribute/description dictionary

    :returns: a list of global attributes
    :rtype: list[dict[str, str | list[dict[str, str]]]]
    """
    global_attributes: list[dict[str, str | list[dict[str, str]]]] = []

    for attribute, description in attributes.items():
        if '@/' in description:
            description = description.replace('@/', 'https://htmx.org/')

        if '.md' in description:
            description = description.replace('.md', '/')

        for prefix in ['', 'data-']:
            global_attribute: dict[str, str | list[dict[str, str]]] = {
                'name': f'{prefix}{attribute}',
                'description': description,
                'valueSet': attribute if attribute in ['hx-swap', 'hx-swap-oob', 'hx-target'] else '',
                'references': [
                    {
                        'name': f'`{attribute}` documentation on htmx.org',
                        'url': f'https://htmx.org/attributes/{attribute}/',
                    },
                ],
            }

            if global_attribute['valueSet'] == '':
                del global_attribute['valueSet']

            global_attributes.append(global_attribute)

    return global_attributes


def get_value_sets() -> list[dict[str, str | list[dict[str, str]]]]:
    """
    Get the value sets for the `html-data.json` file.

    :returns: a list of value sets
    :rtype: list[dict[str, str | list[dict[str, str]]]]
    """
    # TODO: Think about ways to automate this.

    value = NamedTuple('value', [('name', str), ('description', str)])

    hx_swap: dict[str, str | list[dict[str, str]]] = {'name': 'hx-swap', 'values': []}
    hx_swap_oob: dict[str, str | list[dict[str, str]]] = {'name': 'hx-swap-oob', 'values': [{'name': 'true'}]}
    hx_target: dict[str, str | list[dict[str, str]]] = {'name': 'hx-target', 'values': []}

    swap_values = [
        value('innerHTML', 'Replace the inner html of the target element'),
        value('outerHTML', 'Replace the entire target element with the response'),
        value('textContext', 'Replace the text content of the target element, without parsing the response as HTML'),
        value('beforebegin', 'Insert the response before the target element'),
        value('afterbegin', 'Insert the response before the first child of the target element'),
        value('beforeend', 'Insert the response after the last child of the target element'),
        value('afterend', 'Insert the response after the target element'),
        value('delete', 'Deletes the target element regardless of the response'),
        value('none', 'Does not append content from response (out of band items will still be processed).'),
    ]

    target_values = [
        value(
            '<CSS query selector>',
            'A CSS query selector of the element to target.',
        ),
        value(
            'this',
            '`this` which indicates that the element that the `hx-target` attribute is on is the target.',
        ),
        value(
            'closest <CSS selector>',
            '`closest <CSS selector>` which will find the [closest](https://developer.mozilla.org/docs/Web/API/Element/closest) ancestor element or itself, that matches the given CSS selector (e.g. `closest tr` will target the closest table row to the element).',
        ),
        value(
            'find <CSS selector>',
            '`find <CSS selector>` which will find the first child descendant element that matches the given CSS selector.',
        ),
        value(
            'next',
            '`next` which resolves to [element.nextElementSibling](https://developer.mozilla.org/docs/Web/API/Element/nextElementSibling)',
        ),
        value(
            'next <CSS selector>',
            '`next <CSS selector>` which will scan the DOM forward for the first element that matches the given CSS selector. (e.g. `next .error` will target the closest following sibling element with `error` class)',
        ),
        value(
            'previous',
            '`previous` which resolves to [element.previousElementSibling](https://developer.mozilla.org/docs/Web/API/Element/previousElementSibling)',
        ),
        value(
            'previous <CSS selector>',
            '`previous <CSS selector>` which will scan the DOM backwards for the first element that matches the given CSS selector. (e.g `previous .error` will target the closest previous sibling with `error` class)',
        ),
    ]

    for swap_value in swap_values:
        hx_swap['values'].append(swap_value._asdict())  # type: ignore
        hx_swap_oob['values'].append(swap_value._asdict())  # type: ignore
        if swap_value.name != 'none':
            hx_swap_oob['values'].append(value(f'{swap_value.name}:<CSS selector>', swap_value.description)._asdict())  # type: ignore

    for target_value in target_values:
        hx_target['values'].append(target_value._asdict())  # type: ignore

    return [hx_swap, hx_swap_oob, hx_target]


def write_output(
    global_attributes: list[dict[str, str | list[dict[str, str]]]],
    value_sets: list[dict[str, str | list[dict[str, str]]]],
) -> None:
    """
    Create or replace the extension's `htmx2.html-data.json` file.

    :param list[dict[str, str | list[dict[str, str]]]] global_attributes: a JSON-like `globalAttributes` object
    :param list[dict[str, str | list[dict[str, str]]]] value_sets: a JSON-like valueSets object
    """
    html_data: dict[str, float | list[None] | list[dict[str, str | list[dict[str, str]]]]] = {
        'version': 1.1,
        'tags': [],
        'globalAttributes': global_attributes,
        'valueSets': value_sets,
    }

    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(os.path.join(script_directory, '..', 'data', 'htmx2.html-data.json'))

    with open(output_path, 'w') as output_file:
        output_file.writelines(json.dumps(html_data, indent=4))


if __name__ == '__main__':
    main()
