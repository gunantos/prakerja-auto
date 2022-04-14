from asyncio import threads
from email import header
import json
import requests
from urllib.parse import urljoin
import time
from math import floor
import webbrowser

from requests.api import head


class API:
    source = 'a2FyaWVybXUtd2Vi'
    program_id = ''
    user_id = ''
    token_not_login = 'Sekolahmu0App0Key0Secret!!!'
    token = ''
    url_origin = 'https://prakerja.karier.mu'
    url = 'https://api.sekolah.mu'
    user = {}
    program_user_id = ''
    url_link = ''
    email=''
    password=''

    headers = {
        'accept': 'application/json, text/plain, */*',
        'origin': url_origin,
        'referer': url_origin+'/',
        'authorization': token,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
        'Content-Type': 'application/json'
    }

    def __init__(self, email='', password=''):
        self.email = email
        self.password = password

    def getHeader(self, islogin=False):
        header = self.headers
        if islogin:
            header['authorization'] = self.token_not_login
            header['Content-Type'] = 'application/x-www-form-urlencoded'
        else:
            self.headers['authorization'] = self.token
            header['Content-Type'] = 'application/json'
        return self.headers

    async def req(self, method="GET", uri='', data={}, islogin=False):
        header = self.getHeader(islogin)
        url = urljoin(self.url, uri)
        req = requests.request(method, url, headers=header, data=data)
        return req.json()

    async def login(self, email, password):
        payload = json.dumps({
            "agent": "Chrome",
            "email": email,
            "latitude": "",
            "longitude": "",
            "operation_system": "Chrome 100.0.4896.75",
            "password": password,
            "source": self.source
        })
        req = await self.req('POST', '/v2/auth/login?platform=kariermu', payload, True)
        if req['status'] == 200:
            self.user = req['data']
            self.user_id = req['data']['id']
            self.token = req['token']['token']
            return {
                "user_id": self.user_id,
                "token": self.token
            }
        else:
            return False

    async def getProgram(self):
        uri = "/program_activity/enrolled/" + str(self.user_id) + "/1/12?platform=kariermu"
        res = await self.req('GET', uri)
        if (res['status'] == 200):
            data = res['data']
            for dat in data:
                if dat['status']:
                    self.program_id = dat['id']
                    self.program_user_id = dat['program_user_id']
                    pass
            return {
                "program_id": self.program_id,
                "program_user_id": self.program_user_id
            }
        else:
            return False

    async def getLinkActivitas(self):
        program = await self.getProgram()
        if (program == False):
            print('ERROR YOU MUST LOGIN FIRST')
            return False
        else:
            program_id = program['program_id']
            uri = '/program/first-activity-multi-program/?platform=kariermu'
            payload = json.dumps({
                "program_id_list": [program_id]
            })
            res = await self.req('POST', uri, payload)
            if (res['status'] == 200):
                data = res['data']
                self.url_link = res['data'][0]['first_activity_slug']
                return self.url_link
            else:
                return False

    async def getList(self):
        getlink = await self.getLinkActivitas()
        if (getlink == False):
            return False
        else:
            url = "/program_activity/v2/product_by_activity/"+ str(self.url_link) +"/activity?platform=kariermu"
            response = await self.req('GET', url)
            list = []
            ke = 1
            if response['status'] == 200:
                self.program_user_id = response['data']['program_user_id']
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

    async def end_video(self, id):
        payload = json.dumps({
            "program_user_id": self.program_user_id,
            "resource_id": id,
            "is_finish": True
        })
        url = "/program_activity/activity/?platform=kariermu&source=a2FyaWVyLm11LXdlYg=="
        response = await self.req('POST', url, payload)
        print(response)

    async def start_video(self, id):
        payload = json.dumps({
            "program_user_id": self.program_user_id,
            "resource_id": id,
            "is_finish": False
        })
        url = "/program_activity/activity/?platform=kariermu"
        response = await self.req('POST', url, payload)
        print(response)

    async def start_login(self):
        email = input('Masukkan email anda : ')
        password = input('Masukkan password anda : ')
        print('tunggu sedang login ke sistem')
        req = await self.login(email, password)
        if req:
            return req
        else:
            return await self.start_login()

    async def run(self, email='', password=''):
        if email != '':
            self.email = email
        if password != '':
            self.password = password
        print('Start aplication automatis prakerja')
        if (self.email != "" and self.password != ""):
            login = await self.login(self.email, self.password)
            if not login:
                raise Exception('Email atau password salah')
        else:
            login = await self.start_login()
        listdata = await self.getList()
        if listdata != False:
            soal_ke = 1
            for itm in listdata:
                print(itm['ke']+". " + itm['title'])

                if itm['complete'] == True:
                    print("==Sudah dikerjakan==")
                else:
                    if itm['type'] == 'video':
                        print("-----> Mulai menonton")
                        await self.start_video(itm['id'])
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
                        await self.end_video(itm['id'])
                        print("-----> selesai menonton")
                    else:
                        slug = itm['slug']
                        webbrowser.get(
                            using='windows-default').open("${url}/aktivitas/${slug}", new=2)
                        _l = True
                        while _l:
                            c = input(
                                "Jika anda telah menyelesaikan, ketik [y]: ")
                            if c.lower() == 'y':
                                _list = self.getList()
                                if _list[soal_ke]['complete'] == True:
                                    _l = False
                                else:
                                    print('--soal belum dikerjakan--')
                                    webbrowser.get(
                                        using='windows-default').open("${url}/aktivitas/${slug}", new=2)
                soal_ke += 1
            else:
                if (self.email != "" and self.password != ""):
                    login = await self.login(self.email, self.password)
                    if not login:
                        raise Exception('Email atau password salah')
                else:
                    print('Password atau email salah')
                    return await self.run()
