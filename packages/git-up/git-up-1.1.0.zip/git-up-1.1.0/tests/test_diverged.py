# System imports
import os
from os.path import join

# 3rd party libs
from nose.tools import *
from git import *

# PyGitup imports
from tests import basepath, init_master, update_file

test_name = 'diverged'
repo_path = join(basepath, test_name + os.sep)


def setup():
    master_path, master = init_master(test_name)

    # Prepare master repo
    master.git.checkout(b=test_name)

    # Clone to test repo
    path = join(basepath, test_name)

    master.clone(path, b=test_name)
    repo = Repo(path, odbt=GitCmdObjectDB)

    assert repo.working_dir == path

    # Set git-up.rebase.auto to false
    repo.git.config('git-up.rebase.auto', 'false')

    # Modify file in master
    update_file(master, test_name)

    # Modify file in our repo
    update_file(repo, test_name)


def test_diverged():
    """ Run 'git up' with result: diverged """
    os.chdir(repo_path)

    from PyGitUp.gitup import GitUp
    gitup = GitUp(testing=True)
    gitup.run()

    assert_equal(len(gitup.states), 1)
    assert_equal(gitup.states[0], 'diverged')
