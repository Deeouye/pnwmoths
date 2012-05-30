jQuery(window).load(function() {
    // Initialize our map
    var mapDiv = jQuery("#googlemap");
    mapDiv.show();
    var centerPoint = new google.maps.LatLng(46.9, -118.0);
    var options = {
                zoom: 4,
                streetViewControl: false,
                center: centerPoint,
                mapTypeId: 'terrain'
    };  
    var map = new google.maps.Map(mapDiv[0], options);

    // Create our polygon boundaries with hole
    var everythingElse = [
                new google.maps.LatLng(-87, 120),
                new google.maps.LatLng(-87, -87),
                new google.maps.LatLng(-87, 0)];
    var pnw = [
              new google.maps.LatLng(39, -126),
              new google.maps.LatLng(52.3, -130),
              new google.maps.LatLng(52.3, -109.0),
              new google.maps.LatLng(39, -109.0)];
    var polygon = new google.maps.Polygon({
              paths: [everythingElse, pnw],
              strokeColor: "#003F87",
              strokeOpacity: 0.9,
              strokeWeight: 2,
              fillColor: "#000000",
              fillOpacity: .1
            });
    polygon.setMap(map);

    // Show all coords from fusion table (needs to be updated on occasion)
    var allcoords = new google.maps.FusionTablesLayer({
      query: {
        select: 'location',
        from: '3454735'
      },
      clickable: false
    });
    allcoords.setMap(map);
});