"""waimai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from . import view
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^$', view.hello),
    url(r'menu', view.hello),
    url(r'^admin', view.admin),
    url(r'^login/$', view.login),
    url(r'^regist/$', view.regist),
    url(r'^logout/$', view.logout),
    url(r'^cart/$', view.cart),
    url(r'^summary/$',view.summary),
    url(r'^reset/$', view.reset),
    url(r'^change/$', view.change),
    url(r'^shop_admin/$', view.shop_admin),
    url(r'^change_shop/$', view.change_shop),
    url(r'^submit_order', view.submit_order),
    url(r'^summary_custom', view.summary_custom)
]

# TODO: 尝试自动下单
# TODO: 增加最近三个点单及最热门点单
