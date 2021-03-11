import argparse
import os
import logging

from blur import blur_file

lgr = logging.getLogger(__name__)


image_file_extensions = ['.jpeg','.jpg','.png','.bmp']


def process_dir(base):
    """
    Process images in folder recursively
    :param base: Path to Root Folder
    :return: None
    """

    for file in os.listdir(base):
        path = os.path.join(base, file)
        if os.path.isdir(path):
            process_dir(path)
        else:
            filename = os.fsdecode(file)

            if any([filename.endswith(extension) for extension in image_file_extensions]):
                faces_count = blur_file(path)
                lgr.debug(f'Blurred {faces_count} faces in {path}')
            else:
                # Skip non image
                continue
        # break



def fs_path(path):
    """
    Validated path exists
    :param path: Filesystem Path
    :return: Path if exists
    """
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', type=fs_path, nargs='+', help='Paths to Images or Folders containing images')
    args = parser.parse_args()

    for path in args.paths:
        if os.path.isfile(path):
            blur_file(path)
        elif os.path.isdir(path):
            process_dir(path)
        else:
            lgr.error(f'Unknown Path: {path}')
