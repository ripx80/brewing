# Rip on Brewing

You need python3.5 or higher.

## Upgrading python3.7 on Raspbian

```bash
apt-get update && apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y

wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz
tar xf Python-3.7.0.tar.xz
cd Python-3.7.0
./configure
make -j 4
sudo make altinstall
cd ../;sudo rm -r Python-3.7.0
rm Python-3.7.0.tar.xz

# check if you need this packages with other programms
sudo apt-get --purge remove build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
sudo apt-get autoremove -y
sudo apt-get clean
```

## Usage

```bash
# developer run
python3 brewcontrol.py -d

# try-run with sensor test
python3 brewcontrol.py --try-run

# normal for brewing
python3 brewcontrol.py
```

## Zu beachten

Intervall Motorsteuerung (verbessertes durchmischen der Maische). Kurzes aussetzen des Motors.
Plattenschaltung, wie schnell kann die Hendi 3500 geschaltet werden.

Temperatur müsste direkt am Boden und ganz oben gemessen werden, um einen Durchschnittswert zu erhalten

## Erweiterungen

Lebensmittelechte Pumpe, 14,00
Isopropanol 70% Mischung
SSR-25DA SSR-40A
Tauchhülse
Refactormeter 0-32% Sugar Brix