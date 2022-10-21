function buttonClick(id_value) {
  console.log('buttonclick');
  var value = { value: id_value };
  // ajax
  $.ajax({
  type: 'POST',
  url:  'exec_ajax',
  data: value,
  dataType: 'text',

    // サーバから返送データを受け取る
    success: function (dataset) {
      console.log(dataset);
      dataset = dataset;
      //console.log("T")
      }
    })
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
    $('#action_supinfo').children('div').remove();
    $('#action_supinfo').append(response);
  })
}


function escapeSelectorString(val){
  if(val != null){
    return val.replace(/[ !"#$%&'()*+,.\/:;<=>?@\[\\\]^`{|}~]/g, "\\$&");
  }
  else{
    return val;
  }
}

function add_action_form(action_uri, action){

  $('#contextmenu_form').children().remove();
  $('#contextmenu_form').append('<label class="mt-3">アクションの追加</label>')
  $('#contextmenu_form').append('<input type="hidden" name="action_uri" value= '+ action_uri + ' />' );
  $('#contextmenu_form').append('<input type="text" style="width:100%;" name="added_action" />');
  $('#contextmenu_form').append('<input type="hidden" name="gpm_graph_uri" value="{{gpm_graph_uri}}"  >');
  $('#contextmenu_form').append('<input type="hidden" name="lld_graph_uri" value="{{lld_graph_uri}}"  >');
  $('#contextmenu_form').append('<button class="mt-1" name = "above" type="submit">' + '「'+ action + '」' +'の前にアクションを追加</button>');
  $('#contextmenu_form').append('<button class="mt-1" name="below" type="submit">' + '「'+ action +'」'+ 'の後ろにアクションを追加</button>');
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
      console.log(hier_actions);

      for(let i=0; i<hier_actions.length; i++){
        $("#"+escapeSelectorString(String(hier_actions[i]))).css('background-color', '#adff2f');
      }
      let chosen_action_uri = $('input[name="chosen_action_uri"]').val();
      $("#"+escapeSelectorString(String(chosen_action_uri))).css('border', '3px double #0067c0')
   })
   })
}

function edit_action(action_uri, gpm_graph_uri, lld_graph_uri){

  data = {action_uri: action_uri, gpm_graph_uri:gpm_graph_uri, lld_graph_uri:lld_graph_uri}
  $.ajax({
    type: 'POST',
    url:'edit_action',
    data: data,
    dataType: 'text',
  })
  .done(function(response){
    show_action_supinfo(action_uri, gpm_graph_uri, lld_graph_uri, "GPM");
    $('#edit_LLDinfo').children('div').remove();
    $('#edit_LLDinfo').append(response);
    // $('.todo__text').css('color', '#2b2b2b');
    // $("#"+escapeSelectorString(String(action_uri))).find(".todo__text").css('color', '#f0f8ff');
    $('.todo').css('border', 'none');
    $("#"+escapeSelectorString(String(action_uri))).css('border', '3px double #0067c0');
  })

}