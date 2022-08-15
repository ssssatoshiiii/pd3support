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


function show_action_supinfo(action,uri, gpm_graph_uri, lld_graph_uri){
  data = {action:action, uri:uri, gpm_graph_uri: gpm_graph_uri, lld_graph_uri:lld_graph_uri}
  $.ajax({
    type: 'POST',
    url:'action_supinfo_show',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    $('#action_supinfo').children('div').remove();
    $('#action_supinfo').append(response);
  })
  
}

function test(action){
  console.log(action);
  data = {action:action}
  $.ajax({
    type: 'POST',
    url:'show_pastLLD',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    console.log('test');
    open('show_pastLLD');
  })

}
