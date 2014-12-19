#!/usr/bin/python
#// Copyright (C) 2009  Roberto Jacinto
#// roberto.jacinto@caixamagica.com
#//
#// This program is free software; you can redistribute it and/or
#// modify it under the terms of the GNU General Public License
#// as published by the Free Software Foundation; either version 2
#// of the License, or (at your option) any later version.
#//
#// This program is distributed in the hope that it will be useful,
#// but WITHOUT ANY WARRANTY; without even the implied warranty of
#// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#// GNU General Public License for more details.
#//
#// You should have received a copy of the GNU General Public License
#// along with this program; if not, write to the Free Software
#// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#/***************************************/
#/*
# * Directory where apk's are stored
# * Configuration changes go here! 
# */

from xml.dom import minidom

import os
import subprocess

DIR = ".";
ICON_DIR_OUT = "icons/";

#/****************************************/
ICON_DIR = DIR + "/" + ICON_DIR_OUT;
xml_path = DIR + "/info.xml";

def get_icon(file_, icon, apk):
    
    subprocess.call('unzip ' + file_ + ' -d .tmp > /dev/null', shell=True);
    subprocess.call('mv ./.tmp/' + icon + ' ' + ICON_DIR + apk, shell=True);
    subprocess.call('rm -rf ./.tmp', shell=True);
    return ICON_DIR_OUT + apk

def execute(command):
    dump = ""
    if "check_output" not in dir( subprocess ):
        import commands
        dump = commands.getstatusoutput(command)[1]
    else:
        dump = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True);
    return dump

def get_info(file_):

    infos = []
    infos.append(["name","./aapt d badging " + file_ + "|grep application-label| cut -d\\\' -f2"])
    infos.append(["icon","./aapt d badging " + file_ + "|grep application-icon-480| cut -d\\\' -f2" ])
    infos.append(["pkg","./aapt d badging " + file_ + "|grep package| cut -d\\\' -f2"])
    infos.append(["ver","./aapt d badging " + file_ + "|grep package| cut -d\\\' -f6"])
    infos.append(["vercode","./aapt d badging " +  file_ + "|grep package| cut -d\\\' -f4"])
    infos.append(["date","stat " + file_ + "|grep Change| cut -d' ' -f2,3"])

    send = {};
    for key,command in infos:
        out = ""
        try:
            out = execute(command)
        except:
            print "Error executing %s " % command
        send[key] = out.rstrip('\n\r ')
    return send

### CLEAN
subprocess.call('rm ' + DIR + '/*.xml', shell=True)
subprocess.call('rm -rf ' + ICON_DIR, shell=True)
subprocess.call('mkdir ' + ICON_DIR, shell=True)
dump = execute('find ' + DIR + " -name '*.apk'");

impl = minidom.getDOMImplementation()
dom = impl.createDocument(None, 'apklst', None)
root = dom.documentElement

for apk in dump.split("\n"):
    if apk == "":
        continue

    print "\nAPK: %s" % apk;

    apkName,end = os.path.splitext(apk)

    if end == ".apk":

        rtrn = get_info(apk);
        print rtrn
        if rtrn["icon"] == "":
            icon = "";
        else:
            icon = get_icon(DIR + '/' + apk, rtrn["icon"], rtrn["pkg"])

        print "\nPackage (hasID): %s" % rtrn["pkg"];
        print "\nVersion: %s" % rtrn["ver"];
        print  "\nVersion Code: %s" % rtrn["vercode"];
        print  "\nName: %s" % rtrn["name"];
        print  "\nIcon: %s" % rtrn["icon"];
        print  "\nIcon(L): %s" % icon;
        print  "\nDate: %s" % rtrn["date"];
        print  "\n ======================== \n";
        
        occ = dom.createElement('package');
        occ = root.appendChild(occ);

        for tag,text in [['name',rtrn['name']],['path',apk],['ver',rtrn['ver']],['vercode',rtrn['vercode']],['apkid',rtrn['pkg']],['icon',icon],['date',rtrn['date']]]:

            child = dom.createElement(tag);
            child = occ.appendChild(child);
            value = dom.createTextNode(text);
            value = child.appendChild(value);

xml_string = dom.toxml();
with open(xml_path, 'w') as file_:
    file_.write(xml_string)
print "\nXML FILE SUCCESSFULLY CREATED!\n" + xml_path

