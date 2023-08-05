var slideshow = {
  selector: '.slideshow'
};

(function($) {

  slideshow.init = function(container) {
    container.find(slideshow.selector).each(slideshow.create);
  };

  slideshow.create = function() {
    var touch = !!('ontouchstart' in window) || !!('onmsgesturechange' in window);
    var container = $(this);
    var slides = container.find('> li');
    slides.each(function() {
      var content = $(this).find('> .wrapped > .content');
      var nav = $('<ul class="visualNoMarker nextprevious" />');
      var prev = $('<a href="javascript://" class="prev">&lt;</a>').appendTo(nav).click(slideshow.prev);
      var next = $('<a href="javascript://" class="next">&gt;</a>').appendTo(nav).click(slideshow.next);
      prev.wrap('<li />');
      next.wrap('<li />');
      nav.prependTo(content);
      if(touch)
        $(this).swipe({
          swipeLeft: function(e) {
            next.trigger('click');
          },
          swipeRight: function(e) {
            prev.trigger('click');
          }
        });
    });
    var interval = window.setInterval(function() {
      if(!container)
        return window.clearInterval(interval);
      var current = container.find('> li.current');
      if(!current.size())
        current = container.find('> li:first-child');
      if(!current.size())
        return window.clearInterval(interval);
      current.find('.nextprevious .next').trigger('click');
    }, 8000);
  };

  function swap(hide, show) {
    hide.find('> .wrapped > .content').stop().animate({
      'margin-bottom': -20,
      'opacity': 0
    }, 500, function() {
      hide.stop().show().addClass('prev').removeClass('current');
      show.stop().hide().addClass('current');
      var content = show.find('> .wrapped > .content').removeAttr('style').hide();
      show.fadeTo(500, 1, function() {
        hide.hide().removeClass('prev');
        content.stop().removeAttr('style').hide().css('margin-bottom', -20).animate({
          'margin-bottom': 0,
          'opacity': 1
        }, 500).show();
      }).show();
    });
  }

  slideshow.next = function(e) {
    var slide = $(this).closest('.slideshow > li');
    var next = slide.next('li');
    if(!next.size())
      next = slide.closest('.slideshow').find('li:first-child');
    swap(slide, next);
  };

  slideshow.prev = function(e) {
    var slide = $(this).closest('.slideshow > li');
    var prev = slide.prev('li');
    if(!prev.size())
      prev = slide.closest('.slideshow').find('li:last-child');
    swap(slide, prev);
  };

  $(document).ready(function() {
    slideshow.init($('body'));
    $('.viewletmanager').on('viewlets.updated', function(e) {
      slideshow.init($(this));
    });
  });

})(jQuery);
