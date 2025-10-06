#!/usr/bin/env python3
import subprocess
from datetime import date


def get_version_number() -> str:
    """
    Generate a version string according to CalVer's `YYYY.MM.DD` format (e.g. 1970.1.1). If multiple releases exist
    for today, append or increment a letter suffix.

    :returns: the next CalVer date string
    """
    today: date = date.today()
    today_formatted: str = f'{today.year}.{today.month}.{today.day}'

    latest_tag: str | None = get_latest_tag_for_today(today_formatted)

    if latest_tag is None:
        return today_formatted

    latest_suffix = latest_tag.lstrip('0123456789.')

    if not latest_suffix:
        return f'{today_formatted}a'

    incremented_suffix = get_increment_suffix(latest_suffix)

    return f'{today_formatted}{incremented_suffix}'


def get_latest_tag_for_today(pattern: str) -> str | None:
    """
    Get the latest git tag starting with the given pattern.

    :param pattern: Expected: today's date in YYYY.MM.DD format (e.g. 1970.1.1)

    :return: The most recent tag, or None if none exist.
    """
    try:
        ordered_output = subprocess.check_output(
            ['git', 'tag', '--list', f'{pattern}*', '--sort', 'version:refname'],
            text=True,
        )

        ordered_tags = ordered_output.splitlines()

        if not ordered_tags:
            return None

        return ordered_tags[-1]
    except subprocess.CalledProcessError:
        return None


def get_increment_suffix(suffix: str) -> str:
    """
    Get an incremented alpha suffix. ('a' -> 'b', 'z' -> 'aa', etc.)

    :param suffix: The current suffix.

    :return: The incremented suffix.
    """
    chars = list(suffix)
    index = len(chars) - 1

    while index >= 0:
        if chars[index] < 'z':
            chars[index] = chr(ord(chars[index]) + 1)
            return ''.join(chars)

        chars[index] = 'a'
        index -= 1

    return 'a' + ''.join(chars)


def main() -> None:
    version = get_version_number()

    print(version)


if __name__ == '__main__':
    main()
