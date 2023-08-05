(function($) {

  var default_options = {
    multiple: false,
    items: '> .item',
    content: '> .content',
    trigger: '> .trigger'
  }

  $.fn.raccordion = function(options) {
    options = $.extend(default_options, options);
    var container = this;
    container.addClass('accordion-active');
    var items = this.find(options.items);
    container.find(options.items + ' ' + options.content).hide();
    container.find(options.items + ' ' + options.trigger).click(function(e) {
      var trigger = $(this);
      var item = trigger.closest(options.items.replace(/^> /, ''));
      var content = item.find(options.content);
      if(item.hasClass('accordion-open'))
        content.stop().slideUp('fast', 'easeInOutExpo');
      else {
        content.stop().removeAttr('style').hide().slideDown('fast', 'easeInOutExpo');
        if(!options.multiple)
          container.find('.accordion-open ' + options.trigger).trigger('click');
      }
      item.toggleClass('accordion-open');
    });
    return this;
  }

  function init(e) {
    $(this).find('.accordion-listing').each(function() {
      var container = $(this);
      container.find('> ul > li').each(function() {
        var item = $(this);
        var content = $('<div class="content" />').appendTo(item);
        content.append(item.find('> p, > .body'));
      });
      container.find('> ul').raccordion({
        multiple: container.hasClass('multiple'),
        items: '> li',
        content: '> .content',
        trigger: '> h2'
      });
    });
  }

  $(document).ready(function(e) {
    $.proxy(init, $('body'))(e);
    $('.viewletmanager').bind('viewlets.updated', init);
  });

})(jQuery);