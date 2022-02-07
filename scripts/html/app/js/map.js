var fonds1 = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
			'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		id: 'mapbox.streets'
	});

	var mymap = L.map('content', {
		layers : [fonds1]
	}).setView([48, 2], 3);

	var wmsLayer = L.tileLayer.wms('http://psig.huma-num.fr/geoserver/Front_end/wms?', {
    	layers: 'Front_end:shape_all_geom_omeka_polygons',
	transparent: true,
	format: 'image/png'
	}).addTo(mymap);

/*
	var basemaps = {
    	Polygones: L.tileLayer.wms('http://psig.huma-num.fr/geoserver/Front_end/wms?service=WMS&version=1.1.0&request=GetMap&layers=Front_end:shape_all_geom_omeka_polygons&styles=&bbox=-27.092399,-41.172242,67.495055,49.089256&width=768&height=732&srs=EPSG:4326&format=application/openlayers', {
        layers: 'of:polygones'})
	};

	L.control.layers(basemaps).addTo(mymap);

	basemaps.Polygones.addTo(mymap);

var layerControl = L.control.layers(departments, grounds);
    map.addControl(layerControl);
*/
ms_url="http://psig.huma-num.fr/geoserver/Front_end/wms?";
mymap.addEventListener('click', Identify);
function Identify(e)
{
    // set parameters needed for GetFeatureInfo WMS request
    var BBOX = mymap.getBounds().toBBoxString();
    var WIDTH = mymap.getSize().x;
    var HEIGHT = mymap.getSize().y;
    var X = mymap.layerPointToContainerPoint(e.layerPoint).x;
     var Y = mymap.layerPointToContainerPoint(e.layerPoint).y;
     // compose the URL for the request
    var URL = ms_url + 'SERVICE=WMS&VERSION=1.1.0&REQUEST=GetFeatureInfo&LAYERS=Front_end:shape_all_geom_omeka_polygons&QUERY_LAYERS=Front_end:shape_all_geom_omeka_polygons&BBOX='+BBOX+'&FEATURE_COUNT=1&HEIGHT='+HEIGHT+'&WIDTH='+WIDTH+'&INFO_FORMAT=application%2Fjson&SRS=EPSG%3A4326&X='+X+'&Y='+Y;

   console.log(URL);
    //send the asynchronous HTTP request using jQuery $.ajax
    $.ajax({
        url: URL,
        dataType: "html",
        type: "GET",
        success: function(data)
        {
            var popup = new L.Popup
            ({
                maxWidth: 300
            });

	    //var jsontest = '{"result":true,"count":1}',
    	    //obj = JSON.parse(jsontest);

	    //alert(obj.count);
	    //alert(obj.result);

	    var json = JSON.parse(data);
	    var name_item = json["features"][0]["properties"]["name_item"]
	    var media_url = json["features"][0]["properties"]["url_media_j"]
	    //alert(json["features"][0]["properties"]["name_item"])
	    //alert(json["features"][0]["properties"]["url_media_j"])
	    //console.log(json);
            popup.setContent(name_item + " " + media_url);
	    popup.setContent('<img src="' + media_url + '" style="width:150px; height:150px;"</img> <br> <b>'+ name_item +'</b> <br>');
	    //console.log(json["url_media_j"]);
            popup.setLatLng(e.latlng);
            mymap.openPopup(popup);
        }
    });
}