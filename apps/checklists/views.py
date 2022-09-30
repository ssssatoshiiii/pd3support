from http.client import HTTPResponse
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
    context['GPM_graphs'], context['GPM_titles'] = sparql.get_deslist("GPM")
    context['LLD_graphs']=[]
    context['LLD_descriptions_uri']=[]
    context['LLD_titles']=[]
    

    #新規の記述の登録操作があった場合、ここでfusekiに追加する
    if(request.method == 'POST'):
        if "selected_GPM_graph" in request.POST:
            context['selected_GPM_title']=request.POST.get('selected_GPM_title')
            selected_GPM_graph = request.POST.get('selected_GPM_graph')
            context['selected_GPM_graph']=selected_GPM_graph
            
            if "added_lld_title" in request.POST:
                added_lld_title = request.POST.get('added_lld_title')
                sparql_update.add_LLDgraph_tofuseki(added_lld_title, selected_GPM_graph)
            
            context['LLD_graphs'], LLD_title = sparql.get_lld_list(selected_GPM_graph)
            context['LLD_titles'] = LLD_title

    return render(request, os.getcwd()+'/templates/checklists/show_deslist.html', context)


@login_required
def graphlist(request):

    gpm_graph_uri = request.POST.get('gpm_graph_uri')
    lld_graph_uri = request.POST.get('lld_graph_uri')
    print(gpm_graph_uri, lld_graph_uri)

    if request.method == 'POST':
        if "added_action" in request.POST and "action_uri" in request.POST:
            added_action = request.POST.get("added_action")
            action_uri = request.POST.get("action_uri")

            if("above" in request.POST):
                print("above")
                sparql_update.add_LLDaction_tofuseki(added_action, action_uri, lld_graph_uri, "above")
            elif("below" in request.POST):
                print("below")
                sparql_update.add_LLDaction_tofuseki(added_action, action_uri, lld_graph_uri, "below")
            print(added_action)

    context = dict()
    context['gpm_graph_uri'] = gpm_graph_uri
    context['lld_graph_uri'] = lld_graph_uri
    actions, actions_uri = sparql.get_graph(lld_graph_uri)
    print(actions)
    print(actions_uri)
    context['alllayer_actions'] = []
    context['alllayer_actions'].append(actions)
    context['alllayer_actions_uri']=[]
    context['alllayer_actions_uri'].append(actions_uri)

    checklist =[]
    for i in range(len(actions_uri)):
        if(sparql.get_done_action(actions_uri[i], lld_graph_uri) == "done"):
            checklist.append(i)

    contents_anytime = list()
    contents_anytime.append('t')
    context['contents_anytime']=contents_anytime

    #過去事例の参照の際に使いそう、過去事例の参照可能なアクションを表示
    contents_AM_id = [1,2,4]
    context['contents_AM_id'] =contents_AM_id

    context['checklist']=checklist

    #今は使っていない、コンテナの展開をajaxにしたため、使わなくなった
    # if request.method == 'POST' :
    #     if "action_uri" in request.POST:
    #         #アクションを獲得したら、そのアクションから順番に一番上の層まで遡り、アクションを入手する
    #         uri = request.POST.get("action_uri")
    #         hier_actions = sparql.get_hier_actions(uri, lld_graph_uri)
    #         #hier_actionsをハイライトするため
    #         context['alllayer_hier_actions_uri'] = hier_actions
    #         print(hier_actions)

    #         #各層の上のアクションから、それを展開したコンテナのアクション列を順番に表示
    #         for each_action in hier_actions:
    #             actions, actions_uri = sparql.get_detail_action(each_action, lld_graph_uri)
    #             if(len(actions)!= 0):
    #                 context['alllayer_actions'].append(actions)
    #                 context['alllayer_actions_uri'].append(actions_uri)

    return render(request, os.getcwd()+'/templates/checklists/main.html', context)

def second_list(request):
    if request.method == 'POST' :
        print('test')
        print(request.POST)
        if "action_uri" in request.POST:
            print('test1')
            context = dict()
            context['alllayer_actions'] = []
            context['alllayer_actions_uri'] = []
            context['alllayer_layertype'] = []
            context['checklist'] = []
            #アクションを獲得したら、そのアクションから順番に一番上の層まで遡り、アクションを入手する
            lld_graph_uri = request.POST.get("lld_graph_uri")
            gpm_graph_uri = request.POST.get("gpm_graph_uri")
            context['lld_graph_uri'] = lld_graph_uri
            context['gpm_graph_uri'] = gpm_graph_uri

            uri = request.POST.get("action_uri")
            hier_actions = sparql.get_hier_actions(uri, lld_graph_uri)
            #hier_actionsをハイライトするため
            context['alllayer_hier_actions_uri'] = hier_actions
            print('hier')
            print(hier_actions)


            response = request.POST.get("response")
            if(response=="http"):

                #各層の上のアクションから、それを展開したコンテナのアクション列を順番に表示
                for each_action in hier_actions:
                    actions, actions_uri = sparql.get_detail_action(each_action, lld_graph_uri)
                    checklist =[]
                    for i in range(len(actions_uri)):
                        if(sparql.get_done_action(actions_uri[i], lld_graph_uri) == "done"):
                            checklist.append(i)
                    
                    if(len(actions)!= 0):
                        #layerを取得
                        layertype = sparql.get_action_layer(actions_uri[0], lld_graph_uri)
                        context['alllayer_layertype'].append(layertype)

                        context['alllayer_actions'].append(actions)
                        context['alllayer_actions_uri'].append(actions_uri)
                        print('check')
                        print(checklist)
                        context['checklist'].append(checklist)
                
                return render(request, os.getcwd()+'/templates/checklists/sub.html', context)
            elif(response=="json"):
                result = dict()
                result['hier_actions'] = hier_actions
                return JsonResponse(result)

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
        print(param)
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

def action_supinfo_show(request):
    if request.method == 'POST':
        context = dict()

        #GPMのsupinfoの情報の取得
        #元となるLLDのactionのURI
        action_uri = request.POST.get('action_uri')
        gpm_graph_uri = request.POST.get('gpm_graph_uri')
        context['action_uri'] = action_uri

        context['gpm_graph_uri'] = gpm_graph_uri
        lld_graph_uri = request.POST.get('lld_graph_uri')

        context['lld_graph_uri'] = lld_graph_uri
        gpm_action_uri = sparql.get_gpm_action(action_uri, gpm_graph_uri)

        #GPMのsupinfoの情報取得
        if(gpm_action_uri != ''):
            gpm_action, gpm_intention, gpm_toolknowledge, gpm_annotation, gpm_rationale, gpm_output = sparql.action_supinfo(gpm_action_uri, gpm_graph_uri)
            context['gpm_action'] = gpm_action['action_value']
            context['gpm_intention'] = gpm_intention['intention_value']
            context['gpm_toolknowledge'] = gpm_toolknowledge['toolknowledge_value']
            context['gpm_annotation'] = gpm_annotation['annotation_value']
            context['gpm_rationale'] = gpm_rationale['rationale_value'] 
            context['gpm_output'] = gpm_output['output_value']

        option = request.POST.get('option')
        print(option)
        if(option == "LLD"):
            #記入したLLDのsupinfoの情報の取得
            lld_action, lld_intention, lld_toolknowledge, lld_annotation, lld_rationale, lld_output = sparql.action_supinfo(action_uri, lld_graph_uri)
            context['lld_action'] = lld_action['action_value'] 
            context['lld_intention'] = lld_intention['intention_value'] 
            context['lld_toolknowledge'] = lld_toolknowledge['toolknowledge_value']
            context['lld_annotation'] = lld_annotation['annotation_value']
            context['lld_rationale'] = lld_rationale['rationale_value']
            context['lld_output'] = lld_output['output_value']

        return render(request, os.getcwd()+'/templates/checklists/action_supinfo.html', context)

def edit_action(request):
    if request.method == 'POST':
        context = dict()
        action_uri = request.POST.get('action_uri')
        gpm_graph_uri = request.POST.get('gpm_graph_uri')
        context['action_uri'] = action_uri
        context['gpm_graph_uri'] = gpm_graph_uri
        lld_graph_uri = request.POST.get('lld_graph_uri')
        context['lld_graph_uri'] = lld_graph_uri

        #記入したLLDのsupinfoの情報の取得
        lld_action, lld_intention, lld_toolknowledge, lld_annotation, lld_rationale, lld_output = sparql.action_supinfo(action_uri, lld_graph_uri)
        context['lld_action'] = lld_action['action_value'] 
        context['lld_intention'] = lld_intention['intention_value'] 
        context['lld_toolknowledge'] = lld_toolknowledge['toolknowledge_value']
        context['lld_annotation'] = lld_annotation['annotation_value']
        context['lld_rationale'] = lld_rationale['rationale_value']
        context['lld_output'] = lld_output['output_value']

        #GPMのsupinfoの情報取得
        gpm_action_uri = sparql.get_gpm_action(action_uri, gpm_graph_uri)
        if(gpm_action_uri != ''):
            gpm_action, gpm_intention, gpm_toolknowledge, gpm_annotation, gpm_rationale, gpm_output = sparql.action_supinfo(gpm_action_uri, gpm_graph_uri)
            context['gpm_action'] = gpm_action['action_value']
            context['gpm_intention'] = gpm_intention['intention_value']
            context['gpm_toolknowledge'] = gpm_toolknowledge['toolknowledge_value']
            context['gpm_annotation'] = gpm_annotation['annotation_value']
            context['gpm_rationale'] = gpm_rationale['rationale_value'] 
            context['gpm_output'] = gpm_output['output_value']

        return render(request, os.getcwd()+'/templates/checklists/edit_action.html', context)


#実行したアクションを記録する
def add_LLD(request):
    if request.method == 'POST':
        action_uri = request.POST.get('action_uri')
        gpm_graph_uri = request.POST.get('gpm_graph_uri')
        lld_graph_uri = request.POST.get('lld_graph_uri')
        action = request.POST.get('action')
        intention = request.POST.get('intention')
        toolknowledge = request.POST.get('toolknowledge')
        annotation = request.POST.get('annotation')
        rationale = request.POST.get('rationale')
        output = request.POST.get('output')

        sparql_update.add_LLD_tofuseki(action_uri, action, intention, toolknowledge, annotation, rationale, output, gpm_graph_uri, lld_graph_uri)
        sparql_update.add_done_action(action_uri, lld_graph_uri)

        print(action_uri)
        next_action_uri = sparql.get_nextaction(action_uri, lld_graph_uri)

        #条件文と次のアクションを保存する
        loopcondition, loopnext = sparql.get_nextloop(action_uri, lld_graph_uri)

        result = dict()
        result['next_action_uri']= next_action_uri
        result['loopcondition'] = loopcondition
        result['loopnext'] = loopnext

    return JsonResponse(result)
# Create your views here.


def show_pastLLD(request):
    context = {}
    action_uri = request.POST.get('action_uri')
    gpm_graph_uri = request.POST.get('gpm_graph_uri')
    context['gpm_graph_uri'] = gpm_graph_uri
    gpm_action_uri = sparql.get_gpm_action(action_uri, gpm_graph_uri)
    graph_uri, lld_actions_uri = sparql.get_lld_action2(gpm_action_uri, gpm_graph_uri)
 
    context['lld_actions']=[]   
    for i in range(len(lld_actions_uri)):
        context['lld_actions'].append([graph_uri[i]])
        lld_action_value, lld_intention, lld_toolknowledge, lld_annotation, lld_rationale, lld_output = sparql.action_supinfo(lld_actions_uri[i],graph_uri[i] )
        context['lld_actions'][i].append(sparql.get_graph_title(graph_uri[i]))
        context['lld_actions'][i].append(sparql.get_graph_description(graph_uri[i]))
        context['lld_actions'][i].append(lld_action_value['action_value'])
        context['lld_actions'][i].append(lld_intention['intention_value'])
        context['lld_actions'][i].append(lld_toolknowledge['toolknowledge_value'])
        context['lld_actions'][i].append(lld_annotation['annotation_value'])
        context['lld_actions'][i].append(lld_rationale['rationale_value'])
        context['lld_actions'][i].append(lld_output['output_value'])

    return render(request, os.getcwd()+'/templates/checklists/show_pastLLD.html', context)

def add_action(request):
    context = dict()
    context['action'] = request.POST.get('action')
    context['action_uri'] = request.POST.get('action_uri')
    context['lld_graph_uri'] = request.POST.get('lld_graph_uri')
    context['gpm_graph_uri'] = request.POST.get('gpm_graph_uri')

    return render(request,os.getcwd()+'/templates/checklists/add_action.html', context )

def hello(request):
    context = dict()
    return render(request,os.getcwd()+'/templates/checklists/hello.html', context )

def loop_add(request):
    result = dict()
    #このaction_uriはlld上のアクション
    action_uri = request.POST.get('action_uri')
    loopnext = request.POST.get('loopnext')
    lld_graph_uri = request.POST.get('lld_graph_uri')
    gpm_graph_uri = request.POST.get('gpm_graph_uri')
    print("あいうえお")
    print(action_uri, loopnext, lld_graph_uri, gpm_graph_uri)

    return JsonResponse(result)