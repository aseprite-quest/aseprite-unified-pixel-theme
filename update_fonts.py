import json
import logging
import os
import shutil
import zipfile

import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('update-fonts')

project_root_dir = os.path.dirname(__file__)
fonts_dir = os.path.join(project_root_dir, 'data', 'fonts')
version_file_path = os.path.join(fonts_dir, 'version.json')
cache_dir = os.path.join(project_root_dir, 'cache')


def _get_github_releases_latest_tag_name(repository_name: str) -> str:
    url = f'https://api.github.com/repos/{repository_name}/releases/latest'
    response = requests.get(url)
    assert response.ok, url
    return response.json()['tag_name']


def _download_file(url: str, file_path: str):
    response = requests.get(url, stream=True)
    assert response.ok, url
    tmp_file_path = f'{file_path}.download'
    with open(tmp_file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=512):
            if chunk is not None:
                file.write(chunk)
    os.rename(tmp_file_path, file_path)


def main():
    repository_name = 'TakWolf/fusion-pixel-font'
    repository_url = f'https://github.com/{repository_name}'

    if os.path.exists(version_file_path):
        with open(version_file_path, 'r', encoding='utf-8') as file:
            current_version = json.loads(file.read())['version']
    else:
        current_version = None

    latest_version = _get_github_releases_latest_tag_name(repository_name)
    if current_version == latest_version:
        return
    logger.info("Need update fonts: '%s'", latest_version)

    download_dir = os.path.join(cache_dir, repository_name, latest_version)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    if os.path.exists(fonts_dir):
        shutil.rmtree(fonts_dir)
        os.makedirs(fonts_dir)

    for font_size in [10]:
        asset_file_name = f'fusion-pixel-font-{font_size}px-proportional-ttf-v{latest_version}.zip'
        asset_file_path = os.path.join(download_dir, asset_file_name)
        if not os.path.exists(asset_file_path):
            asset_url = f'{repository_url}/releases/download/{latest_version}/{asset_file_name}'
            logger.info("Start download: '%s'", asset_url)
            _download_file(asset_url, asset_file_path)
        else:
            logger.info("Already downloaded: '%s'", asset_file_path)

        asset_unzip_dir = os.path.join(fonts_dir, str(font_size))
        if os.path.exists(asset_unzip_dir):
            shutil.rmtree(asset_unzip_dir)
        with zipfile.ZipFile(asset_file_path) as file:
            file.extractall(asset_unzip_dir)
        logger.info("Unzip: '%s'", asset_unzip_dir)

    version_info = {
        'repository_url': repository_url,
        'version': latest_version,
        'version_url': f'{repository_url}/releases/tag/{latest_version}',
    }
    with open(version_file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(version_info, indent=2, ensure_ascii=False))
        file.write('\n')
    logger.info("Update version file: '%s'", version_file_path)


if __name__ == '__main__':
    main()
