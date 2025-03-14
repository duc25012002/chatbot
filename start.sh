#!/bin/bash
chmod +x start.sh
rm -rf /opt/render/.local/lib/python*
pip install --no-cache-dir -r requirements.txt  
pip install gunicorn
pip install flask
export PATH=$PATH:/opt/render/.local/bin
gunicorn -w 4 -b 0.0.0.0:$PORT run:app  
