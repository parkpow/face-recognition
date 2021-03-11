import errno
import os


def create_dirs(instance_dir):
    if not os.path.exists(os.path.dirname(instance_dir)):
        try:
            os.makedirs(os.path.dirname(instance_dir))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
