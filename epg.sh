#!/bin/bash
termux-notification --ongoing --id "epg" --group "group" -c "EPG generation started"
cd ~/git/epg
python epg.py
termux-notification --id "epg" --group "group" -c "EPG Generation Finished"
git add epg.xml.gz
git commit -m "Updated EPG"
git push origin
termux-notification --id "epg" --group "group" -c "EPG pushed to Github"
