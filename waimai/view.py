# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import time
from django.contrib import auth
from waimai.utils.get_menu import get_menu_by_id
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required()
def hello(request):
    context = {}
    context['hello'] = request.user.is_authenticated()
    context['is_login'] = request.user.is_authenticated()
    context['username'] = request.user.username
    return render(request, 'menu.html', context)

def admin(request):
    request.encoding = 'utf-8'
    if 'q' in request.GET:
        message = '你搜索的内容为: ' + request.GET['q']
        items = get_menu_by_id(request.GET['q'])
        context = {}
        context['shop1'] = items
        context['hello'] = 'Hello World!'
        return render(request, 'menu.html', context)
    else:
        return render(request, 'admin.html')

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

def logout(req):
    auth.logout(req)
    return HttpResponseRedirect("/menu")