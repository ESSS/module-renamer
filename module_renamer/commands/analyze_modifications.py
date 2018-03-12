import ast
import fnmatch
import os
from collections import Counter, namedtuple
from contextlib import contextmanager

from click import ClickException, confirm, echo
from git import Repo
from tqdm import tqdm

CONFLICT_MSG = (
    "\n"
    "Unfortunately, you moved two objects with the same name on different paths.\n"
    "This situation could be catastrophic while running the script for rename the imports. \n"
    "These are the imports that have conflict: \n "
    " -> {} \n"
)

INFORMATIVE_CONFLICT_MSG = (
    "Do you want to generate the file without this import? \n"
    "Otherwise this script will be aborted."
)

Import = namedtuple("Import", ["module", "name"])


@contextmanager
def checkout_branch(repo, branch_name):
    """
    Change the current git branch for the branch informed on branch_name

    :param git.Repo repo: The git repository of the project.

    :param str branch_name: Name of the branch that Git should move into
    """

    if (repo.is_dirty() or len(repo.untracked_files)) != 0:
        raise ClickException("The repository is dirty, please clean it first ")

    current_branch = repo.active_branch.name
    repo.branches[branch_name].checkout()

    try:
        yield
    finally:
        getattr(repo.heads, current_branch).checkout()


def analyze_modifications(project_path, compare_with, branch, output_file):
    """
    Track modifications between two different branches.
    The output will be a list written directly to a file.
    """

    full_project_path = os.path.join(project_path)
    repo = Repo(project_path)

    origin_branch = compare_with

    if branch:
        work_branch = branch
    else:
        work_branch = repo.active_branch.name

    if origin_branch == work_branch:
        raise ClickException(
            "Origin and Working branch are the same. "
            "Please, change your activate branch to where you made you changes on the code, "
            "or use the option --branch and --compare-with ."
        )

    list_of_py_files = [i for i in walk_on_py_files(full_project_path)]
    with checkout_branch(repo, origin_branch):
        import_list_from_origin = {imp for imp in get_imports(full_project_path, list_of_py_files)}

    with checkout_branch(repo, work_branch):
        import_list_from_working = {imp for imp in
                                    get_imports(full_project_path, list_of_py_files)}

    list_with_modified_imports = generate_list_with_modified_imports(import_list_from_origin,
                                                                     import_list_from_working)
    write_list_to_file(list_with_modified_imports, output_file)


def write_list_to_file(list_with_modified_imports, file_name):
    """
    Write the list of modified imports on a python file, the python file per default will be named
    "list_output.py" but can be changed by passing the argument --output_file

    The name of the list (inside the file) cannot be changed since it will be used later on the
    script for renaming the project.
    """
    echo('Generating the file {0}'.format(file_name))

    with open(file_name, 'w') as file:
        file.write("imports_to_move = ")

        from pprint import pprint
        pprint(list(list_with_modified_imports), stream=file, indent=4, width=120)


def generate_list_with_modified_imports(import_list_from_origin, import_list_from_working):
    """
    This methods looks for imports that keep the same name but has has different modules path

    :return: A list with unique elements that has the same name but different modules path
    :rtype: set
    """

    origin_filtered, working_filtered = _filter_import(import_list_from_origin,
                                                       import_list_from_working)

    moved_imports = _find_moved_imports(origin_filtered, working_filtered)

    list_with_modified_imports = _check_for_conflicts(moved_imports)

    return list_with_modified_imports


def _filter_import(origin_import_list, working_import_list):
    """
    Create a new set with elements present origin_list or working_list but not on both,
    this helps to filter classes that could have same name but different modules.
    """
    difference = origin_import_list.symmetric_difference(working_import_list)
    origin_filtered = origin_import_list.intersection(difference)
    working_filtered = working_import_list.intersection(difference)
    return origin_filtered, working_filtered


def _find_moved_imports(list_with_import_from_origin_branch, list_with_import_from_working_branch):
    """
    Return a list with tuples where the first element is the origin and the second element is
    the branch with the modifications
    """
    list_with_modified_imports = {
        (origin.module + "." + origin.name, working.module + "." + working.name)
        for origin in list_with_import_from_origin_branch
        for working in list_with_import_from_working_branch
        if working.name is not '*'
        if origin.name == working.name
        if origin.module != working.module
    }
    return list_with_modified_imports


def _check_for_conflicts(list_with_modified_imports):
    """
    Checks if there is more than one object with the same module path.

    If any conflict is found, the script will display the list of conflicts for the user
    to decide either abort the script or create the list without the conflicted module path.
    """
    import_from = [modified_import[0] for modified_import in list(list_with_modified_imports)]
    imports_with_conflict = [class_name
                             for class_name, number_of_occurrences in Counter(import_from).items()
                             if number_of_occurrences > 1]
    if len(imports_with_conflict) > 0:
        echo(CONFLICT_MSG.format('\n -> '.join(imports_with_conflict)))

        if confirm(INFORMATIVE_CONFLICT_MSG, abort=True):
            list_with_modified_imports = [modified_import
                                          for modified_import in list_with_modified_imports
                                          if modified_import[0] not in imports_with_conflict
                                          if modified_import[1] not in imports_with_conflict]
    return list_with_modified_imports


def get_imports(project_path, list_of_py_files):
    # type: (str) -> Import
    """
    Look for all .py files on the given project path and return the import statements found on
    each file.

    Note.: I inserted the TQDM here because was the only way that I could have an accurate
    progress bar, feel free to share any thoughts or tips on how to improve this progress bar =)

    :type project_path: str
    :rtype: commands.utils.Import
    """
    with tqdm(total=len(list_of_py_files), unit='files', leave=False, desc=project_path) as pbar:
        for file_path in list_of_py_files:
            pbar.update()
            with open(file_path, mode='r') as file:
                file_content = ast.parse(file.read(), file_path)

            for node in ast.iter_child_nodes(file_content):
                if isinstance(node, ast.Import):
                    module = ''
                elif isinstance(node, ast.ImportFrom):
                    # node.module can be None when the following statement is used: from . import foo
                    if node.module is not None:
                        module = node.module
                    else:
                        module = ''
                else:
                    continue

                for name_node in node.names:
                    yield Import(module, name_node.name)


def walk_on_py_files(folder):
    """
    Walk through each python files in a directory
    """
    for dir_path, _, files in os.walk(folder):
        for filename in fnmatch.filter(files, '*.py'):
            yield os.path.abspath(os.path.join(dir_path, filename))
