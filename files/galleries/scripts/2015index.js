/*
 * Requires
 * - jquery-3.1.1.slim.min.js
 * - jquery.popupoverlay-1.7.13.min.js
 */

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
function initializeCatalogMap() {
    if(map == null) {
        var mapElement = $('#map');
        var mapCountries = $(mapElement).data('countries');
        mapDataArray = [['Country', 'Visits']].concat(mapCountries);

        var data = google.visualization.arrayToDataTable(mapDataArray);

        var options = {
            displayMode: 'regions',
            legend: 'none',
            enableRegionInteractivity: false,
            region: 'world',
            backgroundColor: {
                fill: 'white',
                stroke: 'transparent',
                strokeWidth: 0,
            },
            defaultColor: '#369',
            datalessRegionColor: '#f5f5f5',
            colorAxis: {colors: ['#5599cc', '#336699']},
        };

        var map = new google.visualization.GeoChart(document.getElementById('map'));
        map.draw(data, options);
    }
}

$(document).ready(function() {
    // scroll top positions ([current, previous])
    var scrollTop = [0, 0];
    // monitor scroll top positions
    $(window).scroll(function() {
        // set previous scroll top position
        scrollTop[1] = scrollTop[0];
        // set current scroll top position
        scrollTop[0] = $(document).scrollTop();
    });
    $(document).keyup(
        function(event) {
            switch(event.keyCode) {
                case 38: // key up => load index page

                    // because key up is used to scroll,
                    // we only use key up to load the index page
                    // if we are at the top of the page
                    if (scrollTop[0] == 0 && scrollTop[1] == 0) {
                        showIndex();
                    }
                    else {
                        scrollTop[1] = 0;
                    }
                    break;

                case 77: // m

                    var mapElement = $('#map');
                    if (mapElement) {
                        $(mapElement).popup('show');
                    }
                    break;

                //default: alert(event.keyCode);
            }
        }
    );

    if($('#map').hasClass('catalog')) {
        $('#map').popup({
            openelement: '#maplink',
            transition: 'all 0.3s',
            opacity: '0.8',
            onopen: function() {
                initializeCatalogMap();
            }
        });
    }
});

