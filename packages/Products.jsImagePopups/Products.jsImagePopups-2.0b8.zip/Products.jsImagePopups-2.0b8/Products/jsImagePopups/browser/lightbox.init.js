(function($) {

  function init(e) {
    var container = $(this);
    var images = [];
    container.find('a[rel^=lightbox]').each(function() {
      var o = $(this);
      var rel = o.attr('rel');
      if((rel.length == 8 || rel.indexOf('lightbox[') === 0) && $.inArray(rel, images) == -1)
        images.push(rel);
    });
    for(var i=0; i<images.length; i++)
      container.find('a[rel="'+images[i]+'"]').lightBox(lightbox_settings);

    container.find('a[href*=image_view_fullscreen]').each(function() {
      var o = $(this);
      o.attr('href', o.attr('href').replace('image_view_fullscreen', 'image_preview'));
      o.lightBox(lightbox_settings);
    });
    
    container.find('.photoAlbumEntry a').each(function() {
      var o = $(this);
      o.attr('href', o.attr('href').replace('view', 'image_preview'));
    });
    container.find('.photoAlbumEntry a').lightBox(lightbox_settings);
  }

  $(document).ready(function(e) {
    $.proxy(init, $('body'))(e);
    $('.viewletmanager').bind('viewlets.updated', init);
  });

})(jQuery);

