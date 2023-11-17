import json
import logging
import os
import shutil
import zipfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('build')

project_root_dir = os.path.dirname(__file__)
data_dir = os.path.join(project_root_dir, 'data')
releases_dir = os.path.join(project_root_dir, 'build', 'releases')


def main():
    if os.path.exists(releases_dir):
        shutil.rmtree(releases_dir)
    os.makedirs(releases_dir)

    package_json_file_path = os.path.join(data_dir, 'package.json')
    with open(package_json_file_path, 'r', encoding='utf-8') as file:
        package_info: dict = json.loads(file.read())

    package_name: str = package_info['name']
    package_version: str = package_info['version']
    extension_file_path = os.path.join(releases_dir, f'{package_name}-v{package_version}.aseprite-extension')
    with zipfile.ZipFile(extension_file_path, 'w') as file:
        for file_dir, _, file_names in os.walk(data_dir):
            for file_name in file_names:
                if file_name.startswith('.'):
                    continue
                file_path = os.path.join(file_dir, file_name)
                arc_path = file_path.removeprefix(f'{data_dir}/')
                file.write(file_path, arc_path)
                logger.info("Pack file: '%s'", arc_path)


if __name__ == '__main__':
    main()
