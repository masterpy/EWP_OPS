#coding: utf-8
from django.db import models
from CMDB.models import IDC,Host
# Create your models here.
class SaltServer(models.Model):
    ip = models.OneToOneField(Host,verbose_name=u'所属主机')
    url = models.URLField(max_length=100,verbose_name=u'URL地址')
    username = models.CharField(max_length=50, verbose_name=u'用户名')
    password = models.CharField(max_length=50,verbose_name=u'密码')
    def __unicode__(self):
        return self.url
    class Meta:
        verbose_name = u'Salt服务器'
        verbose_name_plural = u'Salt服务器列表'

#https://docs.saltstack.com/en/latest/ref/modules/all/index.html
class Module(models.Model):
    name = models.CharField(unique=True,max_length=20,verbose_name=u'Salt模块')
    info = models.TextField(max_length=200,verbose_name=u'模块说明')
    url = models.URLField(blank=True,verbose_name=u'官网链接')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u'Salt模块'
        verbose_name_plural = u'Salt模块列表'

class Command(models.Model):
    cmd = models.CharField(unique=True,max_length=40,verbose_name=u'Salt命令')
    module = models.ForeignKey(Module,verbose_name=u'所属模块')
    doc = models.TextField(max_length=500, blank=True,verbose_name=u'帮助文档')
    def __unicode__(self):
        return self.cmd
    class Meta:
        verbose_name = u'Salt命令'
        verbose_name_plural = u'Salt命令列表'


class TargetType(models.Model):
    name = models.CharField(unique=True,max_length=20,verbose_name=u'目标类型')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u'Salt目标类型'
        verbose_name_plural = u'Salt目标类型列表'


class ClientType(models.Model):
    name = models.CharField(unique=True,max_length=20,verbose_name=u'执行方式')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u'Salt执行方式'
        verbose_name_plural = u'Salt执行方式列表'

class Result(models.Model):
    #命令
    client = models.CharField(max_length=20,blank=True,verbose_name=u'执行方式')
    fun = models.CharField(max_length=50,verbose_name=u'命令')
    arg = models.CharField(max_length=255,blank=True,verbose_name=u'参数')
    tgt_type =  models.CharField(max_length=20,verbose_name=u'目标类型')
    #返回
    jid = models.CharField(unique=True,blank=True,max_length=50,verbose_name=u'任务号')
    minions = models.CharField(max_length=500,blank=True,verbose_name=u'目标主机')
    result = models.TextField(blank=True,verbose_name=u'返回结果')
    # success = models.NullBooleanField(blank=True,verbose_name=u'是否成功')
    # full_ret = models.TextField()
    #其他信息
    idc_id = models.IntegerField(verbose_name=u'Salt接口')
    user = models.CharField(max_length=50,verbose_name=u'操作用户')
    datetime =models.DateTimeField(auto_now_add=True,verbose_name=u'执行时间')
    def __unicode__(self):
        return self.jid
    class Meta:
        verbose_name = u'命令返回结果'
        verbose_name_plural = u'命令返回结果'

# class SvnProject(models.Model):
#     name = models.CharField(max_length=50,verbose_name=u'项目名称')
#     host = models.ForeignKey(Host,verbose_name=u'项目主机')
#     local_path = models.CharField(max_length=200,verbose_name=u'项目路径')
#     url = models.CharField(max_length=200,verbose_name=u'SVN地址')
#     username = models.CharField(max_length=40,verbose_name=u'SVN账号')
#     password = models.CharField(max_length=40,verbose_name=u'SVN密码')
#     info = models.CharField(max_length=100,blank=True,verbose_name=u'备注信息')
#     def __unicode__(self):
#         return self.name
#     class Meta:
#         verbose_name = u'SVN项目'
#         verbose_name_plural = u'SVN项目列表'

class Upload(models.Model):
    username = models.CharField(max_length = 30,verbose_name=u'用户')
    headImg = models.FileField(upload_to = './media/',verbose_name=u'文件路径')
    date = models.DateTimeField(auto_now_add=True,verbose_name=u'上传时间')
    #存放的并非用户上传的文件本身，而是文件的存放路径。
    def __unicode__(self):
        return self.headImg
    class Meta:
        verbose_name = u'文件上传'
        verbose_name_plural = u'文件上传'