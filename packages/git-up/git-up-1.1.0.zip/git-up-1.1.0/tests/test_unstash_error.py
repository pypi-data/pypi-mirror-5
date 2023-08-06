# System imports
import os
from os.path import join

# 3rd party libs
from nose.tools import *
from git import *

# PyGitup imports
from PyGitUp.git_wrapper import GitError
from tests import basepath, write_file, init_master, testfile_name

test_name = 'unstash_error'
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

    # Modify file in master
    master_path_file = join(master_path, testfile_name)
    write_file(master_path_file, 'contents')
    master.index.add([master_path_file])
    master.index.commit(test_name)

    # Modify file in repo
    path_file = join(path, testfile_name)
    os.unlink(path_file)


@raises(GitError)
def test_unstash_error():
    """ Run 'git up' with an unclean unstash """
    os.chdir(repo_path)

    from PyGitUp.gitup import GitUp
    gitup = GitUp(testing=True)
    gitup.run()
