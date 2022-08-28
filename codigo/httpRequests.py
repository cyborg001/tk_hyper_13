import http.client
from enum import Enum
from http.client import HTTPConnection
import json
import ssl
import urllib.parse


class HttpRequest():
    mainUrl=""
    def __init__(self,endpoint=""):
        self.mainUrl=endpoint
        super().__init__()

    def MakeRequest(self,url,HttpMethods,body,params,headers):
        toSend={}
        if body!="":
            toSend=body.toJSON()
       # ssl._create_default_https_context=ssl._create_unverified_context
        conn = http.client.HTTPConnection(self.mainUrl)
        try:
            conn.request(HttpMethods.name, url,toSend,headers)
            response = conn.getresponse()
            data={}
            if response.code ==200:
                data= json.loads(response.read())
            else:
                data= json.loads('{"status":-1}')
            return data
            pass
        except Exception as identifier:
            return json.loads('{"status":-1}')
            pass
        finally:
            conn.close()
            pass
        
        


class HttpMethods(Enum):
    GET=1,
    POST=2,
    PUT=3,
    DELETE=4,
    PATCH=5
