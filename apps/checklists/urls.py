from django.urls import path, include
from . import views

app_name = 'checklists'
urlpatterns = [
    path('show_deslist', views.show_deslist, name='show_deslist'),
    path('top', views.graphlist, name='top'),
    path('second', views.second_list, name='second'),
    path("exec_ajax", views.exec_ajax, name='exec_ajax'),
    path("swal_ajax", views.swal_ajax, name='swal_ajax'),
    path('action_supinfo_show', views.action_supinfo_show, name = 'action_supinfo_show'),
    path('add_LLD', views.add_LLD, name='add_LLD'),
    path('show_pastLLD', views.show_pastLLD, name='show_pastLLD'),
    path('edit_action', views.edit_action, name='edit_action'),
    path('add_action', views.add_action, name='add_action'),
    path('hello', views.hello, name='hello'),
    path('loop_add', views.loop_add, name='loop_add'),
    path('get_nextaction', views.get_nextaction, name='get_nextaction'),
]
