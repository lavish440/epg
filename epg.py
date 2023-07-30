import requests
from datetime import datetime
import xmltodict
import time
import sys
import gzip
from concurrent.futures.thread import ThreadPoolExecutor

API = "http://jiotv.data.cdn.jio.com/apis"
IMG = "http://jiotv.catchup.cdn.jio.com/dare_images"
channel = []
programme = []
error = []
result = []
done = 0


def genEPG(i, c):
    global channel, programme, error, result, API, IMG, done
    # for day in range(-7, 8):
    # 1 day future , today and two days past to play catchup
    for day in range(-2, 2):
        try:
            resp = requests.get(f"{API}/v1.3/getepg/get", params={"offset": day,
                                "channel_id": c['channel_id'], "langId": "6"}).json()
            day == 0 and channel.append({
                "@id": c['channel_id'],
                "display-name": c['channel_name'],
                "icon": {
                    "@src": f"{IMG}/images/{c['logoUrl']}"
                }
            })
            for eachEGP in resp.get("epg"):
                pdict = {
                    "@start": datetime.utcfromtimestamp(int(eachEGP['startEpoch']*.001)).strftime('%Y%m%d%H%M%S'),
                    "@stop": datetime.utcfromtimestamp(int(eachEGP['endEpoch']*.001)).strftime('%Y%m%d%H%M%S'),
                    "@channel": eachEGP['channel_id'],
                    "@catchup-id": eachEGP['srno'],
                    "title": eachEGP['showname'],
                    "desc": eachEGP['description'],
                    "category": eachEGP['showCategory'],
                    # "date": datetime.today().strftime('%Y%m%d'),
                    # "star-rating": {
                    #     "value": "10/10"
                    # },
                    "icon": {
                        "@src": f"{IMG}/shows/{eachEGP['episodePoster']}"
                    }
                }
                if eachEGP['episode_num'] > -1:
                    pdict["episode-num"] = {
                        "@system": "xmltv_ns",
                        "#text": f"0.{eachEGP['episode_num']}"
                    }
                if eachEGP.get("director") or eachEGP.get("starCast"):
                    pdict["credits"] = {
                        "director": eachEGP.get("director"),
                        "actor": eachEGP.get("starCast") and eachEGP.get("starCast").split(', ')
                    }
                if eachEGP.get("episode_desc"):
                    pdict["sub-title"] = eachEGP.get("episode_desc")
                programme.append(pdict)
        except Exception as e:
            print(e)
            error.append(c['channel_id'])
    done += 1
    # print(f"{done*100/len(result):.2f} %", end="\r")


if __name__ == "__main__":
    stime = time.time()
    # prms = {"os": "android", "devicetype": "phone"}
    raw = requests.get(
        f"{API}/v3.0/getMobileChannelList/get/?langId=6&os=android&devicetype=phone&usertype=tvYR7NSNn7rymo3F&version=285").json()
    result = raw.get("result")
    with ThreadPoolExecutor() as e:
        e.map(genEPG, range(len(result)), result)
    epgdict = {"tv": {
        "channel": channel,
        "programme": programme
    }}
    epgxml = xmltodict.unparse(epgdict, pretty=True)
    with open("epg.xml.gz", 'wb+') as f:
        f.write(gzip.compress(epgxml.encode('utf-8')))
    # with open(sys.argv[1], 'rb') as f_in:
    #     with gzip.open(sys.argv[2], 'wb+') as f_out:
    #         f_out.write(gzip.compress(epgxml.encode('utf-8')))
    print("EPG updated", datetime.now())
    if len(error) > 0:
        print(f'error in {error}')
    print(f"Took {time.time()-stime:.2f} seconds")
