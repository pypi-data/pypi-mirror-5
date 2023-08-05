var mediagallery = {
  selector: '.media'
};

(function($) {

  mediagallery.init = function(container) {
    container.find(mediagallery.selector).each(mediagallery.create);
  }

  mediagallery.create = function() {
    var container = $(this);
    var touch = !!('ontouchstart' in window) || !!('onmsgesturechange' in window);
    container.addClass('media-enhanced');
    var groups = container.find('> ul > li');
    var nav = false;
    if(groups.size() > 1)
      nav = $('<ul class="visualNoMarker nav" />');
    var htimer = false;
    function horizontalrealign(e) {
      if(htimer)
        window.clearTimeout(htimer);
      htimer = window.setTimeout(function() {
        var height = 0;
        var width = container.width() - 30;
        var groupwidth = 0;
        var navwidth = nav ? nav.outerWidth() : 0;
        groups.each(function() {
          var group = $(this);
          var items = group.find('> ul li');
          var itemheight = 100000;
          items.addClass('no-animation').each(function() {
            var item = $(this);
            item.removeAttr('style').css('width', Math.min(width, item.data('w')));
            itemheight = Math.min(itemheight, item.data('h') * Math.min(width, item.data('w')) / item.data('w'));
          }).removeAttr('style').css('height', itemheight).each(function() {
            var item = $(this);
            var w = item.data('w') * itemheight / item.data('h');
            item.css('width', w);
            if(w > width - 150)
              item.addClass('arrows-inside');
            else
              item.removeClass('arrows-inside');
            groupwidth += w + 30;
          });
          wrapped = group.css('height', 'auto').find('.wrapped').removeAttr('style');
          wrapped.css({
            'width': wrapped.outerWidth() - parseInt(wrapped.css('padding-left')) - navwidth,
            'padding-right': navwidth
          }).find('> ul').css('width', width);
          height = Math.max(group.height(), height);
          items.removeClass('no-animation');
          var item = group.find('> ul li.current');
          slideTo(item && item.size() ? item : group.find('> ul li:first-child'));
        });
        groups.css('height', height);
        container.css('height', height);
        if(nav)
          nav.find('li.current a').trigger('click');
      }, 250);
    }
    groups.each(function() {
      var group = $(this);
      var img = group.find('.wrapped > img');
      if(nav) {
        var link = $('<a href="javascript://" title="' + group.find('h2 > span').html() + '" />');
        if(img.size())
          link.append(img);
        else
          link.html(link.attr('title'));
        link.click(mediagallery.group);
        nav.append(link);
        link.wrap('<li />');
      } else if(img.size())
        img.remove();
      var vtimer = false;
      var prevwidth = container.width();
      function verticalrealign() {
        if(vtimer)
          window.clearTimeout(vtimer);
        vtimer = window.setTimeout(function() {
          if(prevwidth != container.width()) {
            var item = group.find('> ul li.current');
            slideTo(item && item.size() ? item : group.find('> ul li:first-child'));
          }
          prevwidth = container.width();
        }, 250);
      }
      var width = 0;
      var items = group.find('> ul li');
      var d = items.size();
      function loaded() {
        d--;
        var item = $(this);
        if(!item.is('li'))
          item = item.closest('li');
        width += item.data('w') + 30;
        var content = group.find('> ul');
        content.css('width', width);
        if(d == 0) {
          $(window).load(verticalrealign);
          $(window).resize(verticalrealign);
          verticalrealign();
          horizontalrealign();
        }
      }
      items.each(function() {
        var item = $(this);
        var img = item.find('> img');
        if(img.size()) {
          var image = new Image();
          image.onload = function(e) {
            item.data('w', image.width).data('h', image.height).addClass('ready');
            $.proxy(loaded, item)();
          };
          image.src = img.attr('src');
        } else {
          item.data('w', item.width()).data('h', item.height()).addClass('ready');
          $.proxy(loaded, item)();
        }
        if(item.is(':first-child') && item.is(':last-child'))
          return;
        if(!item.is(':first-child'))
          $('<a href="javascript://" class="prev">&lt;</a>').click(mediagallery.prev).appendTo(item);
        if(!item.is(':last-child'))
          $('<a href="javascript://" class="next">&gt;</a>').click(mediagallery.next).appendTo(item);
        if(img.size() && !touch)
          img.click(mediagallery.select);
      });
    });
    if(nav) {
      container.prepend(nav);
      nav.wrap('<div class="wrapped nav-wrapper" />').find('> li:first-child').addClass('current');
    }
    var stimer = false;
    if(touch)
      container.swipe({
        swipeLeft: function(e) {
          if(stimer)
            window.clearTimeout(stimer);
          stimer = window.setTimeout(function() {
            group = groups.eq(groups.size() > 1 ? nav.find('> li.current').index() : 0);
            group.find('> ul li.current a.next').trigger('click');
          }, 10);
        },
        swipeRight: function(e) {
          if(stimer)
            window.clearTimeout(stimer);
          stimer = window.setTimeout(function() {
            group = groups.eq(groups.size() > 1 ? nav.find('> li.current').index() : 0);
            group.find('> ul li.current a.prev').trigger('click');
          }, 10);
        }
      });
    $(window).resize(horizontalrealign);
    $(document).keydown(function(e) {
      var link = false;
      if(e.keyCode == 37 || e.keyCode == 39) { // left & right
        var group = groups.eq(nav ? nav.find('.current').index() : 0);
        if(e.keyCode == 37) // left
          link = group.find('.current > .prev');
        else // right
          link = group.find('.current > .next');
      } else if(e.keyCode == 38 && nav) { // up
        link = nav.find('.current').prev('li');
        link = link.size() ? link.find('a') : false;
      } else if(e.keyCode == 40 && nav) { // down
        link = nav.find('.current').next('li');
        link = link.size() ? link.find('a') : false;
      }
      if(link && link.size())
        link.trigger('click');
    });
  }

  mediagallery.group = function(e) {
    var link = $(this);
    link.closest('ul').find('.current').removeClass('current');
    var group = link.closest('li').addClass('current').index();
    var container = link.closest('.media-enhanced');
    var groups = container.find('> ul.manageableList');
    groups.stop().animate({'top': - group * container.height()}, 500, 'easeInOutExpo');
  }

  function slideTo(item) {
    if(!item || !item.size())
      return;
    var group = item.closest('ul');
    var container = group.closest('.media-enhanced');
    group.stop().animate({'left': - item.position().left - 15 + (container.width() - item.width()) / 2}, 500, 'easeInOutExpo', function() {
      group.find('.current').removeClass('current');
      item.addClass('current');
    });
  }

  mediagallery.select = function(e) {
    var item = $(this).closest('li');
    if(!item.hasClass('current'))
      return slideTo(item);
    var next = item.find('a.next');
    if(next.size())
      return next.trigger('click');
    slideTo(item.closest('ul').find('li:first-child'));
  }

  mediagallery.next = function(e) {
    slideTo($(this).closest('li').next('li'));
  }

  mediagallery.prev = function(e) {
    slideTo($(this).closest('li').prev('li'));
  }

  $(document).ready(function() {
    mediagallery.init($('body'));
    $('.viewletmanager').bind('viewlets.updated', function(e) {
      mediagallery.init($(this));
    });
  });

})(jQuery);
