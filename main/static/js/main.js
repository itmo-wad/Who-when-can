//add day event handler. on button click add new empty day
var hour_html =`
<div class=\"hour\">
  Choose your time 
  <input type=\"time\" class=\"timepicker inline\"> 
  <div class=\"delete_hours btn__small btn__blue inline\">
    Remove
  </div>
</div>`

var day_html = `
<tr class=\"date\">
  <td class=\"date__td\">
    <i class=\"fas fa-calendar-day date__logo\"></i>
    Choose your date 
    <input type=\"date\" class=\"datepicker inline\"> 
    <div class=\"delete_day btn__small btn__blue inline\">
      Click to remove this day
    </div>
    <div class=\"clone_day btn__small btn__blue inline\">
      Click to clone this day
    </div>
  </td>
  <td class=\"hour__td\">
<div class=\"add_hours btn__small btn__blue\">
  Click to add timeslot
</div>
`+hour_html+`</td></tr>`;

$( ".add_day" ).click(function() {

    $( ".date__table" ).append(day_html);   
    
  });

//add hour event handler. on button click add new empty hour
$( "body" ).on( "click", ".add_hours", function() {
    $(this).parent().append(hour_html);
  });

//delete hour
  $( "body" ).on( "click", ".delete_hours", function() {
    $(this).parent().remove();
  });

  //delete day
  $( "body" ).on( "click", ".delete_day", function() {
    $(this).parent().parent().remove();
  });

  $( "body" ).on( "click", ".clone_day", function() {
    clone = $(this).parent().parent().clone();
    clone.appendTo($(this).parent().parent().parent());
  });




//add submit event handler. on button click parse all days and hours, create JSON out of this and send it to the backend
function submit_first_dates() {
  var json_obj = {};
  var days = [];
  json_obj.days=days;
  $('.date__table > tbody  > tr').each(function() {
  var hours = [];
  $(this).find('input').slice(1).each(function() {if ($(this).val()){hours.push($(this).val())}});
  var day = {
            "day": $(this).find('input').eq(0).val(),
            "hours": Object.assign({}, hours)
            }
        json_obj.days.push(day);
  })
  $('#available_dates').val(JSON.stringify(json_obj));
  return true;
};

// change color of selected table element
$( function() {
  $('table table table td').click( function() {
    $(this).toggleClass("selected-cell");
  } );
} );

//send selected days to the server
function submit_selected_dates() {
  var obj = {"day":{}};
  $( "table" ).find( ".selected-cell" ).each(function(){
    var date = $(this).parent().parent().parent().parent().parent().find('td').first().text();
    var hour = $(this).text();
    if (obj.day[date]== undefined){
      obj.day[date]={'hours':[hour]}}
    else{
      obj.day[date].hours.push(hour)};
    });
  $('#selecteddaysandhours').val(JSON.stringify(obj));
  console.log(JSON.stringify(obj));
  return true;
};

//copy meeting's link to clipboard
function copy_to_clipboard(){
  var copyText = document.getElementById("meeting_link");
  copyText.select();
  copyText.setSelectionRange(0, 99999)
  document.execCommand("copy");
  if ($('#copied_text').hasClass('hidden')){
    $('#copied_text').css('visibility', 'visible');
    setTimeout(() => {
      $('#copied_text').css('visibility', 'hidden');
    }, 2000);
  }
}