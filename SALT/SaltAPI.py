#!/usr/bin/env python
#coding=utf-8

import urllib2, urllib, json

#Python 2.7.9 之后版本引入了一个新特性
#当你urllib.urlopen一个 https 的时候会验证一次 SSL 证书
#当目标使用的是自签名的证书时就会爆出一个
#urllib.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:581)> 的错误消息，
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class SaltAPI:
    def __init__(self,url,username,password):
        self.__url = url.rstrip('/') #移除URL末尾的/
        self.__username = username
        self.__password = password
        self.__token_id = self.SaltLogin()
    #登陆获取token
    def SaltLogin(self):
        params = {'eauth': 'pam', 'username': self.__username, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        headers = {'X-Auth-Token':''}
        url = self.__url + '/login'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        try:
            token = content['return'][0]['token']
            #3489c6508041569a102f25bd09bf9072a1152bcb
            return token
        except KeyError:
            raise KeyError
    #推送请求
    def PostRequest(self, obj, prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token': self.__token_id}
        req = urllib2.Request(url,obj, headers)  # obj为传入data参数字典，data为None 则方法为get，有date为post方法
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        return content

    #将接收的参数通过推送请求获取命令执行结果
    #如 params = {'client':'local', 'fun':'test.ping', 'tgt':'*'}
    #如 params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': 'nodegroup'}
    def SaltRun(self, params,prefix='/'):
        if params:
            obj = urllib.urlencode(params)
        else:
            obj = None
        res = self.PostRequest(obj,prefix)
        return res
    #异步命令，仅返回jid和minions
    def SaltCmd(self,tgt,fun,arg,client='local_async',expr_form='glob',**kwargs):
        if arg:
            params = {'client':client, 'fun':fun, 'tgt':tgt, 'arg':arg,'expr_form':expr_form}
        else:
            params = {'client':client, 'fun':fun, 'tgt':tgt, 'expr_form':expr_form}
        if kwargs:
            params=dict(params.items()+kwargs['kwargs'].items())
            print kwargs
            print params
        obj = urllib.urlencode(params)
        res = self.PostRequest(obj)
        # res=self.SaltRun(params)
        return res
        #{u'return': [{u'jid': u'20160331104340284003', u'minions': [u'saltminion01-41.ewp.com']}]}

    #获取JOB ID的详细执行结果
    def SaltJob(self,jid=''):
        # params = {'client':'runner', 'fun':'jobs.lookup_jid', 'jid': jid}
        if jid:
            prefix = '/jobs/'+jid
        else:
            prefix = '/jobs'
        res = self.PostRequest(None,prefix)
        return res
    #{u'info': [{u'Function': u'cmd.run', u'jid': u'20160415114825662427', u'Result': {u'saltminion02-42': {u'return': u'saltminion02-42'}, u'saltminion01-41.ewp.com': {u'return': u'saltminion01-41.ewp.com'}}, u'Target': u'saltminion02-42,saltminion01-41.ewp.com', u'Target-type': u'list', u'User': u'salt', u'StartTime': u'2016, Apr 15 11:48:25.662427', u'Minions': [u'saltminion01-41.ewp.com', u'saltminion02-42'], u'Arguments': [u'hostname']}], u'return': [{u'saltminion01-41.ewp.com': u'saltminion01-41.ewp.com'}]}

    #获取grains
    def SaltMinions(self,minion=''):
        if minion and minion!='*':
            prefix = '/minions/'+minion
        else:
            prefix = '/minions'
        res = self.PostRequest(None,prefix)
        return res

    #pip install websocket-client
    # def SaltEvents(self):
    #     from websocket import create_connection
    #
    #     ws = create_connection('ws://10.188.1.40:8000/ws/'+self.__token_id)
    #     print "Sending 'Hello, World'..."
    #     ws.send('websocket client ready')
    #     print "Sent"
    #     print "Reeiving..."
    #     # Look at https://pypi.python.org/pypi/websocket-client/ for more examples.
    #     # while listening_to_events:
    #     result = ws.recv()
    #     print result
    #     ws.close()

#测试：python manager.py shell ; from SALT.SaltAPI import * ; main()，代码修改了要ctrl+Z退出重进
def main():
    idc = '2'
    tgt = 'saltmaster-40.ewp.com'   #  '*'不能使用list类型
    # tgt = 'saltminion01-41.ewp.com,saltminion02-42'
    fun ='file.write'
    client = 'local'
    arg = ['/srv/salt/test.txt','fadfwef2f']
    kwargs={'args': 'fadfwef2f'}
    from models import SaltServer
    salt_server = SaltServer.objects.get(ip__server__idc=idc) #根据机房ID选择对应salt服务端
    # print salt_server.url
    sapi = SaltAPI(url=salt_server.url,username=salt_server.username,password=salt_server.password)
   #异步执行命令，仅返回jid和minions
    result = sapi.SaltCmd(tgt=tgt,fun=fun,client=client,arg=arg)
    # print result
    #通过返回的minions获取其grains信息
    # minions= sapi.SaltMinions(result['return'][0]['minions'][1])
    # print minions
    # jid = result['return'][0]['jid']
    # print jid
    # jidinfo=sapi.SaltJob(jid)
    # print jidinfo
    # evt=sapi.SaltEvents()
    # print evt
    return (result)

#ssh: ::: {u'return': [{u'minion03': {u'fun_args': [], u'jid': u'20160418114256060122', u'return': True, u'retcode': 0, u'fun': u'test.ping', u'id': u'minion03'}}]}
#local::: {u'return': [{u'saltminion03-43.ewp.com': True, u'saltminion01-41.ewp.com': True, u'saltminion02-42.ewp.com': True, u'saltmaster-40.ewp.com': True}]}
#local_async:::{u'return': [{u'jid': u'20160331104340284003', u'minions': [u'saltminion01-41.ewp.com']}]}


if __name__ == '__main__':
    main()