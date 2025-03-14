#!/bin/bash
chmod +x start.sh
pip install --no-cache-dir -r requirements.txt  
gunicorn -w 4 -b 0.0.0.0:$PORT run:app  
