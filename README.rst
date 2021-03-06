tagNFC_DB_server
=================

An open source system to manage machines in a cool makerspace!
--------------------------------------------------------------

The system is composed by nodes and 1 gateway. The gateway is a raspberry pi 3 with an RF69HW moteino board connected trough UART.
Each node has at least 1 moteino board and a NFC tag shield.

## Gateway

https://mongopi.wordpress.com/2012/11/25/installation/

I'm using Raspberry PI 3.
Download raspbian from [here] (https://www.raspberrypi.org/downloads/raspbian/)

Follow all the instructions [here](https://www.raspberrypi.org/documentation/installation/installing-images/)

1- SDFormatter


Resize to the max size
      sudo raspi-config
      --resize

update


      sudo apt-get update
      sudo apt-get upgrade
      sudo apt-get dist-upgrade
      sudo rpi-update
      sudo dpkg-reconfigure tzdata

from https://openenergymonitor.org/emon/node/12311

      sudo nano /boot/config.txt
      *add* core_freq=250
      *add* dtoverlay=pi3-disable-bt
      sudo systemctl disable hciuart

prevent rpi3 to use UART

      sudo nano /boot/cmdline.txt
      dwc_otg.lpm_enable=0 console=serial1,115200  console=tty1 root=/dev/mmcblk0p2  kgdboc=serial1,115200 rootfstype=ext4 elevator=deadline fsck.repair=yes  rootwait

test UART

      sudo apt-get install minicom
      sudo minicom -D /dev/ttyAMA0 -b115200

setup wifi

      https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md




## Run on startup (?)

http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

      sudo /etc/init.d/goMonitor.sh start
      sudo /etc/init.d/goMonitor.sh status
      sudo /etc/init.d/goMonitor.sh stop

      http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html

      python myscript.py >/tmp/script_stdout.txt 2>/tmp/script_stderr.txt &
      sudo update-rc.d NameOfYourScript defaults
      sudo update-rc.d -f  NameOfYourScript remove

## Webserver

      https://www.raspberrypi.org/documentation/remote-access/web-server/apache.md


      sudo apt-get install git-core
      ssh-keygen -t rsa -b 4096 -C "you@example.com"
      eval "$(ssh-agent -s)"
      ssh-add ~/.ssh/id_rsa
      tail ~/.ssh/id_rsa.pub
      --copy and paste it to github/settings--
      git clone git@github.com:paolocavagnolo/tagNFC_DB_server.git
      git config --global user.email "you@example.com"
      git config --global user.name "Your Name"

## Put scripts in /usr/bin/
      sudo cp /home/pi/Documents/tagNFC_DB_server/script/updateGateway.sh /usr/bin/
      sudo chmod 755 /usr/bin/updateGateway.sh

## Setup machine for python big program

      sudo apt-get install python-nose

### Install MongoDB
http://andyfelong.com/2016/01/mongodb-3-0-9-binaries-for-raspberry-pi-2-jessie/

### Install gspread
      sudo pip install PyOpenSSL
      sudo pip install --upgrade oauth2client
      sudo pip install gspread
      scp **the json credential to rpi**

### Install plotly

      sudo pip install plotly






## Platformio

http://www.russelldavis.org/2015/08/01/platformio-on-the-raspberry-pi/
https://github.com/deanmao/avrdude-rpi

      sudo apt-get install libmpc-dev libelf1 libftdi1
      sudo python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"
      platformio init --board uno --board uno
      platformio lib search Adafruit-PN*
      platformio lib search SPI*
      platformio lib search RFM69*

      plarformio lib install 125
      platformio lib install 92

      git clone git@github.com:deanmao/avrdude-rpi.git

      sudo cp ~/Documents/avrdude-rpi/a* /home/pi/.platformio/packages/tool-avrdude/
      mv /home/pi/.platformio/packages/tool-avrdude/avrdude /home/pi/.platformio/packages/tool-avrdude/avrdude-original
      ln -s /home/pi/.platformio/packages/tool-avrdude/avrdude-autoreset /home/pi/.platformio/packages/tool-avrdude/avrdude

      *** platformio run --upload-port /dev/ttyAMA0 -t upload




## Set-up VPN for remote controll

https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-debian-8




## CRONTAB
sudo service mongodb start


https://www.raspberrypi.org/forums/viewtopic.php?f=108&t=120793

      sudo apt-get install xinput

http://forums.pimoroni.com/t/official-7-raspberry-pi-touch-screen-faq/959
