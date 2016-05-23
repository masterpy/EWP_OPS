# -*- coding: utf-8 -*-
from django.shortcuts import  render,render_to_response,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required  #setting: LOGIN_URL = '/auth/login/'
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import  PasswordChangeForm
from models import *
from CMDB.models import *
from CMDB.views import host
from django.db.models import Q
import datetime
from SaltAPI import SaltAPI
import json
from django.forms.models import model_to_dict


#命令列表
@login_required
def command(request):
    cmd_list=Command.objects.order_by('cmd')
    module_list=Module.objects.order_by('name')
    module_id = request.GET.get('module_id')
    cmd = request.GET.get('cmd')

    if module_id:  #按模块ID过滤
        cmd_list = cmd_list.filter(module=module_id).order_by('cmd')
        if request.is_ajax():
            cmd_list = [cmd.cmd for cmd in cmd_list]
            return JsonResponse(cmd_list,safe=False)
    elif cmd:    #命令帮助信息
        command=Command.objects.get(cmd=cmd)
        return JsonResponse(command.doc.replace("\n","<br>").replace(" ","&nbsp;"),safe=False)
    else:
        cmd_list=cmd_list
    return render(request,'SALT/command.html',locals())
#接口列表
@login_required
def server(request):
    server_list=SaltServer.objects.order_by('ip')
    return render(request, 'SALT/server.html', locals())
#执行命令页面
@login_required
def cmd_run(request):
    system_list = SystemType.objects.order_by('name')
    server_list = Server.objects.order_by('name')
    idc_list = IDC.objects.order_by('name')
    group_list = HostGroup.objects.order_by('name')
    module_list=Module.objects.order_by('name')
    tgt_type_list=TargetType.objects.order_by('name')
    client_type_list=ClientType.objects.order_by('name')
    return render(request,'SALT/cmd_run.html',locals())
#目标过滤
@login_required
def target(request):
    if request.is_ajax():
        if request.method == 'GET':
            tgt=request.GET.get('tgt','')
            idc_id=request.GET.get('idc_id','')
            system_id = request.GET.get('system_id','')
            group_id = request.GET.get('group_id','')
            # print(idc_id,system_id,group_id,hostname)
            host_list = HostDetail.objects.filter(salt_status=True).order_by('tgt_id')
            if tgt:
                if idc_id:
                    if system_id:
                        if group_id:
                            host_list = host_list.filter(tgt_id__icontains=tgt,host__server__idc=idc_id,host__system_type=system_id,host__group=group_id)
                        else:
                            host_list = host_list.filter(tgt_id__icontains=tgt,host__server__idc=idc_id,host__system_type=system_id)
                    elif group_id:
                        host_list = host_list.filter(tgt_id__icontains=tgt,host__server__idc=idc_id,host__group=group_id)
                    else:
                        host_list = host_list.filter(tgt_id__icontains=tgt,host__server__idc=idc_id)
                elif system_id:
                     if group_id:
                         host_list = host_list.filter(tgt_id__icontains=tgt,host__system_type=system_id,host__group=group_id)
                     else:
                         host_list = host_list.filter(tgt_id__icontains=tgt,host__system_type=system_id)
                elif group_id:
                    host_list = host_list.filter(tgt_id__icontains=tgt,host__group=group_id)
                else:
                    host_list = host_list.filter(tgt_id__icontains=tgt)
            elif idc_id:
                if system_id:
                    if group_id:
                        host_list = host_list.filter(host__server__idc=idc_id,host__system_type=system_id,host__group=group_id)
                    else:
                        host_list = host_list.filter(host__server__idc=idc_id,host__system_type=system_id)
                elif group_id:
                    host_list = host_list.filter(host__server__idc=idc_id,host__group=group_id)
                else:
                    host_list = host_list.filter(host__server__idc=idc_id)
            elif system_id:
                 if group_id:
                     host_list = host_list.filter(host__system_type=system_id,host__group=group_id)
                 else:
                     host_list = host_list.filter(host__system_type=system_id)
            elif group_id:
                host_list = host_list.filter(host__group=group_id)

            # print host_list
            host_list = [host.tgt_id for host in host_list]
            return JsonResponse(host_list,safe=False)
#命令结果
@login_required
def cmd_result(request):
    if request.is_ajax():
        if request.method == 'GET':
            idc = request.GET.get('idc')
            tgt_type = request.GET.get('tgt_type')
            # tgt_type = TargetType.objects.get(id=tgt_type_id).name
            tgt  = request.GET.get('tgt')
            # client   = request.GET.get('client')
            # client = ClientType.objects.get(id=client_id).name
            fun = request.GET.get('fun')
            arg = request.GET.get('arg','')
            user  = request.user.username
            # print(idc,tgt_type,tgt,client,fun,arg,user)

            salt_server = SaltServer.objects.get(ip__server__idc=idc) #根据机房ID选择对应salt服务端
            sapi = SaltAPI(url=salt_server.url,username=salt_server.username,password=salt_server.password)
            result = sapi.SaltCmd(tgt=tgt,fun=fun,arg=arg,expr_form=tgt_type)
            # if client == 'local_async':
            jid = result['return'][0]['jid']
            minions = ','.join(result['return'][0]['minions'])
            r=Result(jid=jid,minions=minions,fun=fun,arg=arg,tgt_type=tgt_type,idc_id=idc,user=user)
            r.save()
            res=model_to_dict(r,exclude='result')
            return JsonResponse(res,safe=False)
    else:
        result_list = Result.objects.order_by('-id')
        return render(request,'SALT/cmd_result.html',locals())
#任务信息
@login_required
def jid_info(request):
    jid = request.GET.get('jid','')
    if jid:
        try:
            r = Result.objects.get(jid=jid)
        except Exception as e:
            return e
        if r.result and r.result!='{}' :
            result = json.loads(r.result) #cmd_result.html默认从数据库中读取
        else:
            idc = r.idc_id
            salt_server = SaltServer.objects.get(ip__server__idc=idc)
            sapi = SaltAPI(url=salt_server.url,username=salt_server.username,password=salt_server.password)
            jid_info=sapi.SaltJob(jid)
            result = jid_info['info'][0]['Result']
            print jid_info
            r.result=json.dumps(result)
            r.save()
        return JsonResponse(result,safe=False)
#命令帮助信息
@login_required
def cmd_doc(request):
    salt_server = SaltServer.objects.all()[0] #选择salt接口中的第一个
    cmd_list = Command.objects.filter(doc='') #只对未获取帮助信息的命令操作
    sapi = SaltAPI(url=salt_server.url,username=salt_server.username,password=salt_server.password)
    for cmd in cmd_list:
        result = sapi.SaltCmd(client='local',tgt='*',fun='sys.doc',arg=cmd.cmd) #使用local直接返回结果，不需要异步
        print result
#{u'return': [{u'saltminion01-41.ewp.com': {u'cmd.script': u'\n    Download a script from a remote location and execute the script locally.\n  ...
        try:
            cmd.doc=result['return'][0].values()[0][cmd.cmd]
        #.replace(" ","&nbsp;")
        except:
            cmd.doc=u"这个命令没有帮助信息，请点击模块查看官方网站信息!"
        cmd.save()
    return HttpResponseRedirect(reverse('salt:command'))

