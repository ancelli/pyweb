#!/usr/bin/python
#-*- coding:utf-8 -*-
# ancelli
import socket 
import os,sys
import select
import thread
import subprocess
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

###########################################config##############################################
CONFIG={'cgi_dir':'/home/ancelli/work/wechat/',
        'static_dir':'/home/ancelli/work/wechat/',
        'logLevel':3
}
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='/var/log/wechat/server.log',
                filemode='a')
logger = logging.getLogger("http-server")
###############################################################################################
def DEBUG(lStr):
    if CONFIG['logLevel'] >= 3 :
        logger.debug( lStr )
def INFO(lStr):
    logger.info( lStr )
def ERROR(lStr):
    logger.error( lStr )
RET404={'httpCode':404,'content':'404 not found','headers':{'Connection':'close'}}

class HttpSvr():
    def __init__(self):
        self.env = os.environ
        self.env['SERVER_PROTOCOL'] = 'HTTP/1.0'
        pass
    def readStaticFile(self,sFilePath):
        inFile = open(sFilePath,'rb')
        try:
            return inFile.read()
        except Exception as e:
            ERROR( e )
        finally:
            inFile.close()
    def httpRead(self , data):
        httpData = {}
        try :
            httpData = {}
            tmp = data.split(' ')
            httpData['action'] = tmp[0]
            httpData['uri'] = ""
            _headers = {}
            if len(tmp) > 1 :
                httpData['uri'] = data.split(' ')[1]
            tmp = data.split('\r\n')
            headLen = len(tmp)
            if httpData['action'] == 'POST' :
                httpData['postData'] = tmp[ len(tmp) -1 ]
                headLen  = headLen - 1
            for i in range(1,headLen):
                    if tmp[i].find(':') > -1 :
                        _headers[ tmp[i].split(':')[0] ] = tmp[i].split(':')[1].strip()
            httpData['headers'] = _headers
            _extname = ""
            _param = ""
            tmp = httpData['uri'].split('?')
            _cgiFile = tmp[0]
            if len(tmp) > 1 :
                _param = tmp[1]
            if httpData['action'] == 'POST':
                if httpData['postData'].find('&') > 0 and httpData['postData'].find('=') > 0 :
                    _param += str(httpData['postData'])
                else:
                    _param += "&postData=%s"%str(httpData['postData'])
            tmp2 = _cgiFile[-5:].split('.')
            if len(tmp2) > 1 : _extname = tmp2[1]
            httpData['extname'] = _extname
            httpData['param'] = _param
            httpData['cgiFile'] = _cgiFile
            INFO("%s"%str(httpData))
        except Exception as e: 
            ERROR("%s,%s"%(data,e))
        return httpData
    def process(self , request):
        DEBUG('process: begin')
        _response = {}
        _response['httpCode'] = 200
        _response_header = {}
        if request['extname'] in ['cgi','py','sh'] :
            DEBUG('cgi process')
            filePath = "%s%s"%(CONFIG['cgi_dir'],request['cgiFile'])
            if not os.path.exists(filePath) or os.path.isdir(filePath) : 
                return RET404
            proc = subprocess.Popen("%s \"%s\""%(filePath, request['param']), shell=True, stdout=subprocess.PIPE,env=self.env)
            _response['content'] = proc.stdout.read()
            _response_header['content-type'] = "text/json"
            _response_header['Content-Length'] = len(_response['content'])
        else: 
            filePath = "%s%s"%(CONFIG['static_dir'],request['cgiFile'])
            DEBUG('static process , %s'%filePath)
            if not os.path.exists(filePath)  or os.path.isdir(filePath) :
                 return  RET404
            _response['content'] = self.readStaticFile(filePath)
            _response_header['Content-Length'] = len(_response['content'])
            _response_header['content-type'] = "text/%s"%request['extname']
            if request['extname']  in ['jpg','png','gif','jpeg','ico']:
                _response_header['content-type'] = "image/%s"%request['extname']
        INFO( "%s"%str(request['uri']) )
        if 'Connection' in request['headers']:
            if request['headers']['Connection'] == 'keep-alive':
                _response_header['Connection'] = 'keep-alive'
            else:
                _response_header['Connection'] = 'close'
        _response['headers'] = _response_header
        return _response 

    def handler(self , client , addr):
        DEBUG('handler: %s'%str(client))
        try : 
            data = client.recv(1024)
        except Exception as e:
            ERROR(e)
        request = self.httpRead(data)
        response = self.process( request)
        headers = response['headers']
        headerText=""
        for key in headers:
            headerText +="%s:%s\r\n"%(key,headers[key])
        if response['httpCode'] == 200 :
            h = "HTTP/1.1 200 OK\r\n%s\r\n%s" % ( headerText , response['content'] )
        if response['httpCode'] == 404 :
            h = "HTTP/1.1 404 not found\r\n%s\r\n%s" % ( headerText , response['content'] )
        server_response = h
        if 'content-type' in headers:
            if headers['content-type'].find('text/') > -1 :
                try :
                    server_response = h.encode('utf-8')
                except Exception as e:
                    print e,headers['content-type']
        client.send(server_response)

    def run(self,ip,port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind( (ip,int(port)) )
        server.listen(1204)
        while True:
            client, address = server.accept()     # 建立客户端连接。
            INFO('connected from %s'%str(address))
            thread.start_new_thread(self.handler, (client, address))
            #self.handler(c, addr)
            #c.close()                # 关闭连接

#run
if __name__ == "__main__":
    if len(sys.argv) < 3 :
        ERROR("%s ip port"%sys.argv[0])
        exit(1)
    ip = sys.argv[1]
    port = sys.argv[2]
    httpd = HttpSvr()
    httpd.run(ip,port)

