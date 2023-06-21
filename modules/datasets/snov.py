#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# @name   : EmailAll - Email Information Gathering Tools
# @url    : http://github.com/Taonn
# @author : Tao. (Taonn)
import requests
import re
import json

from common.search import Search
from urllib.parse import unquote, quote
from config import settings
from config.log import logger


class Snov(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Datasets'
        self.source = 'Snov'
        self.addr = 'https://app.snov.io'
        self.username = settings.snov_username
        self.password = settings.snov_password
        self.num = 999
        self.session = requests.session()
        self.proxies = {'http': '127.0.0.1:8080', 'https': '127.0.0.1:8080'}

    def login(self):

        header = {'Content-Type': 'application/json;charset=UTF-8'}
        resp = self.session.get(self.addr + '/login', verify=False)
        if resp:
            param = {
                "email": settings.snov_username,
                "password": settings.snov_password,
                "remember": "true"
            }
            json_param = json.dumps(param)
            new_rem = "true"
            regex = re.compile(r'"true"', re.S)
            json_param = re.sub(regex, new_rem, json_param)
            if 1:
                rep = self.session.post(self.addr + '/login', headers=header, data=json_param, verify=False)
                return True
            else:
                return

    def search(self):

        if self.login():
            self.header.update({'Content-Type': 'application/json;charset=UTF-8'})
            params = {"domain": self.domain,
                      "isGreen": "true",
                      "lastId": 0,
                      "perPage": 20}
            json_param = json.dumps(params)
            new_rem = 'true'
            regex = re.compile(r'"true"', re.S)
            json_param = re.sub(regex, new_rem, json_param)
            resp = self.session.post(self.addr + '/domain-search', headers=self.header, data=json_param, verify=False)
            if hasattr(resp, 'json'):
                resp_json = resp.json()
                cid = resp_json["companyInfo"]["id"]
                params = {"isGreen": "true",
                          "lastId": 0,
                          "perPage": self.num,
                          "page": 1}
                json_param = json.dumps(params)
                new_rem = "true"
                regex = re.compile(r'"true"', re.S)
                json_param = re.sub(regex, new_rem, json_param)
                rep = self.session.post(self.addr + f'/companies/{cid}', headers=self.header, verify=False)
                self.header.update({'Referer': f'https://app.snov.io/domain-search?name={self.domain}&tab=emails',
                                    'X-Requested-With': 'XMLHttpRequest'})
                rep = self.session.post(self.addr + f'/companies/{cid}/emails', headers=self.header, data=json_param, verify=False)
                emails = self.match_emails(rep)
                if emails:
                    self.results.update(emails)
                else:
                    return
        else:
            logger.log('ALERT', 'Search Failed! you need to configure the username&password in api.py file')
            return

    def run(self):
        self.begin()
        self.search()
        self.finish()
        self.save_json()
        self.save_res()


def run(domain):
    search = Snov(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
