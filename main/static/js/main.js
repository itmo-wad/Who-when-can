//add day event handler. on button click add new empty day
$( ".add_day" ).click(function() {
    $( ".date" ).append( $( "<div class=\"day\"><input type=\"date\"><div class=\"hour\"><input type=\"time\"></div><div class=\"add_hours\">Click to add hours</div></div>" ) );
  });

//add hour event handler. on button click add new empty hour
$( "body" ).on( "click", ".add_hours", function() {
    $(this).before($( "<div class=\"hour\"><input type=\"time\"></div>" ) );
  });


//add submit event handler. on button click parse all days and hours, create JSON out of this and send it to the backend
function submit_first_dates() {
    var json_obj = {};
    var days = [];
    json_obj.days=days;
    $(".day").each(function() {
        var hours = [];       
        $(this).children(".hour").each(function() {
            hours.push($(this).children(":input").val());
            });
        var day = {
            "day": $(this).children(":input").val(),
            "hours": Object.assign({}, hours)
            }
        json_obj.days.push(day);
    });
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