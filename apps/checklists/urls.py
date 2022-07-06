from django.urls import path, include
from . import views

app_name = 'checklists'
urlpatterns = [
    path('top', views.graphlist, name='top'),
    path("exec_ajax", views.exec_ajax, name='exec_ajax'),
    path("swal_ajax", views.swal_ajax, name='swal_ajax'),
    path('second_graph_list', views.second_graph_list, name='second_graph_list'),
    path('action_supinfo_show', views.action_supinfo_show, name = 'action_supinfo_show'),
]
