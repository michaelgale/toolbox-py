#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
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
from pathlib import Path
import crayons
from .niceprint import colour_path_str, file_size_str

# File type groups
image_files = [
    "jpg",
    "jpeg",
    "png",
    "tiff",
    "bmp",
    "pxm",
    "gif",
    "ico",
    "raw",
    "ppm",
    "pgm",
    "pbm",
    "pnm",
    "tif",
    "xcf",
    "xpm",
    "psd",
    "pict",
    "xbm",
    "icns",
    "exif",
    "nef",
]
archive_files = [
    "dmg",
    "zip",
    "gz",
    "tar",
    "bzip",
    "bz2",
    "7z",
    "arc",
    "lza",
    "jar",
    "rar",
    "tgz",
    "lzma",
    "tbz2",
    "iso",
    "msi",
    "cab",
    "rpm",
    "vdi",
    "vmdk",
    "deb",
    "egg",
    "pack",
    "xip",
    "pickle",
    "pkl",
    "whl",
    "wheel",
]
media_files = [
    "mov",
    "mp4",
    "avi",
    "xvid",
    "webm",
    "mpg",
    "mpg2",
    "m4v",
    "mkv",
    "flv",
    "swf",
    "wmv",
    "mpeg",
    "asf",
    "3gp",
]
audio_files = [
    "wav",
    "mp3",
    "m4c",
    "m4a",
    "aiff",
    "flac",
    "ogg",
    "gsm",
    "aup",
    "ac3",
    "wma",
    "aac",
    "au",
    "m4p",
]
vector_files = [
    "svg",
    "ai",
    "wmf",
    "graffle",
    "eps",
    "cdr",
    "cgm",
    "vsd",
    "amf",
    "gstencil",
]
cad_files = [
    "dwg",
    "dxf",
    "step",
    "stl",
    "iges",
    "igs",
    "blend1",
    "blend",
    "dae",
    "obj",
    "ply",
    "pov",
    "vrml",
    "gbr",
    "pcb",
    "sch",
    "lbr",
    "FCStd",
    "brd",
]
doc_files = [
    "doc",
    "xls",
    "xlsx",
    "docx",
    "ppt",
    "pptx",
    "pages",
    "numbers",
    "keynote",
    "key",
    "pps",
    "gslides",
    "pdf",
    "txt",
    "md",
    "tex",
    "rst",
]
src_files = [
    "c",
    "cpp",
    "h",
    "hpp",
    "py",
    "pyi",
    "swift",
    "cxx",
    "hxx",
    "m",
    "mm",
    "js",
    "java",
    "sh",
    "v",
    "vhd",
    "vhdl",
    "nib",
    "cc",
    "asm",
    "scr",
    "ulp",
    "xcodeproj",
    "lua",
    "pl",
    "pm",
    "rb",
    "scpt",
    "rs",
    "ipynb",
    "coffee",
    "vcproj",
    "lproj",
    "sln",
    "tcl",
]
web_files = [
    "html",
    "htm",
    "php",
    "css",
    "cgi",
    "rss",
    "rw",
    "rw6",
    "rw7",
    "webarchive",
]
obj_files = [
    "o",
    "a",
    "lib",
    "pyc",
    "coff",
    "elf",
    "dll",
    "so",
    "war",
    "com",
    "class",
    "ipa",
    "hex",
    "framework",
    "dvi",
    "dylib",
    "sdk",
    "swiftmodule",
    "pch",
]
lego_files = ["ldr", "lxf", "mpd", "dat", "ldd", "ldraw", "bbm", "pub"]
cfg_files = ["cfg", "ini", "plist", "rc", "config", "xcconfig", "yml", "json", "conf"]
font_files = ["ttf", "otf", "woff", "eot", "pfb", "afm", "woff2"]
app_files = ["app", "exe", "bundle"]
data_files = [
    "csv",
    "sqlite",
    "sqlite3",
    "log",
    "xml",
    "sqlitedb",
    "db",
    "data",
    "dtbase2",
    "dtmeta",
]

file_groups = {
    "Images": image_files,
    "Audio": audio_files,
    "Media": media_files,
    "Archive": archive_files,
    "Vector": vector_files,
    "CAD": cad_files,
    "Documents": doc_files,
    "Source code": src_files,
    "Web": web_files,
    "Object code": obj_files,
    "Lego": lego_files,
    "Config": cfg_files,
    "Fonts": font_files,
    "Apps": app_files,
    "Data": data_files,
}


def get_file_group(ext, fsgroup, size):
    for k, v in file_groups.items():
        if ext.lower() in v:
            if k in fsgroup:
                fsgroup[k][0] += 1
                fsgroup[k][1] += size
            else:
                fsgroup[k] = [1, size]
    return fsgroup


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
    if "~" in str(file):
        return os.path.expanduser(file)
    return os.path.expanduser(os.path.abspath(file))


def split_path(file):
    """ Returns a tuple containing a file's (directory, name.ext)"""
    if os.path.isdir(file):
        return full_path(file), None
    return os.path.split(full_path(file))


def split_filename(file):
    """ Splits a file name into base name and extension """
    return os.path.splitext(file)


def colour_list_str(t1, q1, s1, t2, q2, s2, style="colour"):
    def _column(t, q, s):
        cs = []
        cs.append(str(crayons.normal("%15s" % (t))))
        cs.append(" : ")
        cs.append(str(crayons.cyan("%-6d" % (q))))
        cs.append("(%10s)" % (file_size_str(s, style=style)))
        return "".join(cs)

    s = []
    s.append(_column(t1, q1, s1))
    s.append("  ")
    s.append(_column(t2, q2, s2))
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
        self.last_file = ""

    def verify_file(self, file):
        """ Checks if a file exists """
        if not os.path.isfile(full_path(file)):
            if self.verbose:
                self.colprint("File ", file, " does not exist", "red")
            return False
        return True

    def choose_safe_filename(self, file):
        """Checks if a file already exists and returns a alternative
        filename with a suffix "-1", "-2", ... until a unique name is found,
        otherwise it will simply return the file name as is"""
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
        """ Checks if a name refers to a file rather than a directory """
        dirname = full_path(name)
        if os.path.isfile(dirname):
            if self.verbose:
                self.colprint(
                    "A file with same name ", name, " already exists", "yellow"
                )
            return False
        return True

    def rename_file(self, src, dest):
        """Renames supplied file src with name dest.
        If renamed file already exists, it will ignore the request
        unless overwrite is True.  Returns True if the operation is
        performed and False otherwise."""
        if not self.verify_file(src):
            return False
        srcdir, srcname = split_path(src)
        # strip any superfluous path info from dest
        destdir, destname = split_path(dest)
        newpath = os.path.normpath(srcdir + os.sep + destname)
        self.last_file = newpath
        # check for trivial rename with same name
        if srcname == destname:
            return True
        if self.safe_overwrite:
            newpath = self.choose_safe_filename(newpath)
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
        """Moves supplied file src to new location specified with dest.
        If moved file already exists, it will ignore the request
        unless overwrite or safe_overwrite is True.  Returns True if the
        operation is performed and False otherwise."""
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
                shutil.move(full_path(src), newpath)
            if self.verbose:
                self.colprint("File ", srcname, " moved to ", "green", dest)
            return True
        if self.verbose:
            self.colprint(
                "Moved file ", srcname, " already exists in ", "yellow", destdir
            )
        return False

    def copy_file(self, src, dest):
        """Copies supplied file src to new location specified with dest.
        If copied file already exists, it will ignore the request
        unless overwrite or safe_overwrite is True.  Returns True if
        the operation is performed and False otherwise."""
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
        """Removes a directory.  If remove_all is True, then it
        will also remove all of the directory's content including
        files and subdirectories.  Otherwise, we assume we are
        removing an empty directory"""
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
        """Removes all files for a directory.  If remove_subdir is
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

    def get_file_list(self, path, spec="*", recursive=False, as_iterator=False):
        """ Gets a file listing from the root of the specified path """
        if not self.verify_dir_not_file(path):
            return False
        dirname = full_path(path)
        if os.path.isdir(dirname):
            files = Path(dirname).rglob(spec)
            if as_iterator:
                return files
            return list(files)
        elif self.verbose:
            self.colprint("Directory ", dirname, " does not exist", "red")
        return False

    def print_dir_summary(self, path, colour_list=True):
        """ Gets a sub-directory listing from the root of the specified path """
        if not self.verify_dir_not_file(path):
            return False
        dirname = full_path(path)
        if os.path.isdir(dirname):
            fs = {
                "dir_count": 0,
                "file_count": 0,
                "max_size": 0,
                "total_size": 0,
                "mean_size": 0,
                "dir_size": {},
            }
            longest_name = 0
            files = Path(dirname).glob("*")
            for file in files:
                size = 0
                f, e = split_filename(file)
                ext = e.replace(".", "").lower()
                if os.path.isdir(file):
                    size = sum(
                        f.stat().st_size for f in file.glob("**/*") if f.is_file()
                    )
                    subdir = str(file).replace(dirname, "").replace(os.sep, "")
                    fs["dir_size"][subdir] = size
                    fs["dir_count"] += 1
                    longest_name = max(len(subdir), longest_name)
                elif os.path.isfile(file):
                    fs["file_count"] += 1
                    size = os.path.getsize(file)
                fs["total_size"] += size
                fs["max_size"] = max(size, fs["max_size"])
            if fs["file_count"] > 0:
                fs["mean_size"] = fs["total_size"] / fs["dir_count"]
            print("Directory: " + crayons.blue(dirname, bold=True))
            print("  Files         : " + crayons.cyan(fs["file_count"]))
            print("  Directories   : " + crayons.cyan(fs["dir_count"]))
            print("  Total size    : " + file_size_str(fs["total_size"], style="mono"))
            print("  Max size      : " + file_size_str(fs["max_size"], style="mono"))
            print("  Average size  : " + file_size_str(fs["mean_size"], style="mono"))
            listext = sorted(fs["dir_size"].items(), key=lambda x: x[1], reverse=True)
            longest_name = max(15, longest_name)
            fmt = "%%%ds : %%10s" % (longest_name)
            style = "colour" if colour_list else "mono"
            for el in listext:
                sd = " " * (longest_name - len(el[0])) + crayons.blue(el[0], bold=True)
                print(fmt % (sd, file_size_str(el[1], style=style)))

        elif self.verbose:
            self.colprint("Directory ", dirname, " does not exist", "red")
        return False

    def print_file_summary(self, path, recursive=False, colour_list=True):
        """ Gets a file listing from the root of the specified path """
        if not self.verify_dir_not_file(path):
            return False
        dirname = full_path(path)
        if os.path.isdir(dirname):
            if recursive:
                files = Path(dirname).rglob("*")
            else:
                files = Path(dirname).glob("*")

            fs = {
                "dir_count": 0,
                "file_count": 0,
                "file_types": 0,
                "max_size": 0,
                "total_size": 0,
                "mean_size": 0,
                "file_ext": {},
                "file_groups": {},
            }
            for file in files:
                size = 0
                f, e = split_filename(file)
                ext = e.replace(".", "").lower()

                if os.path.isdir(file):
                    fs["dir_count"] += 1
                    if len(ext) > 0:
                        size = sum(
                            f.stat().st_size for f in file.glob("**/*") if f.is_file()
                        )
                elif os.path.isfile(file):
                    fs["file_count"] += 1
                    size = os.path.getsize(file)
                    fs["max_size"] = max(size, fs["max_size"])
                    fs["total_size"] += size
                if len(ext) > 0:
                    if ext in fs["file_ext"]:
                        fs["file_ext"][ext][0] += 1
                        fs["file_ext"][ext][1] += size
                    else:
                        fs["file_ext"][ext] = [1, size]
                    fs["file_groups"] = get_file_group(ext, fs["file_groups"], size)
            fs["file_types"] = len(fs["file_ext"])
            if fs["file_count"] > 0:
                fs["mean_size"] = fs["total_size"] / fs["file_count"]
            print("Directory: " + crayons.blue(dirname, bold=True))
            print("  Files         : " + crayons.cyan(fs["file_count"]))
            print("  Directories   : " + crayons.cyan(fs["dir_count"]))
            print("  Total size    : " + file_size_str(fs["total_size"], style="mono"))
            print("  Max size      : " + file_size_str(fs["max_size"], style="mono"))
            print("  Average size  : " + file_size_str(fs["mean_size"], style="mono"))
            print(
                crayons.white("  File types    : ", bold=True)
                + crayons.cyan(fs["file_types"])
            )
            listext = sorted(
                fs["file_ext"].items(), key=lambda x: x[1][1], reverse=True
            )
            ccount, csize = 0, 0
            minsize = 0.95 * (fs["total_size"])
            mincount = 0.95 * (fs["file_count"])
            maxcount = min(64, 0.95 * fs["file_types"])
            exts, qtys, sizes = [], [], []
            for i, el in enumerate(listext):
                if (ccount < mincount or csize < minsize) and i < maxcount:
                    exts.append(el[0][:15])
                    qtys.append(el[1][0])
                    sizes.append(el[1][1])
                ccount += el[1][0]
                csize += el[1][1]
            cs = sorted(zip(exts, qtys, sizes), key=lambda x: x[1], reverse=True)
            style = "colour" if colour_list else "mono"
            for e, q, s, c in zip(exts, qtys, sizes, cs):
                print(colour_list_str(e, q, s, c[0], c[1], c[2], style))
            listgroup = sorted(
                fs["file_groups"].items(), key=lambda x: x[1][1], reverse=True
            )
            print(crayons.white("   File groups  :", bold=True))
            exts, qtys, sizes = [], [], []
            for el in listgroup:
                exts.append(el[0][:15])
                qtys.append(el[1][0])
                sizes.append(el[1][1])
            cs = sorted(zip(exts, qtys, sizes), key=lambda x: x[1], reverse=True)
            for e, q, s, c in zip(exts, qtys, sizes, cs):
                print(colour_list_str(e, q, s, c[0], c[1], c[2], style))

        elif self.verbose:
            self.colprint("Directory ", dirname, " does not exist", "red")
        return False
