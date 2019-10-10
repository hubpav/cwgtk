#!/bin/bash

# Exit script on error or undefined variable
set -eu

# Set environmental variable for Google service account authorization
export GOOGLE_APPLICATION_CREDENTIALS='/home/pi/cwgtk.json'

# Switch to coffeelog directory
cd /home/pi/cwgtk/coffeelog

# Activate Python virtual environment for coffeelog
source env/bin/activate

# Pipe tagcat's stdout and coffeelog's stdin streams
../tagcat/tagcat | python3 -m coffeelog
