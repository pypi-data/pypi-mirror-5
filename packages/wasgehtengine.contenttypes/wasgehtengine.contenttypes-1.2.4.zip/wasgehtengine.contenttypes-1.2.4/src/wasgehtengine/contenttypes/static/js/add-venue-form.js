function init() {

		$('<div id="map" />').insertAfter('#formfield-form-widgets-longitude')

		map = new OpenLayers.Map("map");
		map.addLayer(new OpenLayers.Layer.OSM());

		var lonLatCenter = new OpenLayers.LonLat( 7.100013444518991 , 50.73435432371313 ).transform(
			new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
			map.getProjectionObject() // to Spherical Mercator Projection
			);

		var zoom=13;

		map.setCenter (lonLatCenter, zoom);

		var markers = new OpenLayers.Layer.Markers( "Markers" );
		map.addLayer(markers);

		marker = new OpenLayers.Marker(lonLatCenter);

		markers.addMarker(marker);

		OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {                
			defaultHandlerOptions: {
				'single': true,
			'double': false,
			'pixelTolerance': 0,
			'stopSingle': false,
			'stopDouble': false
			},

			initialize: function(options) {
				this.handlerOptions = OpenLayers.Util.extend(
					{}, this.defaultHandlerOptions
					);
				OpenLayers.Control.prototype.initialize.apply(
					this, arguments
					); 
				this.handler = new OpenLayers.Handler.Click(
					this, {
						'click': this.trigger
					}, this.handlerOptions
					);
			}, 

			trigger: function(e) {
				var lonlat = map.getLonLatFromViewPortPx(e.xy).transform(new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326"));

				document.getElementById("form-widgets-latitude").value = lonlat.lat;
				document.getElementById("form-widgets-longitude").value = lonlat.lon;

				var newPx = map.getLayerPxFromViewPortPx(e.xy);
				marker.moveTo(newPx);

			}

		});

		click = new OpenLayers.Control.Click();
		map.addControl(click);

		click.activate();
	}

	$("#latitude, #longitude").change(function(e) {

		var lonLat = new OpenLayers.LonLat( $("#longitude").val(),$("#latitude").val())
		.transform(
			new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
			map.getProjectionObject() // to Spherical Mercator Projection
			);

		var newPx = map.getLayerPxFromLonLat(lonLat);
		marker.moveTo(newPx);
		map.moveTo(lonLat);
	}
);


// Initialize when DOM is loaded
$(document).ready(init);