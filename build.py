import argparse
import builders
import logging
import os
import sys

def main():
    # Parse argument
    parser = argparse.ArgumentParser()

    parser.add_argument("--build-type", help='Specify the build type',
                        dest='build_type', choices=["Release", "Debug"], default="Release")
    parser.add_argument("--path", "-p", help='Specify the destination directory',
                        dest='path', default="thirdparty")
    parser.add_argument('-v', '--verbose', help='Enables verbose output; '
                        'repeat up to three time for more verbose output',
                        action='count', default=0)

    args = parser.parse_args()

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
        os.mkdir(args.path)

    # Build shaderc
    logger.info("Build Shaderc")

    shaderc_builder = builders.Shaderc(args, logger)
    if not shaderc_builder.build():
        logger.error("Failed to build Shaderc")
        sys.exit(1)

if __name__ == "__main__":
    main()
