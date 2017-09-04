# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
import time
from django.contrib import auth
from waimai.utils.get_menu import get_menu_by_id, get_menu_from_db, get_shop, get_shop_table, change_shop_table
from waimai.utils.get_order import add_cart, get_cart, get_order, remove_order, get_order_by_name_date, add_comment, \
    get_comment
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from waimai.constants import WeekDay
from django.conf import settings
from django.http import JsonResponse
import json
import os
import csv
from waimai.settings import OPEN_TIME
from django.views.decorators.csrf import csrf_exempt


@login_required()
def hello(request):
    context = {}
    # if 'dish' in request.GET and request.user.username != 'admin':
    #     dish = request.GET['dish']
    #     add_cart(request.user.username, dish)
    #     context['dish'] = dish
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
    context['shop_list'] = [shop1, shop2, shop3]
    if request.user.username != 'admin':
        if time.strftime("%H-%M", time.localtime(time.time())) < OPEN_TIME:
            return render(request, 'Wait.html')
    return render(request, 'menu.html', context)


@csrf_exempt
def submit_order(request):
    if request.method == 'POST' and request.user.username != 'admin':
        for item in request.POST:
            for i in range(int(request.POST[item])):
                add_cart(request.user.username, item[1:])
    return HttpResponseRedirect('/menu')


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


# 注册
def regist(req):
    if req.user.is_authenticated():
        return HttpResponseRedirect('/menu')
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        password_re = req.POST['password_re']
        email = req.POST['email']
        # 添加到数据库
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


# 登陆
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
            c_user = req.user
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
    comment_flag = 'comment' in req.GET and req.GET.get('comment') != ''
    dish_id_flag = 'dish_id' in req.GET and 'shop' in req.GET
    if dish_id_flag and not comment_flag:
        remove_order(req.user.username, req.GET['dish_id'], req.GET['shop'])
    elif comment_flag:
        add_comment(req.user.username, req.GET.get('dish_id'), req.GET.get('comment'))
        print(req.GET.get('comment'))
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
    context['shop1_name'] = get_shop(1)
    context['shop2_name'] = get_shop(2)
    context['shop3_name'] = get_shop(3)
    shop2 = get_order(2)
    context['shop2'] = shop2
    shop3 = get_order(3)
    context['shop3'] = shop3
    context['comments'] = get_comment()
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
            return render(request, 'change_shop.html', context)
        else:
            return HttpResponseRedirect('/menu')
    else:
        return HttpResponseRedirect('/menu')


@login_required()
def summary_custom(request):
    context = {}
    context['hello'] = '按日期查询点餐记录'
    return render(request, 'summary_month.html', context)


@csrf_exempt
def ajax_summary(request):
    print('get ajax call')
    if request.method == 'POST':
        start_date = request.POST['start']
        end_date = request.POST['end']
        if 'user' in request.POST:
            user = request.POST['user']
        else:
            user = 'all'
        summary_data = get_order_by_name_date(user, start_date, end_date)
        result = summary_data
    else:
        result = [['无点餐记录', '或无此用户']]
    if not len(result):
        result = [['无点餐记录或无此用户', 'N/A']]
    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type='application/json')


@login_required()
def user_upload(request):
    if request.user.username == 'admin':
        context = {}
        context['username'] = request.user.username
        if request.method == "POST":  # 请求方法为POST时，进行处理
            user_csv = request.FILES.get("user_cvs", None)  # 获取上传的文件，如果没有文件，则默认为None
            if not user_csv:
                context['result'] = '没有选取需要上传的文件'
            else:
                destination = open(os.path.join("./", user_csv.name), 'wb+')  # 打开特定的文件进行二进制的写操作
                for chunk in user_csv.chunks():  # 分块写入文件
                    destination.write(chunk)
                destination.close()
                error_list = []
                with open(os.path.join("./", user_csv.name), 'r', encoding='UTF-8') as f:
                    reader = csv.reader(f)
                    try:
                        for row in reader:
                            username = row[0].encode('utf-8').decode('utf-8-sig')
                            email = row[1]
                            filterResult = User.objects.filter(username=username)
                            if len(filterResult) > 0:
                                error_list.append([username, '用户名已存在'])
                                continue
                            filterResult = User.objects.filter(email=email)
                            if len(filterResult) > 0:
                                error_list.append([username, '邮箱已存在'])
                                continue
                            user = User()
                            user.username = username
                            user.set_password('Digibird2009')
                            user.email = email
                            user.save()
                        print(error_list)
                        context['result'] = '上传成功'
                        context['error_list'] = error_list
                    except csv.Error as e:
                        context['result'] = '文件错误： %s' % e
        return render(request, 'upload_user.html', context)
    else:
        return HttpResponseRedirect('/menu')
