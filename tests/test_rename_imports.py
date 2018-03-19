import os

import pytest
from click.testing import CliRunner
from module_renamer.cli import rename


@pytest.fixture
def run_cli_rename():
    def _run_cli_rename(dir, file):
        from click.testing import CliRunner
        runner = CliRunner()
        return runner.invoke(rename, [dir, file])

    return _run_cli_rename


def test_run_rename(tmpdir, run_cli_rename):
    # Create Test Case Scenario
    os.makedirs(os.path.join(str(tmpdir), 'src'))
    file_path = os.path.join(str(tmpdir), 'src', 'file_a.py')

    with open(file_path, 'w+') as file:
        file.writelines(['from a.b import c\n', 'from d.e import f\n'])

    # Create the file with the list of imports to move
    file_with_the_imports_to_move = os.path.join(str(tmpdir), "list_output.py")
    with open(file_with_the_imports_to_move, 'w+') as file:
        file.writelines("imports_to_move = [('a.b.c', 'x.x.c')]")

    path_to_directory = os.path.join(str(tmpdir), 'src')

    result = run_cli_rename(path_to_directory, file_with_the_imports_to_move)

    assert result.exit_code == 0
    with open(file_path, mode='r') as file:
        assert file.read() == "from x.x import c\nfrom d.e import f\n"




