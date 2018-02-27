# coding=utf-8


import os

import git
import pytest
from click.testing import CliRunner

from module_renamer.cli import track


@pytest.fixture()
def repo(tmpdir):
    """
    Creates a empty repository on the temp dir
    """
    repo = git.Repo.init(path=str(tmpdir))
    yield repo
    repo.close()


@pytest.fixture()
def create_scenario():
    """
    Commits the content from file_master and file_working_branch on the
    given git repository
    """

    def _create_scenario(repo, file_master, file_working_branch):
        file_path = os.path.join(repo.working_dir, 'file_a.py')

        with open(file_path, mode='w') as file:
            file.writelines(file_master)
        repo.index.add(['file_a.py'])
        repo.index.commit("commit on master")
        repo.heads.master.checkout(b='new_branch')

        with open(file_path, mode='w') as file:
            file.writelines(file_working_branch)
        repo.index.add(['file_a.py'])
        repo.index.commit("commit on working branch")

    return _create_scenario


@pytest.fixture()
def run_cli():
    def _run_cli(repo, input=None):
        runner = CliRunner()

        output_file = _output_file(repo)
        output_arg = '--output_file={0}'.format(output_file)

        return runner.invoke(track, [repo.working_dir, output_arg], input=input)

    return _run_cli


def test_track_without_modification(repo, create_scenario, run_cli):
    imports_for_file_a = ['from a.b import c\n', 'from d.e import f\n']
    imports_for_file_b = ['from g.h import i\n', 'from j.k import l\n']

    create_scenario(repo, imports_for_file_a, imports_for_file_b)

    result = run_cli(repo)

    assert result.exit_code == 0
    assert "test_list_output.py" in result.output

    output_file = _output_file(repo)
    with open(output_file, mode='r') as file:
        assert "imports_to_move = []" in file.read()


def test_track_with_modification(repo, create_scenario, run_cli):
    imports_for_file_a = ['from a.b import c\n', 'from d.e import f\n']
    imports_for_file_b = ['from x.x import c\n', 'from j.k import l\n']
    create_scenario(repo, imports_for_file_a, imports_for_file_b)

    result = run_cli(repo)

    assert result.exit_code == 0
    assert "test_list_output.py" in result.output

    output_file = _output_file(repo)
    with open(output_file, mode='r') as file:
        assert "imports_to_move = [('a.b.c', 'x.x.c')]" in file.read()


def test_track_with_conflict(repo, create_scenario, run_cli):
    imports_for_file_a = ['from a.b import c\n', 'from b import c\n']
    imports_for_file_b = ['from x.x import c\n', 'from y import c\n']
    create_scenario(repo, imports_for_file_a, imports_for_file_b)

    result = run_cli(repo)

    assert result.exit_code == 1
    assert ("a.b.c" and "b.c") in result.output


def test_track_save_conflict(repo, create_scenario, run_cli):
    imports_for_file_a = ['from a.b import c\n', 'from b import c\n',
                          'from m import n\n']
    imports_for_file_b = ['from x.x import c\n', 'from y import c\n',
                          'from w import n\n']
    create_scenario(repo, imports_for_file_a, imports_for_file_b)

    result = run_cli(repo, input="y\n")

    assert result.exit_code == 0
    assert "test_list_output.py" in result.output

    output_file = _output_file(repo)
    with open(output_file, mode='r') as file:
        assert "imports_to_move = [('m.n', 'w.n')]" in file.read()


def _output_file(repo):
    return os.path.join(repo.working_dir, "test_list_output.py")
