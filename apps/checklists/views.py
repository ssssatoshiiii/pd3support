from django.http import HttpResponse,JsonResponse
from django.template import loader
from django.shortcuts import render
from . import sparql
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import os
import sys
import time

@login_required
def graphlist(request):
    context = dict()
    actions, actions_uri = sparql.get_graph()
    context['actions']= actions
    context['actions_uri']=actions_uri


    # checked_AM = [1,3]
    # context['checked_AM'] = checked_AM

    contents_anytime = list()
    contents_anytime.append('t')
    context['contents_anytime']=contents_anytime

    #過去事例の参照の際に使いそう、過去事例の参照可能なアクションを表示
    contents_AM_id = [1,2,4]
    context['contents_AM_id'] =contents_AM_id

    if request.method == 'GET':
        uri = request.GET.get("uri")
        added_action = request.GET.get("added_action")
        above_below = request.GET.get("above_below")
        if(uri != None and "above" in request.GET):
            index = context['actions_uri'].index(uri)
            context['actions_uri'].insert(index, uri + str(time.time))
            context['actions'].insert(index, added_action)
        elif(uri!= None and "below" in request.GET):
            index = context['actions_uri'].index(uri) + 1
            context['actions_uri'].insert(index, uri + str(time.time))
            context['actions'].insert(index, added_action)



    return render(request, os.getcwd()+'/templates/checklists/main.html', context)




def exec_ajax(request):
    """
        組長チェックボード初回レンダリング：

        Parameters
        ----------
        request:
        ..../checklists/へのアクセス時のGETリクエスト

        return
        ----------
        os.getcwd()+'/templates/checklists/main.html'
        テンプレート
        context
        初期表示に必要な情報が格納された辞書型配列
    """
    if request.method == 'GET':  # GETの処理
        print("get_request")

        param = request.GET.get("value")  # GETパラメータ
        value_list = str(param).split('_')
        index = int(value_list[0])
        contents_id = value_list[1].strip('][').split(', ')
        custom_execution_contents_id = int(contents_id[index])
        # records = DAO.DAO().method.is_be_completed_update(
        #     DAO.DAO().session, DAO.DAO().LstAchievements, custom_execution_contents_id)
        records = 'data2'

        return HttpResponse(records)

    elif request.method == 'POST':  # POSTの処理
        print("post_request")
        param = request.POST.get("value")  # POSTパラメータ
        value_list = str(param).split('_')
        index = int(value_list[0])
        contents_id = value_list[1].strip('][').split(', ')
        custom_execution_contents_id = int(contents_id[index])

        # records = DAO.DAO().method.is_be_completed_update(DAO.DAO().session,
        #                                                   DAO.DAO().LstAchievements, custom_execution_contents_id)
        return HttpResponse('data1')

def swal_ajax(request):
    """
        ヘルプボタンクリック時のajax通信用関数：

        Parameters
        ----------
        request:
        popup(id_value)クリック時のリクエスト
        id_value = {value:id_value}

        return
        ----------
        result:dict
        ヘルプの中に記載の情報が格納された辞書型配列
    """
    if request.method == 'GET':  # GETの処理
        print("get_request")
        param = request.GET.get("value")  # GETパラメータ
        return HttpResponse(param)

    elif request.method == 'POST':  # POSTの処理
        print("post_request")
        action = request.POST.get("action")  # POSTパラメータ
        uri = request.POST.get("uri")

        reference_list = []

        references = 'あいうえお'
        # for i in reference_list:
        #     if not i == None:
        #         references = references + '<a href = "'+i + \
        #             '" target = "_blank" rel = "noopener noreferrer" > 関連-URL&nbsp;:&nbsp;' + \
        #             i+'</a >&nbsp;&nbsp;'
        result = dict()
        result["title"] = action
        result["detail"] = "detail"
        result["references"] = references

        return JsonResponse(result)

def second_graph_list(request):
    if request.method == 'POST' :
        uri = request.POST.get('uri')
        actions, actions_uri = sparql.get_detail_action(uri)
        context = dict()
        context['actions'] =actions
        context['actions_uri'] = actions_uri

        #アクションの表の数を代入
        action_list_number = request.POST.get('action_list_number')
        context['action_list_number'] = int(action_list_number) +1

        return render(request, os.getcwd()+'/templates/checklists/sub.html', context)

def action_supinfo_show(request):
    if request.method == 'POST':
        uri = request.POST.get('uri')
        action = request.POST.get('action')
        context = dict()
        context['intention'], context['toolknowledge'], context['annotation'] = sparql.action_supinfo(uri)
        context['action'] = action

        return render(request, os.getcwd()+'/templates/checklists/action_supinfo.html', context)

# Create your views here.
