(function($) {

  function init(e) {
    var container = $(this);
    var loaded = false;
    container.find('.easyslider').loaded(function() {
      if(loaded)
        return;
      loaded = true;
      container.find('.easyslider').each(function() {
        var classes = $(this).attr('class').split(' ');
        var settings;
        for(var i=0; i<classes.length; i++)
          if(classes[i].substr(0, 11) == 'easyslider-') {
            var settings = easyslider.settings[classes[i].substr(11)];
            break;
          }
        if(!settings)
          settings = easyslider.settings['standard'];
        $(this).easySlider(settings);
      });
    });
  }

  $(document).ready(function(e) {
    $.proxy(init, $('body'))(e);
    $('.viewletmanager').on('viewlets.updated', init);
  });

})(jQuery);
