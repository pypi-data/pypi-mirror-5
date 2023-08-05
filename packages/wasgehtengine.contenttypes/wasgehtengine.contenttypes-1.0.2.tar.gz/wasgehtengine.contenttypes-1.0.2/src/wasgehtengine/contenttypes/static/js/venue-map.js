function init() {
	var location = [$("#geo-position #latitude").text(), $("#geo-position #longitude").text()];	
	var latitude = $("#geo-position #latitude").text();
	var longitude = $("#geo-position #longitude").text();
	var venueName = $("#venueName").text();

	$("#geo-position").hide()

	// create a map in the "map" div, set the view to a given place and zoom
	var map = L.map('map').setView([latitude, longitude], 16);

	// add an OpenStreetMap tile layer
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);

	// add a marker in the given location, attach some popup content to it and open the popup
	L.marker(location).addTo(map)
	    .bindPopup(venueName)
	    .openPopup();
};	
	
// Initialize when DOM is loaded
$(document).ready(init);