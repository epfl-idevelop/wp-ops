#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible (reclog) dans ce project
# version qui calcul la durée de chaque Task !
# sources: https://janakiev.com/blog/python-shell-commands/
# sources: https://github.com/zuzu59/reclog

import signal
import sys
import os
import datetime

version = "parse-ansible-out4.py  zf200915.1552 "

"""
ATTENTION: il ne faut pas oublier, avant de lancer la *petite fusée* d'effacer le fichier de log de reclog !
rm /Users/zuzu/dev-zf/reclog/file.log

génération du fichier logs:
Le faire avec la petite fusée du template dans l'interface WEB de AWX !

usage:
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_x_sites_y_forks_z_pods.txt

cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_10_sites_5_forks_1_pods.txt2
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_1033_sites_5_forks_1_pods.txt2
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_100_sites_5_forks_1_pods.txt2
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_100_sites_30_forks_1_pods.txt2
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_100_sites_50_forks_1_pods.txt2
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_100_sites_5_forks_10_pods.txt2

reset
./parse-ansible-out4.py awx_logs_10_sites_5_forks_1_pods.txt > toto.txt
./parse-ansible-out4.py awx_logs_1033_sites_5_forks_1_pods.txt > toto.txt

./parse-ansible-out4.py awx_logs_100_sites_5_forks_1_pods.txt > toto.txt
./parse-ansible-out4.py awx_logs_100_sites_30_forks_1_pods.txt > toto.txt
./parse-ansible-out4.py awx_logs_100_sites_50_forks_1_pods.txt > toto.txt
./parse-ansible-out4.py awx_logs_100_sites_5_forks_10_pods.txt > toto.txt


Puis voir le résultat dans un browser
http://noc-tst.idev-fsd.ml:9092/


Pour mettre à zéro la 'table' dans InfluxDB
export zinfluxdb_table="awx_logs1"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT $zinfluxdb_table"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
"""


# True False
zloop_parse = 40000000
zverbose_v = False
zverbose_vv = False
zverbose_dico = False
zverbose_curl = True
zverbose_grafana = True
zloop_curl = 10000000
zmake_curl = True
zsend_grafana = True

zinfluxdb_table = "awx_logs1"

db_logs = {}
ztask_id = 0
ztask_line = 0
ztask_name = ""
ztask_pod = ""
ztask_path = ""
ztask_site_name = ""
ztask_site_id = 0
ztask_time = ""
ztask_duration = 0

ztask_time_1 = ""
ztask_time_obj_1 = ""
ztask_unix_time_1 = 0

ztask_time_2 = ""
ztask_time_obj_2 = ""
ztask_unix_time_2 = 0

# ALT+CMD+F bascule du code au terminal

# Structure du dictionnaire
# index: 1
#     task_name: toto1
#     task_path: tutu1
#     index: 1
#         site_name: tata1
#         time_start: 123
#         time_end: 234
#         time_duree: 12
#     index: 2
#         site_name: tata2
#         time_start: 345
#         time_end: 456
#         time_duree: 23
# index: 2
#     task_name: toto2
#     task_path: tutu2
#     index: 1
#         site_name: tata1
#         time_start: 123
#         time_end: 234
#         time_duree: 12
#     index: 2
#         site_name: tata2
#         time_start: 345
#         time_end: 456


def zprint_db_log():
    for i in range(1, len(db_logs)+1): 
        print("\n++++++++++++++++")
        print("ztask_name: " + str(i) + ", " + db_logs[i]["ztask_name"])
        print("ztask_path: " + db_logs[i]["ztask_path"])
        for j in range(1, (len(db_logs[i]) - 2) + 1):
            print("----")
            
            
            print("ztask_name: " + str(i) + ", " + db_logs[i]["ztask_name"])
            print("ztask_path: " + db_logs[i]["ztask_path"])


            print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])
            print("ztask_pod: " + db_logs[i][j]["ztask_pod"])
            try:
                print("ztask_time_start: " + db_logs[i][j]["ztask_time_start"])
            except:
                print("************************************************************************oups y'a pas de ztask_time_start")

            try:
                print("ztask_line_start: " + str(db_logs[i][j]["ztask_line_start"]))
            except:
                print("************************************************************************oups y'a pas de ztask_line_start")

            try:
                print("ztask_time_end: " + db_logs[i][j]["ztask_time_end"])
            except:
                print("************************************************************************oups y'a pas de ztask_time_end")

            try:
                print("ztask_line_end: " + str(db_logs[i][j]["ztask_line_end"]))
            except:
                print("************************************************************************oups y'a pas de ztask_line_end")

            try:
                print("ztask_duration: " + str(db_logs[i][j]["ztask_duration"]))
            except:
                pass
                # print("************************************************************************oups y'a pas de ztask_line_end")

            
        

def signal_handler(signal, frame):
    print("oups il y a eu un CTRL-C !")
    quit()
    # sys.exit(0)
  
def zget_unix_time(zdate):
    #    date_time_obj = datetime.datetime.strptime(zdate, '%Y-%m-%d %H:%M:%S.%f')
    zdate_time_obj = zdate
    if zverbose_vv: print("zdate_time_obj: [" + str(zdate_time_obj) + "]")
    zdate_time_1970_obj = datetime.datetime.strptime(
        "1970-01-01 02:00:00", '%Y-%m-%d %H:%M:%S')  # Astuce pour faire UTC-2 à cause de Grafana !
    if zverbose_vv: print("zdate_time_1970_obj: [" + str(zdate_time_1970_obj) + "]")
    zdate_time_unix_obj = (zdate_time_obj - zdate_time_1970_obj)
    if zverbose_vv: print("zdate_time_unix_obj: [" + str(zdate_time_unix_obj) + "]")
    return zdate_time_unix_obj


if (__name__ == "__main__"):
    print("\n" + version + "\n")

    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) == 1:
        print("Usage: ./parse-ansible-out4.py fichier_log_a_parser\n\n")
        sys.exit()

    zfile = open(sys.argv[1], "r")
    i = 1

    # on parse le fichier de logs
    while True:
        zline = zfile.readline()
        # est-ce la fin du fichier de logs ?
        if zline == "":
            break

        if zverbose_vv: print("nouvelle ligne: " + str(i) + " " + zline[:-1])

        # est-ce une ligne de Task ?
        if zline.find(', TASK:') != -1:            
            if zverbose_vv: print("coucou c'est une task")
            
            # récupération du task_site
            zstr_find1 = ' by zuzu, '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ': PATH: '            
            p2 = zline.find(zstr_find2, p1)
            ztask_site_name = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_site_name: [" + ztask_site_name + "]")

            # récupération du task_pod
            zstr_find1 = 'PATH: /tmp/awx_'
            p1 = zline.find(zstr_find1)
            zstr_find2 = '_'            
            p2 = zline.find(zstr_find2, p1 + len(zstr_find1))
            ztask_pod = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_pod: [" + ztask_pod + "]")

            # récupération du task_path
            zstr_find1 = 'project/ansible/'
            p1 = zline.find(zstr_find1)
            zstr_find2 = ', TASK: '            
            p2 = zline.find(zstr_find2, p1)
            ztask_path = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_path: [" + ztask_path + "]")

            # récupération du task_name
            zstr_find1 = ' : '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ' at 2020'            
            p2 = zline.find(zstr_find2, p1)
            ztask_name = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_name: [" + ztask_name + "]")
            
            # récupération du ztask_time start ou end
            zstr_find1 = ' at '
            p1 = zline.find(zstr_find1)
            # zstr_find2 = ''            
            # p2 = zline.find(zstr_find2, p1)
            p2 = -1
            ztask_time = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_time: [" + ztask_time + "]")
            
            
            
            # est-ce un start ?
            if zline.find('log start') != -1:
                if zverbose_vv: print("c'est un start")
                    
                # on cherche où se trouve la tâche dans le dictionnaire
                ztask_id = 0
                if zverbose_vv: print("on cherche où se trouve la tâche dans le dictionnaire 114819")
                if zverbose_vv: print("ztask_id_len 114441: " + str(len(db_logs)))
                for j in range(1, len(db_logs)+1):
                    if zverbose_vv: print("j: " + str(j))
                    if db_logs[j]["ztask_path"] == ztask_path and db_logs[j]["ztask_name"] == ztask_name:
                        ztask_id = j
                        if zverbose_vv: print("ztask_id 114543:" + str(ztask_id))
                        break

                if zverbose_vv: print("ztask_id 102011: " + str(ztask_id))

                # avons-nous trouvé la tâche dans le dictionnaire ?
                if ztask_id == 0:
                    # La tâche n'existe pas encore, on la crée
                    if zverbose_vv: print("la tâche n'existe pas encore, on la crée")
                    ztask_id = len(db_logs) + 1
                    if zverbose_vv: print("ztask_id 1739: " + str(ztask_id))
                    db_logs[ztask_id] = {}
                    db_logs[ztask_id]["ztask_name"] = ztask_name
                    db_logs[ztask_id]["ztask_path"] = ztask_path
                                
                # on calcul l'index du site dans le dictionnaire
                ztask_site_id = (len(db_logs[ztask_id]) - 2) + 1
                
                if zverbose_vv: print("ztask_id 180818: " + str(ztask_id))
                if zverbose_vv: print("ztask_site_id_len 111632: " + str((len(db_logs[ztask_id]) - 2)))
                if zverbose_vv: print("ztask_site_id 180818: " + str(ztask_site_id))

                # on crée un nouveau site et écrit le task_time_start
                if zverbose_vv: print("On crée un nouveau site et écrit le task_time_start")
                if zverbose_vv: print("ztask_site_name:" + str(ztask_site_name))
                db_logs[ztask_id][ztask_site_id] = {}
                db_logs[ztask_id][ztask_site_id]["ztask_site_name"] = ztask_site_name
                db_logs[ztask_id][ztask_site_id]["ztask_pod"] = ztask_pod                
                db_logs[ztask_id][ztask_site_id]["ztask_time_start"] = ztask_time
                db_logs[ztask_id][ztask_site_id]["ztask_line_start"] = i
                if zverbose_vv: print("ztask_site_id_len 112027: " + str((len(db_logs[ztask_id]) - 2)))
                if zverbose_vv: print("On a terminé de créer un nouveau site et d'écrire le task_time_start")


                
            # est-ce un end ?
            if zline.find('log end') != -1:                
                if zverbose_vv: print("c'est un end")

                # on cherche où se trouve la tâche dans le dictionnaire
                ztask_id = 0
                if zverbose_vv: print("on cherche où se trouve la tâche dans le dictionnaire 114844")                
                if zverbose_vv: print("ztask_id_len 114225: " + str(len(db_logs)))
                for j in range(1, len(db_logs) + 1):
                    if zverbose_vv: print("j 115336: " + str(j))
                    if db_logs[j]["ztask_path"] == ztask_path and db_logs[j]["ztask_name"] == ztask_name:
                        ztask_id = j
                        if zverbose_vv: print("ztask_id 093236:" + str(ztask_id))
                        break         
                                   
                if zverbose_vv: print("ztask_id 114634: " + str(ztask_id))
                    
                # avons-nous trouvé la tâche dans le dictionnaire ?
                if ztask_id == 0:
                    print("oups, y'a pas de tâche ici 133759")
                    print("et on doit s'arrêter !")
                    exit()
                
                # chercher l'index du site dans le dictionnaire
                ztask_site_id = 0
                for j in range(1, (len(db_logs[ztask_id]) - 2) + 1):
                    if zverbose_vv: print("j 093501: " + str(j))
                    if zverbose_vv: print("ztask_site_name 1 093547: " + str(db_logs[ztask_id][j]["ztask_site_name"]))
                    if zverbose_vv: print("ztask_site_name 2 093547: " + str(ztask_site_name))
                    if db_logs[ztask_id][j]["ztask_site_name"] == ztask_site_name:
                        ztask_site_id = j
                        if zverbose_vv: print("ztask_site_id 1133:" + str(ztask_site_id))
                        break

                # est-ce qu'il y a un site ?
                if ztask_site_id == 0:
                    print("oups, y'a pas de site ici 133935: " + str(i))
                    # break
                    # raw_input('Enter your input:')
                    # print("on s'arrête pour savoir pourquoi il n'y a pas de site ?")
                    # # print(db_logs)
                    # # zprint_db_log()
                    # print("boum on s'est arrêté ! 142745")
                    # exit()
                    
                    # on calcul l'index du site dans le dictionnaire
                    ztask_site_id = (len(db_logs[ztask_id]) - 2) + 1
                    if zverbose_vv: print("ztask_site_id 1346:" + str(ztask_site_id))

                    # on crée un nouveau site
                    db_logs[ztask_id][ztask_site_id] = {}
                    db_logs[ztask_id][ztask_site_id]["ztask_site_name"] = ztask_site_name
                    db_logs[ztask_id][ztask_site_id]["ztask_pod"] = ztask_pod                
                
                # on écrit le task_time_end
                db_logs[ztask_id][ztask_site_id]["ztask_time_end"] = ztask_time
                db_logs[ztask_id][ztask_site_id]["ztask_line_end"] = i

                
            
            

        if zverbose_vv: print("next: " + str(i))
        i = i + 1
        # on évite la boucle infinie ;-)
        if i > zloop_parse:
            break

    zfile.close()

    print("\n\non a terminé de parser les logs 161447\n\n")
    #print(db_logs)
    if zverbose_dico: zprint_db_log()
    # quit()
    
    
    # on calcul les durations pour chaque sites
    for i in range(1, len(db_logs)+1): 
        if zverbose_vv: print("i: " + str(i))
        for j in range(1, (len(db_logs[i]) - 2) + 1):
            if zverbose_vv: print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])
            try:
                ztask_time_1 = db_logs[i][j]["ztask_time_start"][0:-6]
                if zverbose_vv: print("ztask_time_1: " + str(ztask_time_1))
                ztask_time_obj_1 = datetime.datetime.strptime(ztask_time_1, '%Y-%m-%d %H:%M:%S.%f')
                ztask_unix_time_1 = zget_unix_time(ztask_time_obj_1).total_seconds()
                if zverbose_vv: print("ztask_unix_time_1: " + str(ztask_unix_time_1))
                try:
                    ztask_time_2 = db_logs[i][j]["ztask_time_end"][0:-6]
                    if zverbose_vv: print("ztask_time_2: " + str(ztask_time_2))
                    ztask_time_obj_2 = datetime.datetime.strptime(ztask_time_2, '%Y-%m-%d %H:%M:%S.%f')
                    ztask_unix_time_2 = zget_unix_time(ztask_time_obj_2).total_seconds()
                    if zverbose_vv: print("ztask_unix_time_2: " + str(ztask_unix_time_2))
                    ztask_duration = ztask_unix_time_2 - ztask_unix_time_1
                    if zverbose_vv: print("Durée: " + str(ztask_duration))
                    db_logs[i][j]["ztask_duration"] = ztask_duration
                    if zverbose_v: print(".................................................. 110232")                        
                    if zverbose_v: print("Task number: " + str(i))
                    if zverbose_v: print("ztask_name: " + str(i) + ", " + db_logs[i]["ztask_name"])
                    if zverbose_v: print("ztask_path: " + db_logs[i]["ztask_path"])
                    if zverbose_v: print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])
                    if zverbose_v: print("ztask_time_start: " + db_logs[i][j]["ztask_time_start"])
                    if zverbose_v: print("ztask_line_start: " + str(db_logs[i][j]["ztask_line_start"]))
                    if zverbose_v: print("ztask_time_end: " + db_logs[i][j]["ztask_time_end"])
                    if zverbose_v: print("ztask_line_end: " + str(db_logs[i][j]["ztask_line_end"]))
                    if zverbose_v: print("ztask_duration: " + str(db_logs[i][j]["ztask_duration"]))
                    if zverbose_v: print("..................................................")                    
                except:
                    print("oups, c'est pas bon ici 121330")
            except:
                print("oups, c'est pas bon ici 121313")


    print("\n\non a terminé de calculer les durations 141249\n\n")
    #print(db_logs)
    if zverbose_dico: zprint_db_log()
    # quit()

            
            
    # on envoie les données à la db influxdb/grafana    
    if zmake_curl:
        for i in range(1, len(db_logs)+1): 
            if zverbose_vv: print("ztask_path_id 121552: " + str(i) + db_logs[i]["ztask_path"])
            for j in range(1, (len(db_logs[i]) - 2) + 1):
                if zverbose_vv: print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])

                try:
                    ztask_name_1 = db_logs[i]["ztask_name"]
                    ztask_path_1 = db_logs[i]["ztask_path"]
                    ztask_line_1 = db_logs[i][j]["ztask_line_start"]
                    ztask_site_name_1 = db_logs[i][j]["ztask_site_name"]
                                    
                    # on change tous les caractères *system* utilisés par InfluxDB
                    # ztask_name = ztask_name_1.replace(" ", "_") + "_" + str(ztask_line_1)
                    ztask_name = ztask_name_1.replace(" ", "_")
                    ztask_name = ztask_name_1.replace(" ", "_")
                    ztask_path = ztask_path_1.replace(" ", "_")
                    ztask_path = ztask_path.replace(":", "_")
                    ztask_path = ztask_path.replace(".", "_")
                    ztask_site_name = ztask_site_name_1
                    
                    # on transforme en nano secondes pour InfluxDB
                    ztask_time_1 = db_logs[i][j]["ztask_time_start"][0:-6]
                    if zverbose_v: print("ztask_time_1: " + ztask_time_1)

                    ztask_time_obj_1 = datetime.datetime.strptime(ztask_time_1, '%Y-%m-%d %H:%M:%S.%f')
                    ztask_unix_time_1 = zget_unix_time(ztask_time_obj_1).total_seconds()
                    ztask_unix_time_nano = ztask_unix_time_1 * 1000000000

                    try:
                        ztask_duration = db_logs[i][j]["ztask_duration"]
                        zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + zinfluxdb_table
                        zcmd = zcmd + ',task=' + ztask_name + '_/_' + ztask_path + ',site=' + ztask_site_name + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
                        
                        if zverbose_curl: print(zcmd)
                        
                        if zsend_grafana:
                            zerr = os.system(zcmd)
                            if zerr != 0:
                                if zverbose_grafana(): print(zerr)
                    except:
                        print("oups, y'a pas de duration ici 144852")
                except:
                    print("oups, y'a pas de start ici 154446")
                    
                


            # on évite la boucle infinie ;-)
            if zverbose_v: print("toto:" + str(i))
            if i > zloop_curl:
                break
                

