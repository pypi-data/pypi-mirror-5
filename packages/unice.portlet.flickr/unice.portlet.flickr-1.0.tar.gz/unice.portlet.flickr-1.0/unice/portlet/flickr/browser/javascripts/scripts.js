$(document).ready(function(){
    $('.flickrAlbum').each(function( index ) {
        var self = $(this);

        var user = self.data('user');
        var album = self.data('album');
        var count = self.data('count');

        var flickrFeedUrl = 'http://api.flickr.com/services/feeds/photoset.gne?set='+album+'&nsid='+user+'&lang=fr&jsoncallback=?';
        $.getJSON(
            flickrFeedUrl, {format: 'json'},
            function (data) {
                // Titre
                var prefix = 'Contenu provenant de ';
                var title = data.title.substring(prefix.length);
                self.append('<small>'+title+'</small>');
                self.append('<br class="visualClear"/>');
                
                // Photos
                $.each(data.items, function (i, item) {
                    var a = $('<a/>').attr({'href': item.link, 'data-toggle': 'tooltip',  'title': item.title});
                    var img = $('<img/>').attr('src', item.media.m.replace("_m.jpg", "_q.jpg"));
                    
                    a.attr('style', 'float:left; width:33.3%; padding:1%');
                    img.attr('style', 'width:100%;');
                    
                    a.tooltip();
                    a.append(img);
                    self.append(a);
                    
                    if (i == count-1) return false;
                });
            }
        );

    });
});