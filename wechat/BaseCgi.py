#!/usr/bin/python
#-*- coding:utf-8 -*-
# author: ancelli@tencent.com

import sys,os,time
import json
import urllib2,Cookie

class BaseCgi():
    def __init__( self ): 
        self.req = {}
        self.formatInput()
    def formatInput(self):
        _param = ""
        if len( sys.argv ) > 1 : 
            _param = sys.argv[1]
        if _param != "" : 
            tmp = _param.split("&")
            for t in tmp: 
                tmp2 = t.split('=')
                if len(tmp2) < 2: continue
                self.req[ tmp2[0] ] = tmp2[1]
    def checkSession(self):
        if '_login_time' in self.cookie :
            self._login_time = int(self.GetCookie('_login_time'))
        if int(time.time()) > self._login_time + 604800 :
            self.Redirect('/login')
            return
        if '_login_name' in self.cookie :
            self._login_name = self.GetCookie('_login_name')
        else:
            self.Redirect('/login')
            return
        
    def getCookie(self,key):
        for c in self.cookie:
            if c == key :
                return self.cookie[key].value
                
    def setCookie(self):
        try:
            login_name = self._req["login_name"].value
            self.cookie.SetCookie("_login_name",login_name)
            self.cookie.SetCookie("_login_time",int(time.time()))
        except:
            pass

    def redirect(self,url):
        print '<html> <head> <meta http-equiv="Refresh" content="0;url=%s"> </head> <body> Loading... </body> </html>'%url

    def write(self,_result):
        print json.dumps(_result)
    
    def getParam(self,sName):
        sValue = ''
        if sName in self.req :
            sValue = self.req[sName]
        return sValue
    def getParams(self,data=[]):
        _result = {}
        for d in data :
            if self.req.has_key(d) :
                _result[d] = self.req[d]
            else:
                _result[d] = ''
        return _result
    def getPostData(self):
        return self.getParam('postData')
    def do(self):
        print self.req
        pass    

if __name__ == '__main__':
    cgi = BaseCgi()
    cgi.do()
