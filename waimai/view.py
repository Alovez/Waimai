# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import time
from django.contrib import auth
from waimai.utils.get_menu import get_menu_by_id, get_menu_from_db
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required()
def hello(request):
    context = {}
    context['hello'] = request.user.is_authenticated()
    context['is_login'] = request.user.is_authenticated()
    context['username'] = request.user.username
    shop = get_menu_from_db(1)
    context['shop1'] = shop
    context['shop1_name'] = shop[0][2]
    return render(request, 'menu.html', context)

def admin(request):
    request.encoding = 'utf-8'
    if 'q' in request.GET:
        get_menu_by_id(request.GET['q'])
        context = {}
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
            context = {}
            context['login_result'] = '用户名或密码错误'
            return render(req, 'login.html', context)
    else:
        return render(req, 'login.html')

def logout(req):
    auth.logout(req)
    return HttpResponseRedirect("/menu")