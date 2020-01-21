#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Misc file utilities
#

import sys, os
import os.path
import shutil
import crayons

# This useful context manager is based on the CadQuery FreeCAD plugin
class SuppressStdoutStderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


def full_path(file):
    """ Returns the fully expanded path of a file"""
    return os.path.expanduser(os.path.abspath(file))


def split_path(file):
    """ Returns a tuple containing a file's (directory, name.ext)"""
    if os.path.isdir(file):
        return full_path(file), None
    return os.path.split(full_path(file))


def split_filename(file):
    """ Splits a file name into base name and extension """
    return os.path.splitext(file)


def colour_path_str(file):
    fp = full_path(file)
    d, f = split_path(fp)
    s = []
    if f is not None:
        if len(file) == len(f):
            s.append(str(crayons.cyan(file, bold=True)))
        else:
            idx = file.find(f) - 1
            s.append(str(crayons.blue(file[:idx] + os.sep, bold=True)))
            if os.path.isfile(fp):
                s.append(str(crayons.cyan(f, bold=True)))
            elif os.path.isdir(fp):
                s.append(str(crayons.blue(f, bold=True)))
            else:
                s.append(str(crayons.cyan(f, bold=True)))
    else:
        if os.path.isdir(fp):
            s.append(str(crayons.blue(file + os.sep, bold=True)))
        else:
            s.append(str(crayons.cyan(file, bold=True)))
    return "".join(s)


class FileOps:
    """A convenience access class to perform file system 
    operations such as renaming, moving, or copying files.
    This class allows all operations to be "masked" for simulation
    so that file operations are non-destructive and can be
    "dry run" before actually being performed.  File operations
    can also be verbosely logged for debugging or information.
    """

    def __init__(self, simulate=False, verbose=False, overwrite=False):
        self.simulate = simulate
        self.verbose = verbose
        self.overwrite = overwrite
        self.safe_overwrite = True
        self.verbose_errors_only = True

    def verify_file(self, file):
        if not os.path.isfile(full_path(file)):
            if self.verbose:
                self.colprint("File ", file, " does not exist", "red")
            return False
        return True

    def choose_safe_filename(self, file):
        fp = full_path(file)
        if os.path.isfile(fp):
            d, f1 = split_path(fp)
            f, e = split_filename(f1)
            ok = False
            suffix = 1
            while not ok:
                new_name = os.path.abspath(d + os.sep + f + "-" + str(suffix) + e)
                suffix += 1
                ok = not os.path.isfile(full_path(new_name))
            if self.verbose:
                self.colprint("Using safe filename ", new_name, " for ", "yellow", file)
            return new_name
        return file

    def colprint(self, prefix, name, suffix, colour="white", name2=None):
        if self.verbose_errors_only and colour == "green":
            pass
        else:
            s = []
            if self.simulate:
                s.append(str(crayons.black(prefix, bold=True)))
            else:
                s.append(str(crayons.normal(prefix)))
            s.append(colour_path_str(name))
            if colour.lower() == "red":
                s.append(str(crayons.red(suffix)))
            elif colour.lower() == "yellow":
                s.append(str(crayons.yellow(suffix)))
            elif colour.lower() == "green":
                s.append(str(crayons.green(suffix)))
            else:
                s.append(str(crayons.normal(suffix)))
            if name2 is not None:
                s.append(colour_path_str(name2))
            print("".join(s))

    def verify_dir_not_file(self, name):
        dirname = full_path(name)
        if os.path.isfile(dirname):
            if self.verbose:
                self.colprint(
                    "A file with same name ", name, " already exists", "yellow"
                )
            return False
        return True

    def rename_file(self, src, dest):
        """ Renames supplied file src with name dest. 
        If renamed file already exists, it will ignore the request
        unless overwrite is True.  Returns True if the operation is
        performed and False otherwise. """
        if not self.verify_file(src):
            return False
        srcdir, srcname = split_path(src)
        # strip any superfluous path info from dest
        destdir, destname = split_path(dest)
        newpath = os.path.normpath(srcdir + os.sep + destname)
        if not os.path.isfile(newpath) or self.overwrite:
            if not self.simulate:
                os.rename(full_path(src), newpath)
            if self.verbose:
                self.colprint("File ", srcname, " renamed to ", "green", destname)
            return True
        if self.verbose:
            self.colprint("Renamed file ", destname, " already exists", "yellow")
        return False

    def move_file(self, src, dest):
        """ Moves supplied file src to new location specified with dest. 
        If moved file already exists, it will ignore the request
        unless overwrite or safe_overwrite is True.  Returns True if the
        operation is performed and False otherwise. """
        if not self.verify_file(src):
            return False
        srcdir, srcname = split_path(src)
        # strip any superfluous name component from dest
        destdir, destname = split_path(dest)
        newpath = os.path.normpath(destdir + os.sep + srcname)
        if self.safe_overwrite:
            newpath = self.choose_safe_filename(newpath)
        if not os.path.isfile(newpath) or self.overwrite:
            if not self.simulate:
                os.rename(full_path(src), newpath)
            if self.verbose:
                self.colprint("File ", srcname, " moved to ", "green", dest)
            return True
        if self.verbose:
            self.colprint(
                "Moved file ", srcname, " already exists in ", "yellow", destdir
            )
        return False

    def copy_file(self, src, dest):
        """ Copies supplied file src to new location specified with dest.
        If copied file already exists, it will ignore the request
        unless overwrite or safe_overwrite is True.  Returns True if 
        the operation is performed and False otherwise. """
        if not self.verify_file(src):
            return False
        srcdir, srcname = split_path(src)
        # strip any superfluous name component from dest
        destdir, destname = split_path(dest)
        if destname is not None:
            newpath = full_path(dest)
        else:
            newpath = os.path.normpath(destdir + os.sep + srcname)
        if self.safe_overwrite:
            newpath = self.choose_safe_filename(newpath)
        if not os.path.isfile(newpath) or self.overwrite:
            if not self.simulate:
                shutil.copyfile(full_path(src), newpath)
            if self.verbose:
                self.colprint("File ", srcname, " copied to ", "green", dest)
            return True
        if self.verbose:
            self.colprint(
                "Copied file ", srcname, " already exists in ", "yellow", dest
            )
        return False

    def make_directory(self, name):
        """ Creates a directory with name """
        if not self.verify_dir_not_file(name):
            return False
        dirname = full_path(name)
        if not os.path.isdir(dirname):
            try:
                if not self.simulate:
                    os.mkdir(dirname)
                if self.verbose:
                    self.colprint("Directory ", name, " created", "green")
                return True
            except OSError:
                self.colprint("Directory ", dirname, " cannot be created", "red")
        else:
            if self.verbose:
                self.colprint("Directory ", name, " already exists", "yellow")
        return False

    def remove_file(self, file):
        """ Removes specified file """
        filepath = full_path(file)
        if os.path.isfile(filepath):
            if not self.simulate:
                os.remove(filepath)
            if self.verbose:
                self.colprint("File ", file, " removed", "green")
            return True
        elif self.verbose:
            self.colprint("File ", file, " does not exist", "red")
        return False

    def remove_dir(self, name, remove_all=False):
        """ Removes a directory.  If remove_all is True, then it
        will also remove all of the directory's content including
        files and subdirectories.  Otherwise, we assume we are 
        removing an empty directory """
        if not self.verify_dir_not_file(name):
            return False
        dirname = full_path(name)
        if os.path.isdir(dirname):
            try:
                if self.verbose:
                    if remove_all:
                        self.colprint(
                            "Directory ", name, " and its contents removed", "green"
                        )
                    else:
                        self.colprint("Directory ", name, " removed", "green")
                if not self.simulate:
                    if remove_all:
                        shutil.rmtree(dirname)
                    else:
                        os.rmdir(dirname)
                return True
            except OSError:
                self.colprint("Directory ", dirname, " could not be removed", "red")
        else:
            if self.verbose:
                self.colprint("Directory ", name, " does not exist", "red")
        return False

    def remove_files_from_dir(self, name, remove_subdir=False):
        """ Removes all files for a directory.  If remove_subdir is 
        True, then it also removes all subdirectories (and their contents)
        in addition to files.  The resulting empty directory will still
        exist; the remove_dir method can be used to remove the directory
        afterwards."""
        if not self.verify_dir_not_file(name):
            return False
        dirname = full_path(name)
        if os.path.isdir(dirname):
            for root, dirs, files in os.walk(dirname):
                for f in files:
                    if self.verbose:
                        self.colprint("Removing file ", f, " from ", "green", root)
                    if not self.simulate:
                        os.unlink(os.path.join(root, f))
                if remove_subdir:
                    for d in dirs:
                        if self.verbose:
                            self.colprint(
                                "Removing sub-directory ", d, " from ", "green", root
                            )
                        if not self.simulate:
                            shutil.rmtree(os.path.join(root, d))
                return True
        elif self.verbose:
            self.colprint("Directory ", dirname, " does not exist", "red")
        return False

