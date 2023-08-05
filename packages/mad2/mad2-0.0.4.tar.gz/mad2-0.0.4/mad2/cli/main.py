# -*- coding: utf-8 -*-
from __future__ import print_function,  unicode_literals
import logging
import os
import sys
import subprocess
import tempfile

import leip
import Yaco

import mad2.ui
from mad2.util import  get_mad_file, get_all_mad_files

lg = logging.getLogger(__name__)

def dispatch():
    """
    Run the app - this is the actual entry point
    """
    app.run()

##
## define Mad commands
##

@leip.arg('-f', '--force', action='store_true', help='apply force')
@leip.arg('file', nargs='*')
@leip.command
def checksum(app, args):
    """
    Calculate a checksum
    """
    for madfile in get_all_mad_files(app, args):
        if not args.force and 'checksum' in madfile.mad:
            #exists - and not forcing
            lg.warning("Skipping checksum - exists")
            continue
        madfile.checksum()
        madfile.save()


@leip.arg('file', nargs='?')
@leip.arg('key', help='key to set')
@leip.command
def edit(app, args):
    """
    Edit a key in a full screen editor
    """
    key = args.key
    editor = os.environ.get('EDITOR','vim')

    if args.file:
        madfile = get_mad_file(app, args.file)
        default = madfile.mad.get(key, "")
    else:
        #if no file is defined, use the configuration
        default = app.conf.get(key, "")

    #write default value to a temp file, and start the editor
    tmp_file = tempfile.NamedTemporaryFile('wb', delete=False)
    if default:
        tmp_file.write(default)
    tmp_file.close()
    subprocess.call([editor, tmp_file.name])

    #read tmp file
    with open(tmp_file.name, 'r') as F:
        #removing trailing space
        val = F.read().rstrip()

    if args.file:
        madfile.mad[key] = val
        madfile.save()
    else:
        app.conf[key] = val
        app.conf.save()

    os.unlink(tmp_file.name)

@leip.arg('-f', '--force', action='store_true', help='apply force')
@leip.arg('file', nargs='*')
@leip.arg('value', help='value to set')
@leip.arg('key', help='key to set')
@leip.command
def set(app, args):

    key = args.key
    val = args.value

    madfiles = list(get_all_mad_files(app, args))
    
    if val == '-':
        if len(madfiles) == 1:
            data = madfiles[0].data(app.conf)
            default = madfiles[0].mad.get(key, "")
        else:
            data = app.conf.simple()

        val = mad2.ui.askUser(key, default, data)

    if len(madfiles) == 0:
        #apply conf to the local user config if no madfiles are defined
        app.conf[key] = val
        app.conf.save()
        return 

    for madfile in madfiles:
        list_mode = False
        if key[0] == '+':
            list_mode = True
            key = key[1:]
            
        keywords = app.conf.keywords
        if not args.force and not key in keywords:
            print("invalid key: {0}".format(key))

        keyinfo = keywords[key]
        keytype = keyinfo.get('type', 'str')
        
        if list_mode and keyinfo.cardinality == '1':
            print("Cardinality == 1 - no lists!")
            sys.exit(-1)

        if keytype == 'restricted' and \
                not val in keyinfo.allowed:
            print("Value '{0}' not allowed".format(val))
            sys.exit(-1)
                    
        if list_mode:
            if not key in madfile.mad:
                oldval = []
            else:
                oldval = madfile.mad[key]
                if not isinstance(oldval, list):
                    oldval = [oldval]
            madfile.mad[key] = oldval + [val]
        else:
            #not listmode
            madfile.mad[key] = val        
        madfile.save()


##
## define show
##
@leip.arg('-a', '--all', action='store_true')
@leip.arg('file', nargs='*')
@leip.command
def show(app, args):
    lg.debug("processing file: %s" % args.file)
    if args.file or args.all:
        data = Yaco.Yaco()
        if args.file:   
            madfile = get_mad_file(app, args.file)
            data.update(madfile.otf)
            data.update(madfile.mad)
        data.update(app.conf)
        print(data.pretty().decode())
    else:
        print(madfile.pretty().decode())
        
##
## define show
##
@leip.arg('file', nargs="+")
@leip.arg('key')
@leip.command
def unset(app, args):
    lg.debug("unsetting: %s".format(args.key))
    for madfile in get_all_mad_files(app, args):
        if args.key in madfile.mad:
            del(madfile.mad[args.key])
        madfile.save()

##        
## define find
##
@leip.arg('dir', default='.', help='directory to search from')
@leip.command
def find(app, args):
    lg.info("searching dir %s" % args.dir)


## 
## Instantiate the app and discover hooks & commands
##

import pkg_resources
base_config = pkg_resources.resource_string('mad2', 'etc/mad.config')

#trail of config files???
config_files = [
    ('system', '/etc/mad.config'),
    ('user', '~/.config/mad/mad.config')]

path = os.getcwd()
config_no = 0
xtra_config = []
while path:
    config_no += 1
    xtra_config.append(('dd{0}'.format(config_no), os.path.join(path, '.mad')))
    path = path.rsplit(os.sep, 1)[0]

config_files.extend(list(reversed(xtra_config)))
app = leip.app(name='mad', set_name=None, base_config = base_config,
               config_files = config_files)

#discover hooks in this module!
app.discover(globals())
