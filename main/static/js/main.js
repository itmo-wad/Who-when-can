//add day event handler. on button click add new empty day
$( ".add_day" ).click(function() {
    // $( ".date" ).append( $( "<div class=\"day\"><div class=\"col span_1_of_2\"><i class=\"fas fa-calendar-day date__logo\"></i>Choose your date<input type=\"date\" class=\"datepicker\"></div><div class=\"col span_1_of_2\"><div class=\"hour\">Choose your time<input type=\"time\" class=\"timepicker\"></div><div class=\"add_hours btn__small btn__blue\">Click to add more hours</div></div></div>" ) );
    $( ".date__table" ).append( $("<tr class=\"date\"><td><i class=\"fas fa-calendar-day date__logo\"></i>Choose your date<input type=\"date\" class=\"datepicker\"></td><td><div class=\"hour\">Choose your time<input type=\"time\" class=\"timepicker\"></div><div class=\"add_hours btn__small btn__blue\">Click to add more hours</div></td></tr>"));
    
    
  });

//add hour event handler. on button click add new empty hour
$( "body" ).on( "click", ".add_hours", function() {
    $(this).before($( "<div class=\"hour\">Choose your time<input type=\"time\" class=\"timepicker\"></div>" ) );
    	
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