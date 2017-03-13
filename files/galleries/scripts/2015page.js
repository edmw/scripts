/*
 * Requires
 * - jquery-3.1.1.slim.min.js
 * - jquery.popupoverlay-1.7.13.min.js
 */

/*
 * Load next image page, if any.
 */
function nextImage() {
    // get link to next image page from html link element.
    var href = $('link[rel=next]').attr('href')
    if (href) {
        window.location.href = href;
    }
}

/*
 * Load previous image page, if any.
 */
function previousImage() {
    // get link to previous image page from html link element.
    var href = $('link[rel=prev]').attr('href');
    if (href) {
        window.location.href = href;
    }
}

/*
 * Load index page, if any.
 */
function showIndex() {
    // get link to index page from html link element.
    var href = $('link[rel=index]').attr('href');
    if (href) {
        window.location.href = href;
    }
}

var map = null;
function initializeMap(){
    if(map == null) {
        var mapElement = $('#map')
        var mapLat = $(mapElement).data('lat')
        var mapLon = $(mapElement).data('lon')
        var mapLatLng = new google.maps.LatLng(mapLat, mapLon)
        var mapCanvas = document.getElementById('map');
        var mapOptions = {
          center: mapLatLng,
          zoom: 8,
          mapTypeId: google.maps.MapTypeId.SATELLIT
        }
        map = new google.maps.Map(mapCanvas, mapOptions);
        var mapMarker = new google.maps.Marker({
            position: mapLatLng,
            map: map,
        });
    }
}

$(document).ready(function() {
    $(document).keyup(
        function(event) {
            var popup = $('#info').data('popup-visible') || $('map').data('popup-visible')
            switch(event.keyCode){
                case 39: // key right
                    if (!popup) {
                        nextImage();
                    }
                    break;
                case 37: // key left
                    if (!popup) {
                        previousImage();
                    }
                    break;
                case 38: // key up
                    if (!popup) {
                        showIndex();
                    }
                    break;
                case 73: // i
                    if (!popup) {
                        $('#info').popup('show');
                    }
                    break;
                case 77: // m
                    if (!popup) {
                        $('#map').popup('show');
                    }
                    break;
                case 27: // escape
                    $('#info').popup('hide');
                    $('#map').popup('hide');
                    break;
                case 32: // space
                    if (!popup) {
                        nextImage();
                        event.stopImmediatePropagation();
                    }
                    break;

                //default: alert(event.keyCode);
            }
        }
    );

    $('#info').popup({
        openelement: '#infolink',
        transition: 'all 0.3s',
        opacity: '0.8'
    });

    $('#map').popup({
        openelement: '#maplink',
        transition: 'all 0.3s',
        opacity: '0.8',
        onopen: function() {
            initializeMap();
        }
    });
});
