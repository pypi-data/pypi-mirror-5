(function($) {
  return $(function() {
    $('.flip-box').click(function() {});
    $(':file').filestyle({
      icon: true
    });
    return $('input[data-slider-value]').slider();
  });
})(jQuery);
