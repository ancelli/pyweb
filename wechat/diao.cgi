#!/usr/bin/python
# -*- coding: utf-8 -*- 
# author: ancelli ancelli@tencent.com

from BaseCgi import BaseCgi
import hashlib
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='/var/log/wechat/access.log',
                filemode='a')
logger = logging.getLogger("wechat-server")

class CGI(BaseCgi):
    def __init__(self):
        BaseCgi.__init__(self)
        self.token = "ancelli"
        pass    

    def localSignature(self, token, timestamp, nonce):
        items = [token, timestamp, nonce]
        items.sort()
        sha1 = hashlib.sha1()
        map(sha1.update,items)
        hashcode = sha1.hexdigest()
        return hashcode
    def isWeixinSignature(self, token, signature, timestamp, nonce):
        return signature == self.localSignature(token, timestamp, nonce) 

    def do(self):
        signature = self.getParam('signature')
        timestamp = self.getParam('timestamp')
        nonce = self.getParam('nonce')
        echostr = self.getParam('echostr')
        postData = self.getPostData()
        logger.debug(signature)
        logger.debug(timestamp)
        logger.debug(nonce)
        if self.isWeixinSignature(self.token, signature, timestamp, nonce) :
            if echostr :
                print echostr
            else:
                logger.debug(postData)
        
if __name__ == '__main__':
    _cgi = CGI() 
    _cgi.do()
