
function buttonClick(id_value) {
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
      // console.log("T")
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

function test() {
  alert("yeah");
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


function show_action_supinfo(action,uri){
  data = {action:action, uri:uri}
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

