import logging
import yaml
import json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def setup_log():    
    log = logging.getLogger('brew')
    log.setLevel(logging.INFO)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(message)s',"%H:%M:%S")
    console_log.setFormatter(formatter)
    log.addHandler(console_log)

    logfile = logging.FileHandler('log/out.log')
    logfile.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logfile.setFormatter(formatter)
    log.addHandler(logfile)

    logging.addLevelName( logging.DEBUG, f"{bcolors.OKBLUE}[#]{bcolors.ENDC}")
    logging.addLevelName( logging.INFO, f"{bcolors.OKGREEN}[+]{bcolors.ENDC}")
    logging.addLevelName( logging.WARNING, f"{bcolors.WARNING}[?]{bcolors.ENDC}")
    logging.addLevelName( logging.ERROR, f"{bcolors.FAIL}[!]{bcolors.ENDC}")

    return log

log = setup_log()

def fail_exit(msg):
    log.error({msg})
    exit(1)

def go_exit(msg):
    log.info(msg)
    exit(0)

def get_config(confile):
    config = None
    try:
        with open(confile,'r') as fp:
            config = yaml.load(fp)
    except EnvironmentError:
        fail_exit(f"Canot load config file: {confile}")

    return config    

def get_recipe(refile):
    # Load Recept
    recipe = None
    try:
        with open(refile) as rfp:	
            recipe = json.load(rfp)
    except EnvironmentError:
        fail_exit(f"Canot load recipe file: {refile}")

    return recipe