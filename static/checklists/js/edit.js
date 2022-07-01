
function edit_popup(value) {

value_base = { id: value }

$.ajax({
type: 'POST',
url:  'edit_info_extraction_ajax',
data: value_base,
  dataType: 'text',
  // サーバから返送データを受け取る
  success: function (dataset) {
    from_json = JSON.parse(dataset);
    base_title = from_json["title"];
    base_detail = from_json["detail"];
    base_hour = from_json["hour"],
    base_minute = from_json["minute"],

    select_tags_hour = document.createElement('select');
    $(select_tags_hour).attr({
    'id': 'hour',
    });
    for (var i = 0; i < 24; i++) {
      var option = document.createElement('option');
      if (base_hour ==i) {
        option.setAttribute("selected", "selected");
      }
        option.innerHTML = i;
        select_tags_hour.appendChild(option);
    }

    minute_list=[0,15,30,45]
    select_tags_minute = document.createElement('select');
    $(select_tags_minute).attr({
    'id': 'minute',
    });
    for (var i = 0;i < minute_list.length; i++) {
      var option = document.createElement('option');
      if (base_minute ==minute_list[i]) {
        option.setAttribute("selected", "selected");
      }
        option.innerHTML = minute_list[i];
        select_tags_minute.appendChild(option);
    }

    html_section = `<section class="get-in-touch">
          <form class="contact-form row">
            <div class="form-field col x-50">
              <input id="title" class="input-text js-input" type="text" value="` + base_title + `" required>
              <label class="label" for="name">Title</label>
            </div>
          </form>
          <form class="contact-form row">
            <div class="form-field col x-100">
              <label class="label mb-4 pb-2" for="message">Detail</label>
              <textarea id="detail" class="m-form-textarea">` + base_detail + `</textarea>
            </div>
          </form>
          <form class="contact-form row us-form">
            <div class="form-field col x-100">
              <div class = "row ml-1 d-flex align-items-center">
                <span class="us-form-select-wrap">
                  ` +select_tags_hour.outerHTML+ `
                </span>
                <p class="p-0 m-0">&nbsp;&nbsp;:&nbsp;&nbsp;</p>
                <span class="us-form-select-wrap">
                  ` +select_tags_minute.outerHTML+ `
                </span>
                <label class="label mb-2 pb-1" for="message">Limit</label>
            </div>
          </form>
          </div>
        </section>
        <input type="hidden" id="id_input" name="id_input" value="`+ value + `">`

    swalWithBootstrapButtons.fire({

      title: "編集",
      html:
        html_section,
        position: 'center',
        padding: '1.25rem',
        width: '80%',
        showCloseButton: true,
        showCancelButton: true,
        focusConfirm: false,
        confirmButtonText:
        '<img src="../../../static/checklists/images/outline_mode_edit_white.png" width="24" height="24"> Update. ',
        cancelButtonText:
        '<img src="../../../static/checklists/images/delete_white.png" width="24" height="24"> Delete. ',
        showClass: {
          popup: 'animate__animated animate__fadeIn'
        },
        hideClass: {
          popup: 'animate__animated animate__fadeOut'
        }
    }).then((result) => {
          const title = Swal.getPopup().querySelector('#title').value
          const detail = Swal.getPopup().querySelector('#detail').value
          const hour = Swal.getPopup().querySelector('#hour').value
          const minute = Swal.getPopup().querySelector('#minute').value
          const id = Swal.getPopup().querySelector('#id_input').value
        if (result.isConfirmed) {
          swal.fire(
            {
            title: '確認',
            text: "更新してもよろしいですか?",
            icon: 'question',
            confirmButtonColor : '#28a745',
            cancelButtonColor: '#6c757d',
            showCancelButton: true,
            confirmButtonText: '更新',
            cancelButtonText: 'キャンセル',
            reverseButtons: true,
            showLoaderOnConfirm: true,
            preConfirm: () => {
              if (!title || !detail|| !hour|| !minute) {
                Swal.showValidationMessage(`Please enter all text.`)
              }
              values = { title: title, detail: detail, hour: hour, minute: minute, id: id }
              return values
            }
            }).then((result) => {
                $.ajax({
                type: 'POST',
                url:  'edit_click_ajax',
                data: values,
                dataType: 'text',

                // サーバから返送データを受け取る
                success: function (dataset) {
                  dataset = dataset;
                  console.log(dataset)
                  document.location.reload();
                  }
                })
              }
          )
        }else if (
          /* Read more about handling dismissals below */
          result.dismiss === Swal.DismissReason.cancel
        ) {
          swal.fire(
            {
            title: '確認',
            text: "削除してもよろしいですか?",
            icon: 'warning',
            confirmButtonColor : '#dc3545',
            cancelButtonColor: '#6c757d',
            showCancelButton: true,
            confirmButtonText: '削除',
            cancelButtonText: 'キャンセル',
            reverseButtons: true,
            showLoaderOnConfirm: true,
            preConfirm: () => {
              if (!title || !detail|| !hour|| !minute) {
                Swal.showValidationMessage(`Please enter all text.`)
              }
              values = { title: title, detail: detail, hour: hour, minute: minute, id: id }
              return values
            }
            }).then((result) => {
              $.ajax({
              type: 'POST',
              url:  'edit_delete_ajax',
              data: values,
              dataType: 'text',

              // サーバから返送データを受け取る
              success: function (dataset) {
                dataset = dataset;
                console.log(dataset)
                document.location.reload();
                }
              })
            }
          )
        }
      })
      }
    })
  }

var add_AM_text =
  `<form class="contact-form row us-form">
    <div class="form-field col x-100">
      <div class = "row ml-1 d-flex align-items-center">
        <span class="us-form-select-wrap">
          <select id ="hour">{% csrf_token %}
            <option>Hour</option>
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
            <option>6</option>
            <option>7</option>
            <option>8</option>
            <option>9</option>
            <option>10</option>
            <option>11</option>
          </select>
        </span>
        <p class="p-0 m-0">&nbsp;&nbsp;:&nbsp;&nbsp;</p>
        <span class="us-form-select-wrap">
          <select id ="minute">{% csrf_token %}
            <option>Minute</option>
            <option>0</option>
            <option>15</option>
            <option>30</option>
            <option>45</option>
          </select>
        </span>
        <label class="label mb-4" for="message">Limit</label>
    </div>
  </form>`

var add_PM_text =
  `<form class="contact-form row us-form">
    <div class="form-field col x-100">
      <div class = "row ml-1 d-flex align-items-center">
        <span class="us-form-select-wrap">
          <select id ="hour">{% csrf_token %}
            <option>Hour</option>
            <option>12</option>
            <option>13</option>
            <option>14</option>
            <option>15</option>
            <option>16</option>
            <option>17</option>
            <option>18</option>
            <option>19</option>
            <option>20</option>
            <option>21</option>
            <option>22</option>
            <option>23</option>
          </select>
        </span>
        <p class="p-0 m-0">&nbsp;&nbsp;:&nbsp;&nbsp;</p>
        <span class="us-form-select-wrap">
          <select id ="minute">{% csrf_token %}
            <option>Minute</option>
            <option>0</option>
            <option>15</option>
            <option>30</option>
            <option>45</option>
          </select>
        </span>
        <label class="label mb-4" for="message">Limit</label>
    </div>
  </form>`

var add_anytime_text =
  `<form class="contact-form row us-form">
    <div class="form-field col x-100">
      <div class = "row ml-1 d-flex align-items-center">
        <span class="us-form-select-wrap">
          <select id ="hour">{% csrf_token %}
            <option>Hour</option>
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
            <option>6</option>
            <option>7</option>
            <option>8</option>
            <option>9</option>
            <option>10</option>
            <option>11</option>
            <option>12</option>
            <option>13</option>
            <option>14</option>
            <option>15</option>
            <option>16</option>
            <option selected>17</option>
            <option>18</option>
            <option>19</option>
            <option>20</option>
            <option>21</option>
            <option>22</option>
            <option>23</option>
          </select>
        </span>
        <p class="p-0 m-0">&nbsp;&nbsp;:&nbsp;&nbsp;</p>
        <span class="us-form-select-wrap">
          <select id ="minute">{% csrf_token %}
            <option>Minute</option>
            <option selected>0</option>
            <option>15</option>
            <option>30</option>
            <option>45</option>
          </select>
        </span>
        <label class="label mb-4" for="message">Limit</label>
    </div>
  </form>`



function add_popup(time_zone) {
  time_zone = time_zone
  console.log(time_zone)
  if (time_zone == "AM") {
    select_text =add_AM_text
    }
  else if (time_zone == "PM") {
    select_text =add_PM_text
    }
  else {
    select_text =add_anytime_text
    }
  swalWithBootstrapButtons.fire({
    title: time_zone+" 表示内容追加",
    html:
      `<section class="get-in-touch">
          <form class="contact-form row">
            <div class="form-field col x-50">
              <input id="title" class="input-text js-input" type="text" required>
              <label class="label" for="name">Title</label>
            </div>
          </form>
          <form class="contact-form row">
            <div class="form-field col x-100">
              <input id="detail" class="input-text js-input" type="text" required>
              <label class="label" for="message">Detail</label>
            </div>
          </form>
          `+
          select_text
        +`
          </div>
        </section>
        <input type="hidden" id="time_zone_input" name="time_zone_input" value="`+ time_zone + `">`,
        position: 'center',
        padding: '1.25rem',
        width: '80%',
        showCloseButton: true,
        focusConfirm: false,
        confirmButtonText:
          '<img src="../../../static/checklists/images/outline_mode_edit_white.png" width="24" height="24"> Update. ',

        showClass: {
          popup: 'animate__animated animate__fadeIn'
        },
        hideClass: {
          popup: 'animate__animated animate__fadeOut'
        }
      }).then((result) => {
    if (result.isConfirmed) {
      const title = Swal.getPopup().querySelector('#title').value
      const detail = Swal.getPopup().querySelector('#detail').value
      const hour = Swal.getPopup().querySelector('#hour').value
      const minute = Swal.getPopup().querySelector('#minute').value
      const time_zone = Swal.getPopup().querySelector('#time_zone_input').value
      swal.fire(
        {
        title: '確認',
        text: "更新してもよろしいですか?",
        icon: 'warning',
        confirmButtonColor : '#28a745',
        cancelButtonColor: '#6c757d',
        showCancelButton: true,
        confirmButtonText: '更新',
        cancelButtonText: 'キャンセル',
        reverseButtons: true,
        showLoaderOnConfirm: true,
        preConfirm: () => {
          if (!title || !detail|| !hour|| !minute) {
            Swal.showValidationMessage(`Please enter all text.`)
          }
          values = { title: title, detail: detail, hour: hour, minute: minute,time_zone:time_zone }
          return values
        }
        }).then((result) => {
            $.ajax({
            type: 'POST',
            url:  'edit_add_ajax',
            data: values,
            dataType: 'text',

            // サーバから返送データを受け取る
            success: function (dataset) {
              dataset = dataset;
              console.log(dataset)
              document.location.reload();
              }
            })
          }
      )
    }
  })
}

$( '.js-input' ).keyup(function() {
  if( $(this).val() ) {
     $(this).addClass('not-empty');
  } else {
     $(this).removeClass('not-empty');
  }
});
