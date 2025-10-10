#!/usr/bin/env python3
import os
import re
import subprocess
import sys


def main() -> None:
    verify_html_data_changes()
    verify_package_manifest_changes()

    print('All required file changes successfully detected by Git. Continuing.')
    sys.exit(0)


def verify_html_data_changes() -> None:
    file_path = get_env_variable_value('HTML_DATA_FILE_PATH')

    get_short_stat(file_path)


def verify_package_manifest_changes() -> None:
    file_path = get_env_variable_value('PACKAGE_MANIFEST_FILE_PATH')

    short_stat = get_short_stat(file_path)

    pattern = r'(\d+)\s+file[s]? changed(?:,\s+(\d+)\s+insertion[s]?\(\+\))?(?:,\s+(\d+)\s+deletion[s]?\(\-\))?'
    match = re.search(pattern, short_stat)

    if not match:
        print('Could not parse shortstat output')
        sys.exit(1)

    files_changed = int(match.group(1) if match.group(1) else 0)
    insertions = int(match.group(2) if match.group(2) else 0)
    deletions = int(match.group(3) if match.group(3) else 0)

    if files_changed != 1 or insertions != 2 or deletions != 2:
        print(f'Unexpected change count in {file_path}. Exiting.')
        print('Expected: 1 file changed, 2 insertions, 2 deletions.')
        print(f'Found: {files_changed} files changed, {insertions} insertions, {deletions} deletions.')
        sys.exit(1)


def get_env_variable_value(environment_variable: str) -> str:
    file_path = os.environ.get(environment_variable)

    if not file_path:
        print(f'Unable to access environment variable {environment_variable}. Exiting.')
        sys.exit(1)

    return file_path


def get_short_stat(file_path: str) -> str:
    try:
        file_stat = subprocess.check_output(['git', 'diff', '--shortstat', file_path], text=True)

        if not file_stat:
            print(f'No changes detected in {file_path}. Exiting.')
            sys.exit(1)

        return file_stat
    except subprocess.CalledProcessError as git_error:
        expected_error_code = 1

        if git_error.returncode == expected_error_code:
            return git_error.stdout.strip()
        else:
            print(f'Unexpected error verifying {file_path}')
            sys.exit(1)
    except Exception:
        print(f'Unexpected error verifying {file_path}')
        sys.exit(1)


if __name__ == '__main__':
    main()
