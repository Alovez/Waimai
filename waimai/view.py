# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import time
from waimai.utils.get_menu import get_menu_by_id

def hello(request):
    context = {}
    context['hello'] = 'Hello World!'
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