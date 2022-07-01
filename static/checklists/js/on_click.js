
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

function popup(value) {
  var value = { value: value };
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
  alert("yes");
}