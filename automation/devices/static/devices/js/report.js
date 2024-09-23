//
let MAP = null;
let blue_circle = L.divIcon({ className: 'blue-circle'})
let orange_circle = L.divIcon({ className: 'orange-circle'})
let div_circle = orange_circle;

function blink(id, time, interval){
    var timer=window.setInterval(function(){id.css("opacity", "0.0");
    window.setTimeout(function(){id.css("opacity", "1");}, 100);}, interval);
    window.setTimeout(function(){clearInterval(timer); id.text('');}, time);
}

function playsound(nameid)  { $('#'+nameid).trigger("play"); }

function setLatLonZone(layer) {
    const corners = layer.getBounds();
    const northwest = corners.getNorthWest();
    const northeast = corners.getNorthEast();
    const southeast = corners.getSouthEast();
    const southwest = corners.getSouthWest();

    //console.log(northwest);   console.log(northeast); console.log(southeast);console.log(southwest);
    $('input.geo').val('');
    $('#id_lat_n').val(toFloat(northwest.lat, 6));
    $('#id_lat_s').val(toFloat(southeast.lat, 6));
    $('#id_lon_w').val(toFloat(northwest.lng, 6));
    $('#id_lon_e').val(toFloat(southeast.lng, 6));
}

function addTag(uuid, lat, lon) {
    let tag = $('div[title='+ uuid+']');
    try {
        if (tag != 0)
            tag.remove();
        L.marker(L.latLng(lat, lon), {
            title: uuid,
            icon: div_circle,
        }).addTo(MAP);
    } catch(e) {}
}

mapAddTag = addTag;

function resetMap() {
    MAP.setView([defaultLat, defaultLon], minZoom);
}

function mapInit() {  
    MAP = L.map('main_map', {
        minZoom: minZoom,
        maxZoom: maxZoom,
        drawControl: false,
    }).setView([defaultLat, defaultLon], minZoom);
    L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(MAP);
    L.marker([defaultLat, defaultLon]).addTo(MAP);
    MAP.on('click', function (e){ console.log( e.latlng ); });
    var drawnItems = new L.FeatureGroup();
    MAP.addLayer(drawnItems);
    
    var drawControl = new L.Control.Draw({
        draw: {
            polyline: false,
            polygon: false,
            circlemarker: false,
            circle: false,
        },
        edit: {
            featureGroup: drawnItems
        }
    });
    MAP.addControl(drawControl);
    MAP.on('draw:created', function (e) {
        var type = e.layerType,
            layer = e.layer;
        if (type === 'rectangle') {
            layer.on('mouseover', function() {setLatLonZone(layer);});
            layer.on('click',     function() {if (confirm(deletionMsg)==true){drawnItems.removeLayer(layer);$('input.geo').val(''); }});
            layer.on("edit",      function(e){setLatLonZone(layer);});
        }
        drawnItems.addLayer(layer);
    });
    MAP.on('draw:deleted', function (e) { $('input.geo').val(''); });
    $('#main_map').show();
}

mapInit();

