import argparse
import builders
import sys
import os

def main():
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-type", dest='build_type', choices=["Release", "Debug"], default="Release")
    parser.add_argument("--path", "-p", dest='path', default="thirdparty")

    args = parser.parse_args()

    # Build directory zip
    if not os.path.isdir(args.path):
        os.mkdir(args.path)

    # Build shaderc
    print("Build Shaderc")

    shaderc_builder = builders.Shaderc(args)
    if not shaderc_builder.build():
        print("Failed to build Shaderc")
        sys.exit(1)

    if not shaderc_builder.copy_files():
        print("Failed to copy files from Shaderc")
        sys.exit(1)

if __name__ == "__main__":
    main()
