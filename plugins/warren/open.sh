#!/bin/bash
cd /home/wilst/projects/personal/personas/plugins/warren
pkill -f "python3 -m http.server 7384" 2>/dev/null
python3 -m http.server 7384 &
sleep 0.5
explorer.exe "http://localhost:7384/dashboard.html"
