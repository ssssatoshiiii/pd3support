function show_selecteddescription(graph, title, epType){

  //選択された記述を表示
  if(epType == 'GPM'){
    $('#selected_GPM').children().remove();
    $('#selected_GPM').append("<input id='selected_GPM_title' type='hidden' name='gpm_graph_uri' value=" + graph + ">");
    $('#selected_GPM').append("<label>" + title + "</>")
  }
  else if(epType == 'LLD'){
    $('#selected_LLD').children().remove();
    $('#selected_LLD').append("<input type='hidden' name='lld_graph_uri' value =" + graph + ">");
    $('#selected_LLD').append("<label>" + title + "</>")
  }


  if($('#selected_GPM').children().length >0 && $('#selected_LLD').children().length >0){
    console.log('yes');
    $('#selected_description').append("<input type='submit' value='プロセスを開始する'>");
  }
}

function select_LLD(lld_graph_uri, lld_graph_title){
  console.log(lld_graph_title);
  $('#selected_description').append("<input type='hidden' name='lld_graph_uri' value=" + lld_graph_uri+">")
  $('#selected_description').append("<label>"+ lld_graph_title + "</label>");
  $('#selected_description').append("<input type='submit' value='プロセスを開始する'>")
}

function buttonClick(id_value) {
  //console.log('buttonclick');
  var value = { value: id_value };
  // ajax
  $.ajax({
  type: 'POST',
  url:  'exec_ajax',
  data: value,
  dataType: 'text',

    // サーバから返送データを受け取る
    success: function (dataset) {
      dataset = dataset;
      //console.log("T")
      }
    })
}

function buttonClick1(id_value){
  console.log('test')
}

const swalWithBootstrapButtons = Swal.mixin({
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
  buttonsStyling: false
    
  })

function popup(action, uri) {
  var value = { action: action, uri: uri };
  $.ajax({
    type: 'POST',
    url: 'swal_ajax',
    data: value,
    dataType: 'text',

    // サーバから返送データを受け取る
    success: function (dataset) {
      dataset = JSON.parse(dataset);
      title = dataset["title"]
      detail = dataset["detail"]
      references = dataset["references"]

      swalWithBootstrapButtons.fire({
        title: title,
        html:
        '<br><font size="5">'+ detail+'</font><br><br>',
        // text: detail,
        position: 'center',
        padding: '1.25rem',
        // grow: 'row',
        width: '80%',
        showCloseButton: true,
        focusConfirm: false,
        confirmButtonText:
          '<img src="../../../static/common/images/thumb_up.png" width="24" height="24"> Got it!!! ',
        footer: references,
        showClass: {
          popup: 'animate__animated animate__fadeIn'
        },
        hideClass: {
          popup: 'animate__animated animate__fadeOut'
        }
      })
    }
  })
}


function detail_action(uri, element){
 
  //それぞれの表のidを取得
  action_list_number = element.closest('.col-md-10').id.replace('action_list_layer_', '');
  data = {uri:uri , action_list_number:action_list_number}
  $.ajax({
    type: 'POST',
    url: 'second_graph_list',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    //もしdetail_actionが呼び出されたタグが最下層でなければ、呼び出されたタグの所属する階層以下の階層を消去する
    for(let i = 0; i < $('#action_list').children('div').length; i++){
      if(parseInt(action_list_number) < i+1 ){
        $('#action_list').children('div')[i].remove();
        i = i -1;
      }
    }
    $('#action_list').append(response);
  })
}


function show_action_supinfo(action_uri, gpm_graph_uri, lld_graph_uri, option){
  data = {action_uri:action_uri, gpm_graph_uri: gpm_graph_uri, lld_graph_uri:lld_graph_uri, option:option}
  $.ajax({
    type: 'POST',
    url:'action_supinfo_show',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    $('#action_supinfo').prepend(response);
  })
}

// function test(action){
//   console.log(action);
//   data = {action:action}
//   $.ajax({
//     type: 'POST',
//     url:'show_pastLLD',
//     data: data,
//     dataType: 'text',
//   })
//   .done(function(response){
//     console.log('test');
//     open('show_pastLLD');
//   })
// }

function escapeSelectorString(val){
  return val.replace(/[ !"#$%&'()*+,.\/:;<=>?@\[\\\]^`{|}~]/g, "\\$&");
}

function add_action_form(action_uri, action){
  $('#contextmenu').children().remove();
  // $('#contextmenu').append('<form method="POST"> {% csrf_token %} <input type="hidden" name="action_uri" value= '+ action_uri + ' /> <input type="text" name="added_action" /> <button name = "above" type="submit">' + action +'の上にアクションを追加</button><button name="below" type="submit">' + action +'の下にアクションを追加</button> </form>')
  $('#contextmenu').append('<form id = "contextmenu_form" method="POST"> {% csrf_token %} <input type="hidden" name="action_uri" value= '+ action_uri + ' />' + '</form>');
  $('#contextmenu_form').append('<input type="text" name="added_action" />');
  $('#contextmenu_form').append('<input type="hidden" name="gpm_graph_uri" value="{{gpm_graph_uri}}"  >');
  $('#contextmenu_form').append('<input type="hidden" name="lld_graph_uri" value="{{lld_graph_uri}}"  >');
  $('#contextmenu_form').append('<button name = "above" type="submit">' + action +'の上にアクションを追加</button>');
  $('#contextmenu_form').append('<button name="below" type="submit">' + action +'の下にアクションを追加</button>');
}

function second(action_uri, gpm_graph_uri, lld_graph_uri){
  // tag.parentNode.children[0].children[3].style.color = '#0000ff';
  data = {action_uri: action_uri, gpm_graph_uri:gpm_graph_uri, lld_graph_uri:lld_graph_uri, response:"http"}
  $.ajax({
    type: 'POST',
    url:'second',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    //アクションリストの追加
    l = $('#action_list').children().length-1
    for(let i = 0; i<l; i++){
      $('#action_list').children().eq(-1).remove();
    }
    $('#action_list').append(response);

    data1 = {action_uri: action_uri, gpm_graph_uri:gpm_graph_uri, lld_graph_uri:lld_graph_uri, response:'json'}
    $.ajax({
      type: 'POST',
      url:'second',
      data: data1,
      dataType: 'text',
    })
    .done(function(response){
      //アクションの詳細表示の追加
      $(".todo").css('background-color', '#ffffff');
      let objData = JSON.parse(response);
      let hier_actions = objData.hier_actions;

      $('#action_supinfo').children('div').not('#LLDedit').remove();
      for(let i=0; i<hier_actions.length; i++){
        // $("#"+escapeSelectorString(String(hier_actions[hier_actions.length-1-i]))).css('background-color', '#ffebcd');
        // $("#"+escapeSelectorString(String(hier_actions[hier_actions.length-1-i]))+"_").css('background-color', '#ffebcd');
        show_action_supinfo(hier_actions[hier_actions.length-1-i], gpm_graph_uri, lld_graph_uri, "GPM");
      }
   })
   })
}

function edit_action(action_uri, gpm_graph_uri, lld_graph_uri){

  $('#action_supinfo').children('div').remove();
  data = {action_uri: action_uri, gpm_graph_uri:gpm_graph_uri, lld_graph_uri:lld_graph_uri}
  $.ajax({
    type: 'POST',
    url:'edit_action',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    second(action_uri, gpm_graph_uri, lld_graph_uri);
    $('#edit_LLDinfo').children('div').remove();
    $('#edit_LLDinfo').append(response);
    $('.todo__text').css('color', '#2b2b2b');
    // console.log($("#"+escapeSelectorString(String(action_uri))).find(".todo__text"));
    // console.log(action_uri);
    // console.log(document.getElementById(String(action_uri)+"_"));
    $("#"+escapeSelectorString(String(action_uri))).find(".todo__text").css('color', '#f0f8ff');
  })

}