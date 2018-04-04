from concurrent import futures

import pasta
import six
from click._unicodefun import click
from pasta.augment import rename
from tqdm import tqdm

from module_renamer.commands.utils import walk_on_py_files


def rename_modules(project_path, path_to_moved_imports_file):
    for path in project_path:
        execute_rename(path, path_to_moved_imports_file)


def execute_rename(project_path, path_to_moved_imports_file):
    """
    Main loop that interacts over all python files from the project and delegate
    to an executor to parse each file

    :param str project_path:
        Path to the project that is going to be parsed.

    :param str path_to_moved_imports_file:
        Path of the file with the list of changed imports.
    """
    list_of_py_files = list(walk_on_py_files(project_path))
    file_counter = len(list_of_py_files)

    with futures.ThreadPoolExecutor(max_workers=30) as executor:
        future_map = {
            executor.submit(rename_file, py_file, path_to_moved_imports_file): py_file
            for py_file in list_of_py_files
        }

        done_list = tqdm(futures.as_completed(future_map), total=file_counter, unit="files", leave=False)
        list_of_exception = []
        for future in done_list:
            file_name = future_map[future]
            try:
                future.result()
            except Exception as exc:
                list_of_exception.append((exc, file_name))

        if list_of_exception:
            summary_of_exceptions = ['The following exception(s) has occurred while parsing the files: \n']
            for exception, file_name in list_of_exception:
                msg = 'File {0} generated an exception: {1}'.format(file_name, exception)
                summary_of_exceptions.append(msg)

            raise click.ClickException('\n'.join([str(x) for x in summary_of_exceptions]))


def rename_file(file_path, path_to_moved_imports_file):
    """
    Iterates over the content of a file, looking for imports to be changed

    :param str file_path:
        Path of the file being parsed.
    :param str path_to_moved_imports_file:
        Path of the file with the list of changed imports.
    """
    list_with_moved_imports = _get_list_of_moved_imports(path_to_moved_imports_file)

    with open(file_path, mode='r') as file:
        tree = pasta.parse(file.read())
        for old_path, new_path in list_with_moved_imports:
            try:
                rename.rename_external(tree, old_path, new_path)
            except ValueError:
                raise click.ClickException("An error has occurred on the following path: {0} ,\n "
                                     "while trying to rename from: {1} to {2}"
                                     .format(file_path, old_path, new_path))
        source_code = pasta.dump(tree)

    with open(file_path, mode='w') as file:
        file.write(source_code)


def _get_list_of_moved_imports(path_to_moved_imports_file):
    """
    Return a list of moved imports from a given python file path

    :param str path_to_moved_imports_file:
        Path to the python file with a list of moved imports,
        generated from analyze difference command or created manually.

    """
    if six.PY2:
        import imp
        import_from_user = imp.load_source('moved_imports', path_to_moved_imports_file)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location("moved_imports", path_to_moved_imports_file)
        import_from_user = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(import_from_user)

    return import_from_user.imports_to_move
