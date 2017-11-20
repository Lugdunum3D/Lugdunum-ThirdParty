import argparse
import logging
import os
import sys
import yaml
import zipfile
import shutil
import glob

sys.path.append(os.path.dirname(__file__))

import builders

builder_classes = {
    'fmt': builders.Fmt,
    'gltf2-loader': builders.Gltf2Loader,
    'googlemock': builders.GoogleMock,
    'shaderc': builders.Shaderc,
    'vulkan': builders.Vulkan,
    'imgui': builders.Imgui,
    'json': builders.Json,
    'curl': builders.Curl,
    'restclient': builders.Restclient,
    'freetype': builders.Freetype,
    'imgui_club': builders.Imgui_club,
    'lugdunum': builders.Lugdunum
}

def main():
    # Parse argument
    parser = argparse.ArgumentParser()

    parser.add_argument('--path', '-p', help='Specify the destination directory',
                        dest='path', default='thirdparty')
    parser.add_argument('-v', '--verbose', help='Enables verbose output; '
                        'repeat up to three time for more verbose output',
                        action='count', default=0)
    parser.add_argument('--build-types', help='Specify the build types that you want',
                        dest='build_types', nargs='+', type=str, choices=['Debug', 'Release'], default=['Debug', 'Release'])
    parser.add_argument('--zip-file', '-z', help='Specify the zip file, if not specified will not generate a zip',
                        dest='zip_file')
    parser.add_argument('config_file', help='Specify the configuration file to use',
                        type=str)
    parser.add_argument('--android', help='Compiling for Android', dest='android', default=False, action='store_true')

    args = parser.parse_args()
    args.path = os.path.abspath(args.path)

    # Define the logger
    logger = logging.getLogger()

    # Define the handle of the logger
    formatter = logging.Formatter('[%(levelname)8s] %(message)s')
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    # Define the level of verbosity of the logger
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, args.verbose)]

    logger.setLevel(level=level)

    # Build directory zip
    if not os.path.isdir(args.path):
        os.makedirs(args.path)

    # Load the configuration file
    config = None
    with open(args.config_file) as file:
        config = yaml.load(file)

    android_config = dict()
    android_config['enabled'] = args.android
    if args.android:
        # Find SDK
        if not os.environ.get('ANDROID_SDK_ROOT'):
            logger.error('Can\'t find ANDROID_SDK_ROOT environment variable')
            sys.exit(1)
        else:
            android_config['sdk_root'] = os.environ.get('ANDROID_SDK_ROOT')

        if not os.path.isdir(android_config['sdk_root']):
            logger.error('CMake NDK not found: `' + android_config['sdk_root'] + '`')
            sys.exit(1)

        # Find NDK
        if os.environ.get('ANDROID_NDK_ROOT'):
            android_config['ndk_root'] = os.environ.get('ANDROID_NDK_ROOT')
        else:
            android_config['ndk_root'] = android_config['sdk_root'] + '/ndk-bundle'

        if not os.path.isdir(android_config['ndk_root']):
            logger.error('CMake NDK not found: `' + android_config['ndk_root'] + '`')

        # Find CMake and toolchain
        android_config['cmake_executable'] = shutil.which('cmake', path=':'.join(
            # Sort in case we have multiple versions (invert order to pick the latest)
            sorted(glob.glob(os.environ.get('ANDROID_SDK_ROOT') + '/cmake/*/bin/'), reverse=True)
        ))
        android_config['cmake_toolchain'] = android_config['ndk_root'] + '/build/cmake/android.toolchain.cmake'

        if not android_config['cmake_executable']:
            logger.error('CMake path not found in `' + os.environ.get('ANDROID_SDK_ROOT') + '/cmake`')
            sys.exit(1)
        logger.info('CMake path found: `' + android_config['cmake_executable'] + '`')

        if not os.path.isfile(android_config['cmake_toolchain']):
            logger.error('CMake toolchain not found: `' + android_config['cmake_toolchain'] + '`')
            sys.exit(1)
        logger.info('CMake toolchain found: `' + android_config['cmake_toolchain'] + '`')

    # For each builders in the config file, build
    for builder_name in config:
        if builder_name not in builder_classes:
            logger.error('Can\'t find builder for "%s"', builder_name)
            sys.exit(1)

        builder = builder_classes[builder_name](args, logger, config[builder_name], android_config)
        if not builder.build():
            logger.error('Failed to build for builder "%s"', builder_name)
            sys.exit(1)

    # Generate zip
    if args.zip_file:
        logger.info('Generating the zip file "%s"', args.zip_file)

        zipf = zipfile.ZipFile(args.zip_file, 'w', zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(args.path):
            for file in files:
                filepath = os.path.abspath(os.path.join(root, file))
                zipf.write(filepath, os.path.relpath(filepath, args.path))

        zipf.close()

if __name__ == '__main__':
    main()
