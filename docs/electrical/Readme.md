# Raspberry Pi Electronics

## GPIO pin layout

You can find a layout fo all pins [here](https://pinout.xyz)

## Temperaturfühler - DS18B20

| Bezeichnung    | Infos |
| -------------  | -----|
| 1-Wire DS18B20 | [Onewire](http://www.netzmafia.de/skripten/hardware/RasPi/Projekt-Onewire/index.html) |

Drei Leitungen Masse, 3,3 V und eine Signalleitung
Anschluss mit dem Rasperry

| Pin            | Farbe | Info |
| -------------  |  -----| -----|
| 3,3 V (Pin 1)  | Schwarz | GRND |
| Ground (Pin 6) | Rot | + |
| GPIO 4 (Pin 7) | Gelb | Daten |

Zwischen die 3,3-V-Leitung und die Datenleitung wird ein 4,7-Kiloohm-Widerstand geschaltet.
Siehe Bilder (Raspberry-pi-pinout.jpg).

### Rasperry Konfiguration

```bash
modprobe w1_gpio w1_therm

#/boot/config.txt einfügen, sofern nicht vorhanden
dtoverlay=w1-gpio,gpiopin=4
```

Unter /sys/bus/w1/devices/ sollte nachdem alles angeschlossen wurde undd die kernel module geladen sind eine ID erscheinen neben dem w1_bus_master1

```bash
# Temperatur auslesen:
cat /sys/bus/w1/devices/28-0416c4dec6ff/w1_slave
74 01 4b 46 7f ff 0c 10 55 : crc=55 YES
74 01 4b 46 7f ff 0c 10 55 t=23250
```

Anschließend ein python Programm was das erledigt und aufbereitet.

```python
#!/usr/bin/python
# coding=utf-8

import os, sys, time

# ID Liste
# 28-0516d0809fff
# 28-0316c2d82cff
# 28-0416c5040bff
# 28-0316c2d550ff
# 28-0416c4dec6ff

def getTemp():
    file = open('/sys/bus/w1/devices/28-0516d0809fff/w1_slave')
    cont = file.read()
    file.close()

   #convert
    v = cont.split("\n")[1].split(" ")[9]
    temp = float(v[2:]) / 1000

    return('%6.2f'%temp)

for i in range(0,20):
    print(getTemp())
    time.sleep(5)
```

## Funksteckdosen/Funk- Sende und Empfänger Modul

| Bezeichnung    | Infos |
| -------------  | -----|
| Aukru 433 MHz  |Funk- Sende und Empfänger Modul|
| ITLR 3500 Intertechno | Funksteckdosen |

### Infomaterial

- [tutorial](https://tutorials-raspberrypi.de/raspberry-pi-funksteckdosen-433-mhz-steuern/)
- [wiringpi](https://tutorials-raspberrypi.de/wiringpi-installieren-pinbelegung/)
- [fem wiki](https://wiki.fhem.de/wiki/Intertechno_Code_Berechnung#Selbstlernende_Intertechno_Funksteckdosen_.28z.B._ITR-1500.29)

### Hardware

Dies ist das 5V Modul. Beide werden mit 5V betrieben. Obwohl der Empfänger auch mit V3 funktioniert.

| Pin    | Spannung | Info |
| -------|  -----| -----|
| 17 | 3.3V | + |
| 14 | | GRND |
| 11 | | Daten BCM 17 |
| 13 | 3.3V | Daten BCM 27 |

Siehe Bild (raspberry-pi-funksteckdosen.png)

### Software

```bash
mkdir src; cd src
git clone git://git.drogon.net/wiringPi && cd wiringPi &&./build
git clone --recursive https://github.com/ninjablocks/433Utils.git && cd 433Utils/RPi_utils && make all
```

### Testen

```bash
cd 433Utils/RPi_utils
sudo ./RFSniffer
sudo ./codesend 1234

# compiling with right set of ON and OFF bits

g++ -DRPI   -c -o ../rc-switch/RCSwitch.o ../rc-switch/RCSwitch.cpp
g++ -DRPI   -c -o 433cmd_control-2.o 433cmd_control-2.cpp
g++ -DRPI  ../rc-switch/RCSwitch.o 433cmd_control-2.o -o 433cmd_control-2 -lwiringPi
```

### Funksteckdosen anlernen

Neues Protokoll

```none
32-Bit Wort.
    ID-Code aus 26 Bits, 2-Bit Kommando und eine 4-Bit Geräte bzw. Tastenpaar Nummer
    [26-Bit ID des steuernden Geräts (Fernbedienung)][2-Bit Kommando][4-Bit Kanal-ID (Tastenpaar)]

    Befehl  Bedeutung
    0 0     Ein Gerät einschalten
    0 1     Ein Gerät ausschalten
    1 0     Alle Geräte (dieser Gruppe) einschalten
    1 1     Alle Geräte (dieser Gruppe) ausschalten
```

Einschaltbefehl: 01010010101011101000000110 01 0011

```c
#define INTERTECH_ON  "00000000000101010001010101010100"
#define INTERTECH_OFF "00000000000101010001010001010100"

# Für Steuerung 1
#define INTERTECH_ON  "00000000000101010001010101000001"
#define INTERTECH_OFF "00000000000101010001010001010100"

# Original from Net
#define INTERTECH_ON  "00000000000101010001010101010100"
#define INTERTECH_OFF "00000000000101010001010001010100"

--------------------- to del behind -----

##########################--////
00000000000101010001010101000001 EIN
00000000000101010001010101010001 AUS

int('00000000000101010001010101010100',2)
"{0:b}".format(1381716)
```

Mit folgenden Befehlen können die Codes gesendet werden:

```bash
#ON
./codesend 1115473
#OFF
./codesend 1115476
```

Hier noch ein Link zum selbst lernenden [Protokoll](http://elektronikforumet.com/wiki/index.php/RF_Protokoll_-_Proove_self_learning)

### 433 Mhz Antenne bauen

Here you find a [HowTo](https://arduinodiy.wordpress.com/2015/07/25/coil-loaded-433-mhz-antenna/) or on file (433-coil-antenna.pdf)

### 433Utils

Found on [Github](https://github.com/ninjablocks/433Utils)