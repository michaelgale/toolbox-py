# system modules
import os.path

# my modules
from toolbox import *

VERBOSE = False


def test_full_path():
    fullpath = full_path("./tests/testfiles/file1.txt")
    assert fullpath.endswith("file1.txt")
    assert fullpath.startswith(os.sep)
    assert "testfiles" in fullpath


def test_split_path():
    path, name = split_path("./tests/testfiles/file1.txt")
    assert name == "file1.txt"
    assert path.startswith(os.sep)
    assert "testfiles" in path


fo = FileOps(simulate=True, verbose=VERBOSE, overwrite=False)
fo.verbose_errors_only = False
fo.safe_overwrite = False


def test_fileops():
    res = fo.get_file_list("./tests/testfiles", recursive=True)
    assert res
    res = fo.get_file_list("./tests/testfiles", spec="*.txt", recursive=False)
    assert res
    res = fo.get_file_list("./tests/testfiles/file1.txt", recursive=False)
    assert not res
    res = fo.rename_file("./tests/testfiles/file1.txt", "filex.txt")
    assert res
    res = fo.rename_file("./tests/testfiles/file1.txt", "file1.txt")
    assert res
    res = fo.move_file("./tests/testfiles/file1.txt", "./tests/testfiles/dir1")
    assert res
    res = fo.move_file("./tests/testfiles/file1.txt", "./tests/testfiles/blah")
    assert not res
    res = fo.remove_file("./tests/testfiles/file2.txt")
    assert res
    res = fo.remove_file("./tests/testfiles/blah.txt")
    assert not res
    res = fo.remove_file("./tests/testfiles/dir2")
    assert not res
    res = fo.copy_file("./tests/testfiles/file1.txt", "./tests/testfiles/dir2")
    assert res
    res = fo.copy_file("./tests/testfiles/blah.txt", "./tests/testfiles/dir2")
    assert not res
    res = fo.copy_file("./tests/testfiles/file1.txt", "./tests/testfiles/filey.txt")
    assert res
    res = fo.copy_file("./tests/testfiles/file1.txt", "./tests/testfiles")
    assert not res
    fo.safe_overwrite = True
    res = fo.copy_file("./tests/testfiles/file1.txt", "./tests/testfiles")
    fo.safe_overwrite = False
    assert res


def test_dirops():
    res = fo.make_directory("./tests/testfiles/file1.txt")
    assert not res
    res = fo.make_directory("./tests/testfiles/dir1")
    assert not res
    res = fo.make_directory("./tests/testfiles/newdir")
    assert res
    files = fo.get_file_list("./tests/testfiles", recursive=True)
    if VERBOSE:
        for f in files:
            print(str(f))
        fsumm = fo.print_file_summary("~/Code", recursive=True)
        fsumm = fo.print_dir_summary("~/Code")


def test_remove_ops():
    res = fo.remove_file("./tests/testfiles/file1.txt")
    assert res
    res = fo.remove_file("./tests/testfiles/blah.txt")
    assert not res
    res = fo.remove_dir("./tests/testfiles/file1.txt")
    assert not res
    res = fo.remove_dir("./tests/testfiles/dir1")
    assert res
    res = fo.remove_dir("./tests/testfiles/blah")
    assert not res
    res = fo.remove_files_from_dir("./tests/testfiles/file2.txt")
    assert not res
    res = fo.remove_files_from_dir("./tests/testfiles", remove_subdir=True)
    assert res


fs = FileOps(simulate=False, verbose=VERBOSE, overwrite=False)
fs.verbose_errors_only = False


def test_real_rename():
    res = fs.rename_file("./tests/testfiles/file1.txt", "abc.txt")
    assert res
    newfile = full_path("./tests/testfiles/abc.txt")
    res = os.path.isfile(newfile)
    assert res
    d, fn = split_path(newfile)
    assert fn == "abc.txt"
    res = fs.rename_file("./tests/testfiles/abc.txt", "file1.txt")
    assert res


def test_real_move():
    res = fs.move_file("./tests/testfiles/file1.txt", "./tests/testfiles/dir1")
    newfile = full_path("./tests/testfiles/dir1/file1.txt")
    res = os.path.isfile(newfile)
    assert res
    d, fn = split_path(newfile)
    assert fn == "file1.txt"
    res = fs.move_file("./tests/testfiles/dir1/file1.txt", "./tests/testfiles")
    assert res
    newfile = full_path("./tests/testfiles/file1.txt")
    res = os.path.isfile(newfile)
    assert res
    oldfile = full_path("./tests/testfiles/dir1/file1.txt")
    res = os.path.isfile(oldfile)
    assert not res


def test_real_copy():
    fs.overwrite = True
    fs.safe_overwrite = True
    res = fs.copy_file("./tests/testfiles/file2.txt", "./tests/testfiles/dir2")
    newfile = full_path("./tests/testfiles/dir2/file2.txt")
    res = os.path.isfile(newfile)
    assert res
    d, fn = split_path(newfile)
    assert fn == "file2.txt"
    res = fs.copy_file("./tests/testfiles/dir2/file2.txt", "./tests/testfiles")
    assert res
    newfile = full_path("./tests/testfiles/file2.txt")
    res = os.path.isfile(newfile)
    assert res
    oldfile = full_path("./tests/testfiles/dir2/file2.txt")
    res = os.path.isfile(oldfile)
    assert res
    res = fs.remove_file("./tests/testfiles/dir2/file2.txt")
    assert res
    res = os.path.isfile(oldfile)
    assert not res
    res = fs.remove_file("./tests/testfiles/file2-1.txt")
    assert res


def test_real_dir():
    res = fs.make_directory("./tests/testfiles/newdir")
    assert res
    res = fs.make_directory("./tests/testfiles/newdir")
    assert not res
    res = fs.copy_file("./tests/testfiles/file3.txt", "./tests/testfiles/newdir")
    assert res
    newfile = full_path("./tests/testfiles/newdir/file3.txt")
    res = os.path.isfile(newfile)
    assert res
    res = fs.remove_dir("./tests/testfiles/newdir", remove_all=True)
    assert res
    res = fs.remove_dir("./tests/testfiles/newdir")
    assert not res
