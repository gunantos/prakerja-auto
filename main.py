import json
import requests
import time
from math import floor
import webbrowser

url = 'https://prakerja.karier.mu'
program_id = <<you program id>>
token = <<you token>>
headers = {
    'origin': url,
    'referer': url,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
    'authorization': token,
    'Content-Type': 'application/json'
}


def success(id):
    payload = json.dumps({
        "program_user_id": program_id,
        "resource_id": id,
        "is_finish": True
    })
    url = "https://api.sekolah.mu/program_activity/activity/?platform=kariermu&source=a2FyaWVyLm11LXdlYg=="
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def mulai(id):
    payload = json.dumps({
        "program_user_id": program_id,
        "resource_id": id,
        "is_finish": False
    })
    url = "https://api.sekolah.mu/program_activity/activity/?platform=kariermu"
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def getList():
    url = "https://api.sekolah.mu/program_activity/v2/product_by_activity/solusi-yang-tepat-part-1/activity?platform=kariermu"
    _response = requests.request("GET", url, headers=headers)
    response = _response.json()
    print(response['status'])
    list = []
    ke = 1
    if response['status'] == 200:
        r = response['data']['chapter_list']
        for key in r:
            sub = 1
            chapter = key['chapters'][0]['resource_detail']
            for c in chapter:
                _l = {}
                _l['type'] = c['type']
                _l["id"] = c['id']
                _l["duration"] = c['duration']
                _l["locked"] = c['is_locked']
                _l["complete"] = c['is_complete']
                _l['url'] = c['url']
                _l['slug'] = c['slug']
                _l['title'] = c['title']
                _l['ke'] = str(ke) + "-" + str(sub)
                list.append(_l)
                sub += 1
            ke += 1
    return list


listdata = getList()
on = False
start_time = 0
run = True
ke = 0
soal_ke = 0
while run:
    for itm in listdata:
        print(itm['ke']+". " + itm['title'])
        if itm['complete'] == True:
            print("==Sudah dikerjakan==")
        else:
            if itm['type'] == 'video':
                print("-----> Mulai menonton")
                mulai(itm['id'])
                start_time = time.time()
                dur = itm['duration']
                tunggu = True
                detik = 0
                sisa = 0
                old_sisa = 0
                while tunggu:
                    t = floor(time.time() - start_time)
                    if (detik != t):
                        detik = t
                    ts = floor(t / 60)
                    sisa = dur - ts
                    if (sisa != old_sisa):
                        old_sisa = sisa
                        print("wait " + str(sisa))
                    if sisa <= 0:
                        tunggu = False
                success(itm['id'])
                print("-----> selesai menonton")
            else:
                slug = itm['slug']
                webbrowser.get(
                    using='windows-default').open("${url}/aktivitas/${slug}", new=2)
                _l = True
                while _l:
                    c = input("Jika anda telah menyelesaikan, ketik [y]: ")
                    if c.lower() == 'y':
                        _list = getList()
                        if _list[soal_ke]['complete'] == True:
                            _l = False
                        else:
                            print('--soal belum dikerjakan--')
                            webbrowser.get(
                                using='windows-default').open("${url}/aktivitas/${slug}", new=2)
        soal_ke += 1
