from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^api/tutorials$', views.tutorial_list),

    url(r'^login/(?P<username>[0-9|a-zA-Z]+)/(?P<password>[0-9|a-zA-Z]+)$', views.login),
    url(r'^logout/(?P<user_id>[0-9|a-z]+)$', views.logout),
    url(r'^register$', views.register),
    url(r'^game/delete_account/(?P<user_id>[0-9|a-z]+)$', views.delete_account),
    url(r'^game/change_user_data/(?P<user_id>[0-9|a-z]+)$', views.change_user_data),

    url(r'^game/get_news/(?P<user_id>[0-9|a-z]+)$', views.get_news),
    url(r'^game/feedback/(?P<user_id>[0-9|a-z]+)$', views.redirect_feedback),

    url(r'^game/(?P<user_id>[0-9|a-z]+)$', views.get_all),
    url(r'^game/change_taxes/(?P<user_id>[0-9|a-z]+)$', views.change_taxes),
    url(r'^game/upgrade_technology/(?P<user_id>[0-9|a-z]+)$', views.upgrade_technology),
    url(r'^game/build_industry/(?P<user_id>[0-9|a-z]+)$', views.build_industry),
    url(r'^game/remove_industry/(?P<user_id>[0-9|a-z]+)$', views.remove_industry),
    url(r'^game/upgrade_warehouse/(?P<user_id>[0-9|a-z]+)$', views.upgrade_warehouse),
    url(r'^game/set_law/(?P<user_id>[0-9|a-z]+)$', views.set_law),
    url(r'^game/cancel_law/(?P<user_id>[0-9|a-z]+)$', views.cancel_law),
    url(r'^game/buy_goods/(?P<user_id>[0-9|a-z]+)$', views.buy_goods),
    url(r'^game/sell_goods/(?P<user_id>[0-9|a-z]+)$', views.sell_goods),
    url(r'^game/edit_army/(?P<user_id>[0-9|a-z]+)$', views.edit_army),
    url(r'^game/calculate_war/(?P<user_id>[0-9|a-z]+)/(?P<defending_player_id>[0-9|a-z]+)$', views.calculate_war),
]