#!/usr/bin/python
# coding: utf-8
"""
    Achtung: Falls die Abmaischtemperatur unter der letzten Rast liegt. Beendet das Programm sofort, da im mom nur erhitzen vorgesehen ist.
    Sollte der Fall auftreten, dass ich ein solches Rezept erhalte, werde ich diese funktionalaität implementieren.

    # Hopfen_Kochzeit
    Die Kochzeiten sind die Zeiten wie lange eine Hopfengabe mit der Würze gekocht wird, d.h. 0 min bedeutet Zugabe direkt am Kochende. 

    # Next Steps
    [ ] Log all temp events, you dont see anything when main control is sleeping and time watcher looks

    [X] Add Dev Mode (not real, with short times and temps) 
        Add Test Mode (real testing with shorter times and temps)
        Add Prod Mode (real cooking. change seconds to minutes, and do the realy stuff)

    Add Fallback -> shut down thread, turn off plate
    change control path setting. not a good way on two points...
    
    # The Future
    Add API Mode and microservices
"""

import os, sys, time
from pprint import pprint
from datetime import datetime, timedelta
import threading
import argparse
import logging

from lib.funcs import log, fail_exit, go_exit, get_config, get_recipe
from lib.recipe import check_mmum_recipe, print_recipe
from lib.console import confirm
from lib.temp import start_TempWatcher,stop_TempWatcher,wait_to_temp,getTemp



### BEGIN ARGUMENT PARSER ###

parser = argparse.ArgumentParser()
parser.add_argument('-c','--config',    help='set config file, overwrite config', default='config.yml')
parser.add_argument('-r','--recipe',    help='use this recipe file, overwrite config', default=None)
parser.add_argument('-v','--verbose',   help='print verbose messages', action='count')
parser.add_argument('-t','--tryrun',    help='try run for all components. starts a demo programm. No confirmation needed. recipe will be overwrite',action='count')
parser.add_argument('-d','--devmode',   help='run the programm withou real equipment',action='count')
parser.add_argument('-ck', '--check',   help='check all necessary things and exit',action='count')
args = parser.parse_args()

if args.verbose:
    log.setLevel(logging.DEBUG)

if args.tryrun and args.devmode:
    fail_exit("You can only run the try run without devmode. Connecting with your hardware")

config = get_config(args.config)

if not args.tryrun:
    if args.recipe:
        recipe = get_recipe(args.recipe)
    else:
        recipe = get_recipe(config['recipes']['file'])
else:
    recipe = get_recipe(config['recipes']['demo_recipe'])

log.info("Starting brewcontrol...")

# checks
log.debug("Check Temp Sensors")

if not args.devmode:
#if config['sys']['temp']:
    if not getTemp():
        fail_exit('no connection to temp sensor detected')
    if not os.path.isfile(f"{os.path.dirname(os.path.abspath(__file__))}/control/bin/433cmd_control-1"):        
        fail_exit('canot find plate control binary')

log.debug("Check recipe")
if config['recipes']['version'] == "mmum":
    recipe_cnt = check_mmum_recipe(recipe)
else:
    fail_exit("config version not supported (mmum)")   

if not recipe_cnt:
    fail_exit("invalid recipe, information missing")    

if args.check:
    go_exit("all checks done. you can start the brewing process")

log.info(print_recipe(recipe))
try:
    confirm("Brauvorgang starten? Y/n: ")
except KeyboardInterrupt:
    exit(1)


# Einmaischen
begin_brew = datetime.now()
thread=start_TempWatcher(recipe['Infusion_Einmaischtemperatur'], True if args.devmode else False)

try:
    wait_to_temp(thread)

    confirm("Einmaischenischen!... Fertig mit der Schüttung? <Y/n>: ")
    for rast in range(1,recipe_cnt['rast']+1):    
        # erhitze zur Rastzeit
        log.info(f"Erhitze bis Rast: {rast}")        
        thread.temp_to = float(recipe[f"Infusion_Rasttemperatur{rast}"])
        thread.temp_not_reached = True
        # wait to temp reached
        wait_to_temp(thread)               
        if not args.devmode:
            time.sleep(int(recipe[f"Infusion_Rastzeit{rast}"])*60) # in minutes
    
    #thread.temp_to = float(50.2)
    #thread.temp_to = float(recipe["Abmaischtemperatur"])
    #thread.temp_not_reached = True
    log.info(f"Warte auf Abmaischtemperatur: {recipe['Abmaischtemperatur']}")   
    thread.temp_to = float(recipe['Abmaischtemperatur'])
    thread.temp_not_reached = True     
    wait_to_temp(thread)
    log.info("Abmaischtemperatur erreicht.")
    
    stop_TempWatcher(thread)
    
    log.info(f"Nachguss: {recipe['Nachguss']} Liter")
    
    # Cooking
    confirm("Möchten Sie den Kochvorgang starten? Y/n: ")
    
    if recipe_cnt['hopfen_vwh']:
        log.info(f"Das Rezept enhält {recipe_cnt['hopfen_vwh']} Vorderwürzehopfen.")
        for vwh in range(1,recipe_cnt['hopfen_vwh']+1):
            print("\tSorte: "+recipe[f'Hopfen_VWH_{vwh}_Sorte'])
            print("\tMenge: "+recipe[f'Hopfen_VWH_{vwh}_Menge']+" g")
            print("\tAlpha: "+recipe[f'Hopfen_VWH_{vwh}_alpha'])
            print()
    confirm("Haben Sie den Hopfen hinzugefügt? Y/n: ")
  
    log.info("Erhitze bis zur Wallung der Würze. Eigenständig die Leistung herunter regeln:")

    # Was wenn die Kochzeit der Hopfengabe unterschiedlich ist?
    # Sortierung nach Kochzeit und Anzeige/Information zur Zugabe
    if recipe_cnt['hopfen']:
        print("Folgender Hopfen muss hinzugegeben werden")
        for hopfen in range(1,recipe_cnt['hopfen_vwh']+1):
                print("\tSorte: "+recipe[f'Hopfen_{hopfen}_Sorte'])
                print("\tMenge: "+recipe[f'Hopfen_{hopfen}_Menge']+" g")
                print("\tAlpha: "+recipe[f'Hopfen_{hopfen}_alpha'])
                print("\tKochzeit in der Würze:"+recipe[f'Hopfen_{hopfen}_Kochzeit']+" min") # Noch verbleibende Kochzeit 
        
    thread = start_TempWatcher(config['sys']['cooking-temp'], True if args.devmode else False)
    wait_to_temp(thread)
    log.info(f"Kochzeit der Würze beträgt: {recipe['Kochzeit_Wuerze']}")
    if args.devmode:
        time.sleep(2)
    else:
        time.sleep(int(recipe['Kochzeit_Wuerze'])*60) # in minutes
    
    # overwrite cooking time (maybe 90min)
    if config['recipes']['cooking-time-overwrite']:
        cto = int(config['recipes']['cooking-time-overwrite'])*60
        kw = int(recipe['Kochzeit_Wuerze'])*60
        if cto > kw:
            time.sleep((cto - kw))
    
    log.info("Kochzeit erreicht. Nun ist Hopfenseihen angesagt und runterkühlen")
    stop_TempWatcher(thread)
except KeyboardInterrupt:
    if thread:
        stop_TempWatcher(thread)
    