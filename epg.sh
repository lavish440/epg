#!/bin/bash
if [[ $OSTYPE == "linux-android" ]]; then
	termux-notification --ongoing --id "epg" --group "group" -c "EPG generation started"
fi
cd ~/git/epg
python epg.py
if [[ $OSTYPE == "linux-android" ]]; then
	termux-notification --id "epg" --group "group" -c "EPG Generation Finished"
fi
git add epg.xml.gz
git commit -m "Updated EPG"
git push origin
if [[ $OSTYPE == "linux-android" ]]; then
	termux-notification --id "epg" --group "group" -c "EPG pushed to Github"
fi
