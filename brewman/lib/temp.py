import threading
import time
import os

from lib.funcs import fail_exit



class TempWatcher(threading.Thread):
    """no time handling here"""
    def __init__(self,temp_to):
        threading.Thread.__init__(self)
        self.temp_to = temp_to
        self.plate = 0
        self.temp = 50.3
        self.signal = True
        self.temp_not_reached = True
        self.dev_mode = False
        self.control_path = "control/bin/433cmd_control-1"
    
    def run(self):
        while self.signal:
            #print(self.signal)
            if not self.dev_mode:            
                self.temp = getTemp()
            else:            
                if self.plate == 0 and self.temp >= self.temp_to:                
                    self.dev_decrease_temp()
                elif self.plate == 1 and self.temp <= self.temp_to:
                    self.dev_increase_temp()
            
            #print(f"{self.temp} >= {self.temp_to}")	
            if self.temp >= self.temp_to:
                if self.plate == 1:
                    if not self.dev_mode:
                        cmd = f"{self.control_path} 0"
                        if os.system(cmd) > 0:
                            print("Error on exec plate 0")
                        else:
                            self.plate = 0
                            self.temp_not_reached=False
                    else:
                        self.plate = 0                    
                        self.temp_not_reached=False
            elif not self.plate:
                if not self.dev_mode:
                    cmd = f"{self.control_path} 1"
                    if os.system(cmd) > 0:
                        print("Error on exec plate 1")
                    else:
                        self.plate = 1
                        self.temp_not_reached=True
                else:                    
                    self.plate = 1
            self.time_run = time.time()
            time.sleep(1)
        
        # end of this time watcher. turn plate off
        if not self.dev_mode:
            cmd =   f"{self.control_path} 0"
            if os.system(cmd) > 0:
                print("Error on exec plate 1")
            else:
                self.plate = 0
        else:
            self.plate = 0
        
    def dev_increase_temp(self):
        self.temp += 3

    def dev_decrease_temp(self):
        self.temp -= 3

def getTemp():
    sensor= '/sys/bus/w1/devices/28-0516d0809fff/w1_slave'
    try:
        with open(sensor) as file:
            # write a func to auto detect this devices
            #    file = open('/sys/bus/w1/devices/28-0316c2d82cff/w1_slave')
            #    file = open('/sys/bus/w1/devices/28-0416c5040bff/w1_slave')
            #    file = open('/sys/bus/w1/devices/28-0316c2d550ff//w1_slave')
            #    file = open('/sys/bus/w1/devices/28-0416c4dec6ff/w1_slave')
            cont = file.read()
    except FileNotFoundError:
        fail_exit(f"Canot access tempsensor: {sensor}")

   #convert
    v = cont.split("\n")[1].split(" ")[9]
    temp = float(v[2:]) / 1000
    return(temp)

def start_TempWatcher(temp_to,dev_mode = False):
    thread = TempWatcher(temp_to)
    thread.dev_mode = dev_mode
    thread.start() 
    return thread

def stop_TempWatcher(thread):
        thread.signal = False
        thread.join()

def wait_to_temp(thread):
    while thread.temp_not_reached:    
        print(f"Temp: {thread.temp} --> {thread.temp_to}")
        time.sleep(1)