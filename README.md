# IoT Toolkit for Coworking Spaces


## Requirements

* Raspberry Pi Model 3B+
* Speaker pHAT
* Adafruit PN532 RFID/NFC Shield (v1.3+)
* SparkFun FT231X Breakout


## Hardware

1. On Adafruit **Adafrauit PN532 RFID/NFC Shield**, make sure SEL0 is closed (solder bridge) and SEL1 is open. This will switch PN532 in UART mode.

1. Connect signals between **Adafrauit PN532 RFID/NFC Shield** and **SparkFun FT231X Breakout** in the following way:

   | RFID/NFC Shield | FT231X Breakout |
   |-----------------|-----------------|
   | 5V              | VCC             |
   | GND             | GND             |
   | Analog in 4     | RX              |
   | Analog in 5     | TX              |


## Software

### Basic Installation

1. Prepare Raspberry Pi with MicroSD card and Raspbian on it.

   > Use balenaEtcher to flash the Raspbian image.

1. Put empty file `ssh` to the `boot` partition of the SD card to enable SSH access.

1. Insert the MicroSD card to Raspberry Pi and connect the power adapter.

1. SSH to your Raspberry Pi:

       ssh pi@<ip-address>

1. Change default password:

       passwd

1. Set correct locales:

       echo "en_US.UTF-8 UTF-8" | sudo tee /etc/locale.gen
       sudo locale-gen
       echo "LC_ALL=en_US.UTF-8" | sudo tee /etc/default/locale

1. Logout and SSH back to Raspberry Pi with the new password:

       logout
       ssh pi@<ip-address>

1. Set correct timezone:

       sudo dpkg-reconfigure tzdata

1. Change default hostname to `cwgtk`:

       sudo hostnamectl set-hostname cwgtk

1. Overwrite `raspberry` to `cwgtk` in `/etc/hosts`:

       sudo nano /etc/hosts
       
1. Reboot system and SSH back to Raspberry Pi:

       sudo reboot
       ssh pi@<ip-address>

1. Upgrade system packages:

       sudo apt update
       sudo apt upgrade

1. Reboot system and SSH back to Raspberry Pi:

       sudo reboot
       ssh pi@<ip-address>

1. Install common tools:

       sudo apt install git mc tmux vim

1. Select default editor `/bin/nano`:

       select-editor


## Setup Coffee Log

1. Install NFC library:

       sudo apt install libnfc-dev libnfc5
       
1. Edit `linbnfc.conf` file:

       sudo nano /etc/nfc/libnfc.conf

1. Uncomment and edit the following lines:

       device.name = "pn532_uart"
       device.connstring = "pn532_uart:/dev/ttyUSB0"

1. Download `cwgtk`:

       git clone https://github.com/hubpav/cwgtk.git

1. Build `tagcat`:

       cd ~/cwgtk/tagcat
       make

1. Install support for Python 3 virtual environments:

       sudo apt install python3-venv

1. Install required Python 3 packages:

       cd ~/cwgtk/coffeelog
       python3 -m venv env
       source env/bin/activate
       pip3 install -r requirements.txt
       
1. Fix dependency issue with Python 3.7:

       pip3 install 'grpcio==1.23.0' --force-reinstall

1. Install `/home/pi/cwgtk.json` file with Google API credentials.

1. Install `mpg123`:

       sudo apt install mpg123


### Background Service

1. Edit `coffeelog.service` file:

       sudo nano /etc/systemd/system/coffeelog.service

1. Insert this content:

       [Unit]
       Description=CWGTK - Coffee Log Service
       After=network.target
       StartLimitIntervalSec=0

       [Service]
       Type=simple
       User=pi
       ExecStart=/home/pi/cwgtk/coffeelog/run.sh
       Restart=always
       RestartSec=1

       [Install]
       WantedBy=multi-user.target
       
1. Start and enable the service:

       sudo systemctl start coffeelog.service
       sudo systemctl enable coffeelog.service


### Loudspeaker Setup - Speaker pHAT

Run this command:

    curl -sS https://get.pimoroni.com/speakerphat | bash

Answer `N` when asked about full install:

    Do you wish to perform a full install? [y/N] N

When asked about reboot, answer `y`:

    Would you like to reboot now? [y/N] y


### Loudspeaker Setup - USB

1. Edit `alsa.conf` file:

       sudo nano /usr/share/alsa/alsa.conf

1. Update these two parameters to index `1`:

       defaults.ctl.card 1
       defaults.pcm.card 1

1. Create this configuration file:

       sudo nano /etc/asound.conf

1. Insert this content:

       pcm.!default  {
         type hw card 1
       }

       ctl.!default {
         type hw card 1
       }

### Install SQLite Webserver

The following procedure will configure **phpLiteAdmin** with the SQLite database.

1. Change default **phpLiteAdmin** password:

       nano /home/pi/cwgtk/phpliteadmin/phpliteadmin.config.php

1. Install required packages:

       sudo apt install lighttpd php-cgi php-cli php-mbstring php-sqlite3

1. Configure webserver:

       sudo lighty-enable-mod fastcgi
       sudo lighty-enable-mod fastcgi-php
       sudo service lighttpd force-reload

1. Create symlinks to phpLiteAdmin:

       cd /var/www/html
       sudo ln -s /home/pi/cwgtk/phpliteadmin/phpliteadmin.config.php
       sudo ln -s /home/pi/cwgtk/phpliteadmin/phpliteadmin.php index.php

1. Open Raspberry Pi IP address in your browser - you should see a login page.


## Contributing

Please read [**CONTRIBUTING.md**](https://github.com/hubpav/cwgtk/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.


## Versioning

We use [**SemVer**](https://semver.org/) for versioning. For the versions available, see the [**tags on this repository**](https://github.com/hubpav/cwgtk/tags).


## Authors

* [**Pavel Hübner**](https://github.com/hubpav) - Initial work


## License

This project is licensed under the [**MIT License**](https://opensource.org/licenses/MIT/) - see the [**LICENSE**](https://github.com/hubpav/cwgtk/blob/master/LICENSE) file for details.
