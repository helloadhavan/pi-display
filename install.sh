#!/bin/sh

set -e

password=$1

# install pip and some apt dependencies
echo $password | sudo -S apt-get update
echo $password | sudo -S apt install -y python3-pip python3-venv python3-pil python3-smbus

# remove existing virtual environment and create new one
echo $password | sudo -S rm -rf /opt/pidisplay-venv
echo $password | sudo -S python3 -m venv /opt/pidisplay-venv
echo $password | sudo -S chown -R $USER:$USER /opt/pidisplay-venv

# activate venv and install pidisplay
/opt/pidisplay-venv/bin/pip install --upgrade pip setuptools wheel
/opt/pidisplay-venv/bin/pip install .

# install picard display service
echo $password | sudo -S sed -i -e 's:#dtparam=i2c_arm=on:dtparam=i2c_arm=on:g'  /boot/config.txt || true
/opt/pidisplay-venv/bin/python -m pidisplay.create_display_service
echo $password | sudo -S mv picard_display.service /etc/systemd/system/picard_display.service
echo $password | sudo -S systemctl enable picard_display
echo $password | sudo -S systemctl start picard_display
