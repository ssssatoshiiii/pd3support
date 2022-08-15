from django.http import HttpResponse,JsonResponse
from django.template import loader
from django.shortcuts import render
from . import sparql
from . import sparql_update
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import os
import sys
import time
from .models import Graph

@login_required
def show_deslist(request):

    #GPMのグラフのURIとGPMの記述のURIは共通
    context = dict()
    context['GPM_graphs'], context['GPM_descriptions_uri'], context['GPM_titles'] = sparql.get_deslist("GPM")
    context['LLD_graphs'], context['LLD_descriptions_uri'], context['LLD_titles'] = sparql.get_deslist("LLD")

    #新規の記述の登録操作があった場合、ここでfusekiに追加する
    if(request.method == 'POST'):
        print(request.POST.get('added_lld_title'))
        added_lld_title = request.POST.get('added_lld_title')
        if(not added_lld_title in context['LLD_titles']):
            sparql_update.add_LLDgraph_tofuseki(added_lld_title)
            context['LLD_graphs'], context['LLD_descriptions_uri'], context['LLD_titles'] = sparql.get_deslist("LLD")

    return render(request, os.getcwd()+'/templates/checklists/show_deslist.html', context)


@login_required
def graphlist(request):

    gpm_graph_uri = request.POST.get('gpm_graph_uri')
    print(gpm_graph_uri)
    lld_graph_uri = request.POST.get('lld_graph_uri')
    print(lld_graph_uri)

    context = dict()
    context['gpm_graph_uri'] = gpm_graph_uri
    context['lld_graph_uri'] = lld_graph_uri
    actions, actions_uri = sparql.get_graph(gpm_graph_uri)
    context['alllayer_actions'] = []
    context['alllayer_actions'].append(actions)
    context['alllayer_actions_uri']=[]
    context['alllayer_actions_uri'].append(actions_uri)


    # checked_AM = [1,3]
    # context['checked_AM'] = checked_AM

    contents_anytime = list()
    contents_anytime.append('t')
    context['contents_anytime']=contents_anytime

    #過去事例の参照の際に使いそう、過去事例の参照可能なアクションを表示
    contents_AM_id = [1,2,4]
    context['contents_AM_id'] =contents_AM_id


    if request.method == 'POST':
        if "action_uri" in request.POST:
            #アクションを獲得したら、そのアクションから順番に一番上の層まで遡り、アクションを入手する
            uri = request.POST.get("action_uri")
            hier_actions = sparql.get_hier_actions(uri, gpm_graph_uri)

            #各層の上のアクションから、それを展開したコンテナのアクション列を順番に表示
            for each_action in hier_actions:
                print('hiera')
                print(each_action)
                actions, actions_uri = sparql.get_detail_action(each_action, gpm_graph_uri)
                context['alllayer_actions'].append(actions)
                context['alllayer_actions_uri'].append(actions_uri)

        if "added_action" in request.POST:
            uri = request.POST.get("uri")
            added_action = request.POST.get("added_action")
            print(added_action)
            above_below = request.POST.get("above_below")
            for actions_uri in context['alllayer_actions_uri']:
                if(uri in actions_uri):
                    if("above" in request.POST):
                        index = actions_uri.index(uri)
                    elif("below" in request.POST):
                        index = actions_uri.index(uri) + 1
                    actions_uri.insert(index, uri+str(time.time))
                    actions.insert(index, added_action)

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

# def second_graph_list(request):
#     if request.method == 'POST' :
#         uri = request.POST.get('uri')
#         actions, actions_uri = sparql.get_detail_action(uri)
#         context = dict()
#         context['actions'] =actions
#         context['actions_uri'] = actions_uri

#         #アクションの表の数を代入
#         action_list_number = request.POST.get('action_list_number')
#         context['action_list_number'] = int(action_list_number) +1

#         if request.method == 'GET':
#             print('yes')
#             uri = request.GET.get("uri")
#             added_action = request.GET.get("added_action")
#             above_below = request.GET.get("above_below")
#             if(uri != None and "above" in request.GET):
#                 index = context['actions_uri'].index(uri)
#                 context['actions_uri'].insert(index, uri + str(time.time))
#                 context['actions'].insert(index, added_action)
#             elif(uri!= None and "below" in request.GET):
#                 index = context['actions_uri'].index(uri) + 1
#                 context['actions_uri'].insert(index, uri + str(time.time))
#                 context['actions'].insert(index, added_action)

#         return render(request, os.getcwd()+'/templates/checklists/sub.html', context)

def action_supinfo_show(request):
    if request.method == 'POST':
        context = dict()

        #GPMのsupinfoの情報の取得
        #actionのURI
        uri = request.POST.get('uri')
        #actionのvalue
        action = request.POST.get('action')
        gpm_graph_uri = request.POST.get('gpm_graph_uri')
        context['gpm_graph_uri'] = gpm_graph_uri
        lld_graph_uri = request.POST.get('lld_graph_uri')
        context['lld_graph_uri'] = lld_graph_uri

        context['intention'], context['toolknowledge'], context['annotation'], context['output']= sparql.action_supinfo(uri, gpm_graph_uri)
        context['action'] = action
        context['uri'] = uri

        #記入したLLDのsupinfoの情報の取得
        #isUsedByのアクションの取得
        lld_actions_uri, lld_actions_value = sparql.get_lld_action(uri, gpm_graph_uri)
        context['lld_actions'] = []
        for i in range(len(lld_actions_uri)):
            context['lld_actions'].append([lld_actions_uri[i], lld_actions_value[i]])
  

        for i in range(len(lld_actions_uri)):
            print('test1')
            print(lld_graph_uri)
            lld_intention, lld_toolknowledge, lld_annotation, lld_output = sparql.action_supinfo(lld_actions_uri[i], lld_graph_uri)
            print(lld_intention)
            context['lld_actions'][i].append(lld_intention)
            context['lld_actions'][i].append(lld_toolknowledge)
            context['lld_actions'][i].append(lld_annotation)
            context['lld_actions'][i].append(lld_output)
        print('test')
        print(context['lld_actions'])

        return render(request, os.getcwd()+'/templates/checklists/action_supinfo.html', context)

def add_LLD(request):
    if request.method == 'POST':
        
        action_uri = request.POST.get('uri')
        gpm_graph_uri = request.POST.get('gpm_graph_uri')
        lld_graph_uri = request.POST.get('lld_graph_uri')

        action = request.POST.get('action')
        intention = request.POST.get('intention')
        toolknowledge = request.POST.get('toolknowledge')
        annotation = request.POST.get('annotation')
        output = request.POST.get('output')

        sparql_update.add_LLD_tofuseki(action_uri, action, intention, toolknowledge, annotation, output, gpm_graph_uri, lld_graph_uri)

    return HttpResponse('登録しました！')
# Create your views here.

def show_pastLLD(request):
    context = {}
    action = request.POST.get('action')
    print(action)
    context['action'] = action 

    return render(request, os.getcwd()+'/templates/checklists/show_pastLLD.html', context)