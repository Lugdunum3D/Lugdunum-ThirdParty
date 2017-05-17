import argparse
import logging
import os
import sys
import yaml
import zipfile

sys.path.append(os.path.dirname(__file__))

import builders

builder_classes = {
    'fmt': builders.Fmt,
    'gltf2-loader': builders.Gltf2Loader,
    'googlemock': builders.GoogleMock,
    'shaderc': builders.Shaderc,
    'vulkan': builders.Vulkan,
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

    # For each builders in the config file, build
    for builder_name in config:
        if builder_name not in builder_classes:
            logger.error('Can\'t find builder for "%s"', builder_name)
            sys.exit(1)

        builder = builder_classes[builder_name](args, logger, config[builder_name])
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
