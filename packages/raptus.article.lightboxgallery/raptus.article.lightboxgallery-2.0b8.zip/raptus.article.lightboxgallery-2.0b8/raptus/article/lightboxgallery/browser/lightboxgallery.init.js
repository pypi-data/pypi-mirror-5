(function($) {

  function init(e) {
    var images = new Array();
    var settings = inlinelightbox.settings['raptus_article_lightboxgallery'];
    $(this).find('a[rel^=lightboxgallery]').each(function() {
      var o = $(this);
      var rel = o.attr('rel');
      if($.inArray(rel, images) == -1)
        images.push(rel);
    });
    for(var i=0; i<images.length; i++) {
      $(this).find('a[rel="'+images[i]+'"]').inlineLightBox(settings);
    }
  }

  $(document).ready(function(e) {
    $.proxy(init, $('body'))(e);
    $('.viewletmanager').on('viewlets.updated', init);
  });

})(jQuery);