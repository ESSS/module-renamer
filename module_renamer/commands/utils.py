import fnmatch
import os

def walk_on_py_files(folder):
    """
    Walk through each python files in a directory
    """
    for dir_path, _, files in os.walk(folder):
        for filename in fnmatch.filter(files, '*.py'):
            yield os.path.abspath(os.path.join(dir_path, filename))
