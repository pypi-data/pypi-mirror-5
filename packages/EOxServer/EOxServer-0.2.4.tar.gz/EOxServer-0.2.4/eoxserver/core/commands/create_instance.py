#!/usr/bin/env python
#-------------------------------------------------------------------------------
# $Id: create_instance.py 2358 2013-03-15 13:20:17Z meissls $
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#          Stephan Krause <stephan.krause@eox.at>
#          Stephan Meissl <stephan.meissl@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------

"""
Create a new EOxServer instance. This instance will create a root directory 
with the instance name in the given (optional) directory.
"""

import shutil
import os, sys
import django.core.management
from optparse import make_option

import eoxserver
from eoxserver.core.management import EOxServerAdminCommand

# tags to be replaced in the template files
TAG_PATH_SRC = "<$PATH_SRC$>"
TAG_PATH_DST = "<$PATH_DST$>"
TAG_INSTANCE_ID = "<$INSTANCE_ID$>"

class Command(EOxServerAdminCommand):
    option_list = EOxServerAdminCommand.option_list + (                                             
        make_option('--id', nargs=1, action='store', metavar='INSTANCE_ID',
            help='Mandatory name of the eoxserver instance.'
        ),
        make_option('-d', '--dir', default='.', 
            help='Optional base directory. Defaults to the current directory.'
        ),
        make_option('--initial_data', metavar='filename', default=False,
            help='Location of the initial data. Must be in JSON format.'
        ),
        make_option('--init_spatialite', action='store_true',
            help='Flag to initialize the sqlite database.'
        )
    )
    
    help = ("Creates a new EOxServer instance with all necessary files and "
            "folder structure.")
    args = ("--id INSTANCE_ID [--dir DIR --initial_data DIR --init_spatialite]")
    
    def handle(self, *args, **options):
        instance_id = options['id']
        if instance_id is None:
            if len(args) == 1:
                instance_id = args[0]
            else:
                self.parser.error("Instance ID not given.")
        
        dst_root_dir = os.path.abspath(options['dir'])
        if django.VERSION[:2] >= (1, 4):
            dst_inst_dir = os.path.join(dst_root_dir, instance_id, instance_id)
        else:
            dst_inst_dir = os.path.join(dst_root_dir, instance_id)
        dst_conf_dir = os.path.join(dst_inst_dir, "conf")
        dst_data_dir = os.path.join(dst_inst_dir, "data")
        dst_logs_dir = os.path.join(dst_inst_dir, "logs")
        dst_static_dir = os.path.join(dst_inst_dir, "static")
        dst_fixtures_dir = os.path.join(dst_data_dir, "fixtures")
        dst_templates_dir = os.path.join(dst_inst_dir, "templates")
        dst_templates_admin_dir = os.path.join(dst_templates_dir, "admin")

        src_root_dir = os.path.dirname(eoxserver.__file__)
        src_conf_dir = os.path.join(src_root_dir, "conf")
        if not os.path.isfile(os.path.join(src_conf_dir, "TEMPLATE_eoxserver.conf")):
            src_conf_dir = os.path.join(sys.prefix, "eoxserver/conf")
            if not os.path.isfile(os.path.join(src_conf_dir, "TEMPLATE_eoxserver.conf")):
                sys.exit("Error: EOxServer config files not found.")
        
        os.chdir(dst_root_dir)
    
        # create the initial django folder structure
        print("Initializing django project folder.")
        django.core.management.call_command("startproject", instance_id)
    
        # create the `conf`, `data`, `logs` and `fixtures` subdirectories
        os.mkdir(dst_conf_dir)
        os.mkdir(dst_data_dir)
        os.mkdir(dst_logs_dir)
        os.mkdir(dst_static_dir)
        os.mkdir(dst_fixtures_dir)
        os.mkdir(dst_templates_dir)
        os.mkdir(dst_templates_admin_dir)

        # create the WCS-T subdirectories
        os.mkdir(os.path.join(dst_inst_dir, "wcst_perm"))
        os.mkdir(os.path.join(dst_inst_dir, "wcst_temp"))
    
        # create an empty logfile
        create_file(dst_logs_dir, "eoxserver.log")
        
        tags = {
            TAG_PATH_SRC: src_root_dir,
            TAG_PATH_DST: dst_inst_dir,
            TAG_INSTANCE_ID: instance_id
        }
    
        # copy the template settings file and replace its tags
        copy_and_replace_tags(os.path.join(src_conf_dir, "TEMPLATE_settings.py"),
                              os.path.join(dst_inst_dir, "settings.py"),
                              tags)
    
        # copy the template urls file
        shutil.copy(os.path.join(src_conf_dir, "TEMPLATE_urls.py"),
                    os.path.join(dst_inst_dir, "urls.py"))
        
        # copy the template config file and replace its tags
        copy_and_replace_tags(os.path.join(src_conf_dir, "TEMPLATE_eoxserver.conf"),
                              os.path.join(dst_conf_dir, "eoxserver.conf"),
                              tags)
        
        # copy the template base_site.html file
        shutil.copy(os.path.join(src_conf_dir, "TEMPLATE_base_site.html"),
                    os.path.join(dst_templates_admin_dir, "base_site.html"))
        
        shutil.copy(os.path.join(src_conf_dir, "TEMPLATE_template.map"),
                    os.path.join(dst_conf_dir, "template.map"))
        shutil.copy(os.path.join(src_conf_dir, "TEMPLATE_outline_template_dataset.html"),
                    os.path.join(dst_conf_dir, "outline_template_dataset.html"))
        shutil.copy(os.path.join(src_conf_dir, "TEMPLATE_outline_template_footer.html"),
                    os.path.join(dst_conf_dir, "outline_template_footer.html"))
        shutil.copy(os.path.join(src_conf_dir, "TEMPLATE_outline_template_header.html"),
                    os.path.join(dst_conf_dir, "outline_template_header.html"))
        
        shutil.copy(os.path.join(src_conf_dir, "init_spatialite-2.3.sql"),
                    os.path.join(dst_data_dir, "init_spatialite-2.3.sql"))
        
        if options.get('initial_data'):
            initial_data = os.path.abspath(options['initial_data'])
            if os.path.splitext(initial_data)[1].lower() != ".json":
                raise Exception("Initial data must be a JSON file.")
            shutil.copy(initial_data, os.path.join(dst_fixtures_dir,
                                                   "initial_data.json"))
        
        if options.get('init_spatialite'):
            # initialize the spatialite database file
            os.chdir(dst_data_dir)
            db_name = "config.sqlite"
            print("Setting up initial database.")
            try:
                from pyspatialite import dbapi2 as db
                conn = db.connect(db_name)
                rs = conn.execute('SELECT spatialite_version()')
                rs = rs.fetchone()[0].split(".")
                if (int(rs[0]), int(rs[1])) >= (2, 4):
                    print("SpatiaLite found, initializing using 'InitSpatialMetadata()'.")
                    conn.execute("SELECT InitSpatialMetadata()")
                else:
                    print("SpatiaLite version <2.4 found, trying to initialize using 'init_spatialite-2.3.sql'.")
                    init_sql_path = os.path.join(src_conf_dir, "init_spatialite-2.3.sql")
                    with open(init_sql_path, 'r') as init_sql_file:
                        conn.executescript(init_sql_file.read())
                conn.commit()
                conn.close()
            except ImportError:
                print("SpatiaLite not found, trying to initialize using 'init_spatialite-2.3.sql'.")
                init_sql_path = os.path.join(src_conf_dir, "init_spatialite-2.3.sql")
                os.system("spatialite %s < %s" % (db_name, init_sql_path))


def copy_and_replace_tags(src_pth, dst_pth, replacements={}):
    """Helper function to copy a file and replace tags within a file."""
    new_file = open(dst_pth,'w')
    old_file = open(src_pth)
    for line in old_file:
        for pattern, subst in replacements.iteritems():
            line = line.replace(pattern, subst)
        new_file.write(line)
    new_file.close()
    old_file.close()

def create_file(dir_or_path, filename=None):
    """Helper function to create a new empty file at a given location."""
    if filename is not None:
        dir_or_path = os.path.join(dir_or_path, filename)
    f = open(dir_or_path, 'w')
    f.close()
