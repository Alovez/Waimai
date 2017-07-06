#coding=utf-8
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import auth


#注册
def regist(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        email = req.POST['email']
        #添加到数据库
        filterResult = User.objects.filter(username=username)
        if len(filterResult) > 0:
            result = {}
            result['unr'] = '用户名已存在！'
            return render(req, 'regist.html', context=result)
        user = User()
        user.username = username
        user.set_password(password)
        user.email = email
        user.save()
        return render(req, 'login.html')
    return render(req, 'regist.html')

#登陆
def login(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        newUser = auth.authenticate(username=username, password=password)
        if newUser is not None:
            auth.login(req, newUser)
            return HttpResponseRedirect("/menu")
    else:
        return render(req, 'login.html')

#登陆成功
def index(req):
    username = req.COOKIES.get('username','')
    return render_to_response('index.html' ,{'username':username})

#退出
def logout(req):
    response = HttpResponse('logout !!')
    #清理cookie里保存username
    response.delete_cookie('username')
    return response