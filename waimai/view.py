# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import time
from django.contrib import auth
from waimai.utils.get_menu import get_menu_by_id, get_menu_from_db
from waimai.utils.get_order import add_cart, get_cart
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from waimai.constants import WeekDay

@login_required()
def hello(request):
    if 'dish' in request.GET:
        dish = request.GET['dish']
        add_cart(request.user.username, dish)
    context = {}
    context['hello'] = WeekDay[datetime.today().weekday()]
    context['is_login'] = request.user.is_authenticated()
    context['username'] = request.user.username
    shop1 = get_menu_from_db(1)
    shop2 = get_menu_from_db(2)
    shop3 = get_menu_from_db(3)
    context['shop1'] = shop1
    context['shop2'] = shop2
    context['shop3'] = shop3
    context['shop1_name'] = shop1[0][2]
    context['shop2_name'] = shop2[0][2]
    context['shop3_name'] = shop3[0][2]
    return render(request, 'menu.html', context)

@login_required()
def admin(request):
    if request.user.username != 'admin':
        return HttpResponseRedirect('/menu')
    request.encoding = 'utf-8'
    is_get = False
    if 'shop1' in request.GET:
        get_menu_by_id(1, request.GET['shop1'])
        is_get = True
    if 'shop2' in request.GET:
        get_menu_by_id(2, request.GET['shop2'])
        is_get = True
    if 'shop3' in request.GET:
        get_menu_by_id(3, request.GET['shop3'])
        is_get = True
    if is_get:
        return HttpResponseRedirect('/menu')
    else:
        return render(request, 'admin.html')

#注册
def regist(req):
    if req.user.is_authenticated():
        return HttpResponseRedirect('/menu')
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        password_re = req.POST['password_re']
        email = req.POST['email']
        #添加到数据库
        filterResult = User.objects.filter(username=username)
        if len(filterResult) > 0:
            result = {}
            result['unr'] = '用户名已存在！'
            return render(req, 'regist.html', context=result)
        if password != password_re:
            result = {'unr': '两次输入的密码不一致'}
            return render(req, 'regist.html', result)
        user = User()
        user.username = username
        user.set_password(password)
        user.email = email
        user.save()
        return render(req, 'login.html')
    return render(req, 'regist.html')

#登陆
def login(req):
    if req.user.is_authenticated():
        return HttpResponseRedirect('/menu')
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

@login_required()
def cart(req):
    dishes = get_cart(req.user.username)
    context = {}
    context['dishes'] = dishes
    return render(req, 'cart.html', context)

@login_required()
def summary(request):
    if request.user.username != 'admin':
        return HttpResponseRedirect('/menu')
    context = {}
    context['is_login'] = request.user.is_authenticated()
    context['username'] = request.user.username

    return render(request, 'summary.html', context)