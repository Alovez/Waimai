# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import time
from django.contrib import auth
from waimai.utils.get_menu import get_menu_by_id, get_menu_from_db, get_shop, get_shop_table,change_shop_table
from waimai.utils.get_order import add_cart, get_cart, get_order, remove_order
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from waimai.constants import WeekDay

@login_required()
def hello(request):
    context = {}
    if 'dish' in request.GET and request.user.username != 'admin':
        dish = request.GET['dish']
        shop_id = request.GET['shop']
        add_cart(request.user.username, dish, shop_id)
        context['dish'] = dish
    context['hello'] = WeekDay[datetime.today().weekday()]
    context['username'] = request.user.username
    context['is_admin'] = (request.user.username == 'admin')
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

# bH1&5C
@login_required()
def admin(request):
    if request.user.username != 'admin':
        return HttpResponseRedirect('/menu')
    request.encoding = 'utf-8'
    is_get = False
    for i in range(1, 4):
        if 'shop%s' % i in request.GET:
            if 'is_%s_mobile' % i in request.GET and request.GET['is_%s_mobile' % i] == 'on':
                get_menu_by_id.delay(i, request.GET['shop%s' % i], is_mobile=True)
            else:
                get_menu_by_id.delay(i, request.GET['shop%s' % i])
            is_get = True
    if is_get:
        return HttpResponseRedirect('/menu')
    else:
        context = {}
        context['username'] = request.user.username
        return render(request, 'admin.html', context)

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
            if username == 'admin':
                return HttpResponseRedirect("/shop_admin")
            return HttpResponseRedirect("/menu")
        else:
            context = {}
            context['login_result'] = '用户名或密码错误'
            return render(req, 'login.html', context)
    else:
        return render(req, 'login.html')

@login_required()
def change(req):
    context = {}
    if req.method == 'POST':
        password = req.POST['password']
        password_re = req.POST['password_re']
        if password == password_re:
            c_user =  req.user
            c_user.set_password(password)
            c_user.save()
            return HttpResponseRedirect('/menu')
        else:
            context['change_result'] = '两次输入的密码不一致'
            return render(req, 'change.html', context)
    return render(req, 'change.html')

def logout(req):
    auth.logout(req)
    return HttpResponseRedirect("/menu")

@login_required()
def cart(req):
    if 'dish' in req.GET:
        remove_order(req.user.username, req.GET['dish'], req.GET['shop'])
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
    context['hello'] = '今天的点单如下'
    shop1 = get_order(1)
    context['shop1'] = shop1
    print(shop1)
    context['shop1_name'] = get_shop(1)
    context['shop2_name'] = get_shop(2)
    context['shop3_name'] = get_shop(3)
    shop2 = get_order(2)
    context['shop2'] = shop2
    shop3 = get_order(3)
    context['shop3'] = shop3
    return render(request, 'summary.html', context)

@login_required()
def reset(request):
    if request.user.username == 'admin':
        if 'c_user' in request.GET:
            C_User = User.objects.get(username=request.GET['c_user'])
            C_User.set_password('Digibird2009')
            C_User.save()
            context = {'c_user': request.GET['c_user']}
            context['username'] = request.user.username
            return render(request, 'reset.html', context)
        else:
            context = {}
            context['username'] = request.user.username
            return render(request, 'reset.html', context)
    else:
        return HttpResponseRedirect('/menu')

@login_required()
def shop_admin(request):
    if request.user.username == 'admin':
        shop_list = get_shop_table()
        context = {}
        context['shop_list'] = shop_list
        print('*' * 10)
        print(shop_list)
        context['username'] = request.user.username
        return render(request, 'shop_admin.html', context)
    else:
        return HttpResponseRedirect('/menu')

@login_required()
def change_shop(request):
    if request.user.username == 'admin':
        if 'shop_id' in request.GET:
            if 'is_mobile' in request.GET:
                is_mobile = '手机抓取'
            else:
                is_mobile = '网页抓取'
            change_shop_table(request.GET['weekday'], request.GET['shop_num'], request.GET['shop_id'], is_mobile)
            return HttpResponseRedirect('/shop_admin')
        elif 'weekday' in request.GET:
            context = {}
            context['weekday'] = WeekDay.index(request.GET['weekday'])
            context['shop_num'] = request.GET['shop_num']
            context['username'] = request.user.username
            return  render(request, 'change_shop.html', context)
        else:
            return HttpResponseRedirect('/menu')
    else:
        return HttpResponseRedirect('/menu')