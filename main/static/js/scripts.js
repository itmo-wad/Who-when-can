$(document).ready(
    // show hide the notifications text
    $('.header__notifications--logo').click(
        function(){
            if ($('.header__notifications--text').hasClass('hide')){
                $('.header__notifications--text').css("display", "block");
                $('.header__notifications--text').addClass('show');
                $('.header__notifications--text').removeClass('hide');
            }
            else{
                $('.header__notifications--text').css("display", "none");
                $('.header__notifications--text').addClass('hide');
                $('.header__notifications--text').removeClass('show');
            }
        }
    )


)