"""
Logging reader
"""
import os
import re

from django.db import models

from settings import *

class LogFilesManager(object):

    def list_logfiles(self, path):
        """Returns list of files in provided path"""
        file_list = []
        # List only files
        for root,directory,files in os.walk(path):
            for f in files:
                # List only readable files
                try:
                    fi = open(os.path.join(path, f))
                    fi.close()
                    file_list.append(f)
                except Exception:
                    pass
        return file_list

    def get_file(self, file_full_path):
        fobj = open(file_full_path)
        return fobj

    def parse_log_file(self, logfile, from_line=0):
        """Returns parsed read file

        in form of entry names header (taken from Rgex group names)
        and lines tuples list"""
        # Reading file
        logfile.seek(0)
        read_file = logfile.readlines()
        # Creating Regexp prog to match entries
        file_dict = []
        prog = re.compile(LOG_FILES_RE)
        # Reading amount of lines
        line_num = from_line
        for count in range(LOG_FILES_PAGINATE_LINES):
            try:
                line = read_file[line_num]
                matches_set = prog.findall(str(line))
                file_dict.append(matches_set)
                line_num += 1
            except IndexError:
                # log file is shorter then LOG_FILES_PAGINATE_LINES or
                # amount of lines smaller then from_line left
                pass

        # Making file length data
        file_len = read_file.__len__
        # Making logfile indexes header
        header_length = prog.groups
        header_list = []
        if prog.groupindex:
            for number in range(header_length):
                header_list.append(number)
            for group_name, index in prog.groupindex.iteritems():
                header_list[int(index) - 1] = group_name
        return (file_len, header_list, file_dict)

class string_with_title(str):
    def __new__(cls, value, title):
        instance = str.__new__(cls, value)
        instance._title = title
        return instance

    def title(self):
        return self._title

    __copy__ = lambda self: self
    __deepcopy__ = lambda self, memodict: self

class LogFile(models.Model):
    """Hack object to be added to Django admin"""
    class Meta:
        app_label = string_with_title("django_log_file_viewer", "Django Log Files")
    verbose_name = 'Django Log File'
    verbose_name_plural = 'Django Log Files'
