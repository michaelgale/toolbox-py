# Sample Test passing with nose and pytest

# system modules
import math, os.path
import sys
import pytest
import pprint
import string

# my modules
from toolbox import *

VERBOSE = False


def test_full_path():
    fullpath = full_path("./testfiles/file1.txt")
    assert fullpath.endswith("file1.txt")
    assert fullpath.startswith(os.sep)
    assert "testfiles" in fullpath


def test_split_path():
    path, name = split_path("./testfiles/file1.txt")
    assert name == "file1.txt"
    assert path.startswith(os.sep)
    assert "testfiles" in path


fo = FileOps(simulate=True, verbose=VERBOSE, overwrite=False)
fo.verbose_errors_only = False
fo.safe_overwrite = False

def test_fileops():
    res = fo.rename_file("./testfiles/file1.txt", "filex.txt")
    assert res
    res = fo.rename_file("./testfiles/file1.txt", "file1.txt")
    assert not res
    res = fo.move_file("./testfiles/file1.txt", "./testfiles/dir1")
    assert res
    res = fo.move_file("./testfiles/file1.txt", "./testfiles/blah")
    assert not res
    res = fo.remove_file("./testfiles/file2.txt")
    assert res
    res = fo.remove_file("./testfiles/blah.txt")
    assert not res
    res = fo.remove_file("./testfiles/dir2")
    assert not res
    res = fo.copy_file("./testfiles/file1.txt", "./testfiles/dir2")
    assert res
    res = fo.copy_file("./testfiles/blah.txt", "./testfiles/dir2")
    assert not res
    res = fo.copy_file("./testfiles/file1.txt", "./testfiles/filey.txt")
    assert res
    res = fo.copy_file("./testfiles/file1.txt", "./testfiles")
    assert not res
    fo.safe_overwrite = True
    res = fo.copy_file("./testfiles/file1.txt", "./testfiles")
    fo.safe_overwrite = False
    assert res


def test_dirops():
    res = fo.make_directory("./testfiles/file1.txt")
    assert not res
    res = fo.make_directory("./testfiles/dir1")
    assert not res
    res = fo.make_directory("./testfiles/newdir")
    assert res


def test_remove_ops():
    res = fo.remove_file("./testfiles/file1.txt")
    assert res
    res = fo.remove_file("./testfiles/blah.txt")
    assert not res
    res = fo.remove_dir("./testfiles/file1.txt")
    assert not res
    res = fo.remove_dir("./testfiles/dir1")
    assert res
    res = fo.remove_dir("./testfiles/blah")
    assert not res
    res = fo.remove_files_from_dir("./testfiles/file2.txt")
    assert not res
    res = fo.remove_files_from_dir("./testfiles", remove_subdir=True)
    assert res


fs = FileOps(simulate=False, verbose=VERBOSE, overwrite=False)
fs.verbose_errors_only = False


def test_real_rename():
    res = fs.rename_file("./testfiles/file1.txt", "abc.txt")
    assert res
    newfile = full_path("./testfiles/abc.txt")
    res = os.path.isfile(newfile)
    assert res
    d, fn = split_path(newfile)
    assert fn == "abc.txt"
    res = fs.rename_file("./testfiles/abc.txt", "file1.txt")
    assert res


def test_real_move():
    res = fs.move_file("./testfiles/file1.txt", "./testfiles/dir1")
    newfile = full_path("./testfiles/dir1/file1.txt")
    res = os.path.isfile(newfile)
    assert res
    d, fn = split_path(newfile)
    assert fn == "file1.txt"
    res = fs.move_file("./testfiles/dir1/file1.txt", "./testfiles")
    assert res
    newfile = full_path("./testfiles/file1.txt")
    res = os.path.isfile(newfile)
    assert res
    oldfile = full_path("./testfiles/dir1/file1.txt")
    res = os.path.isfile(oldfile)
    assert not res


def test_real_copy():
    fs.overwrite = True
    fs.safe_overwrite = True
    res = fs.copy_file("./testfiles/file2.txt", "./testfiles/dir2")
    newfile = full_path("./testfiles/dir2/file2.txt")
    res = os.path.isfile(newfile)
    assert res
    d, fn = split_path(newfile)
    assert fn == "file2.txt"
    res = fs.copy_file("./testfiles/dir2/file2.txt", "./testfiles")
    assert res
    newfile = full_path("./testfiles/file2.txt")
    res = os.path.isfile(newfile)
    assert res
    oldfile = full_path("./testfiles/dir2/file2.txt")
    res = os.path.isfile(oldfile)
    assert res
    res = fs.remove_file("./testfiles/dir2/file2.txt")
    assert res
    res = os.path.isfile(oldfile)
    assert not res
    res = fs.remove_file("./testfiles/file2-1.txt")
    assert res


def test_real_dir():
    res = fs.make_directory("./testfiles/newdir")
    assert res
    res = fs.make_directory("./testfiles/newdir")
    assert not res
    res = fs.copy_file("./testfiles/file3.txt", "./testfiles/newdir")
    assert res
    newfile = full_path("./testfiles/newdir/file3.txt")
    res = os.path.isfile(newfile)
    assert res
    res = fs.remove_dir("./testfiles/newdir", remove_all=True)
    assert res
    res = fs.remove_dir("./testfiles/newdir")
    assert not res

