(function($) {
  $.fn.default_text = function() {
    $(this).addClass('defaulttext_field');
    $(this).bind('focus', function () {
        $(this).removeClass('defaulttext_field');
        $(this).get(0).value = '';
    });
  }
})(jQuery);