#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# version conventionnelle plus simple que la version parse-ansible-out.py

version = "parse-ansible-out2.py  zf191204.1417 "

"""
génération du fichier logs
./wpsible -vvv -l _srv_www_www.epfl.ch_htdocs_about 2>&1 |tee ansible.log

usage:
cd ./wp-ops/ansible
. parser/bin/activate
./parse-ansible-out2.py
"""


import datetime

def zget_time(zstring):
    p1 = zline.find(zstring) + len(zstring)
    p2 = zline.find(" ", p1)
    p3 = zline.find('"', p2)
    date_time_str = zline[p1:p3]
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
    date_time_obj_1970 = datetime.datetime.strptime("1970-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
    date_time_nano_sec = ((date_time_obj - date_time_obj_1970).total_seconds())*1000000000
    #print("%18.0f\n" % (date_time_nano_sec))
    return date_time_nano_sec

if (__name__ == "__main__"):
    print("\n" + version + "\n")
    zfile = open("ansible.log.191010", "r")
    i = 0
    time_start = 0
    while True:
        zline = zfile.readline()
        i = i + 1

        a = 'TASK '
        if zline.find(a) != -1 :
            #print(i, zline)
            ztask = zline[zline.find(": ")+2:zline.find("]")]
            num_line = i

        a = '"start": "'
        if zline.find(a) != -1 :
            #print(i, zline)
            time_start = zget_time(a)
            #print("%18.0f\n" % (time_start))

        a = '"end": "'
        if zline.find(a) != -1 :
            #print(i, zline)
            time_end = zget_time(a)
            #print("%18.0f\n" % (time_end))

        a = '}'
        if zline[0:1] == a :
            if time_start > 0 :
                #print(i, zline)
                #print(".......................end task...")
                time_delta = (time_end - time_start)/1000000000
                print(str(num_line) + " [" +ztask + "] start à " + "%0.0f" % (time_start) + ", durée: " + str(time_delta))
                time_start = 0

        if zline == "":
            break

    zfile.close()
