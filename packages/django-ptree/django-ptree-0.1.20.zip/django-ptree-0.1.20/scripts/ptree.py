#!/usr/bin/env python
import os, sys

from django.core.management import execute_from_command_line

STARTPROJECT = 'startproject'
STARTAPP = 'startapp'


if __name__ == "__main__":

    command = sys.argv[1]
    project_or_app_name = sys.argv[2]

    if command == STARTPROJECT:
        argv = ['', STARTPROJECT, 'template={}'.format('http://is.gd/ptree_project'), project_or_app_name]
    elif command == STARTAPP:
        argv = ['', STARTAPP, 'template={}'.format('http://is.gd/ptree_app'), project_or_app_name]
    else:
        print 'Available commands are: {}'.format(', '.join([STARTAPP, STARTPROJECT]))
        sys.exit(1)
    execute_from_command_line(argv)