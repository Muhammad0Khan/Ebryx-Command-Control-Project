#!/bin/bash

# Run the CPU Info Script in the Background
python3 myapp/scripts/cpu_info_script.py &
# Run the Server
python3 manage.py runserver