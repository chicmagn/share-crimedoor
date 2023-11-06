$(document).ready(function () {

})
let script = document.createElement('script');
script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyDVu4ZjuyPf8s-uhRPP6RGLfczaLF8hJQY&callback=initMap';
script.defer = true;

// Attach your callback function to the `window` object
window.initMap = function (lat = 4.7073, lng = 100.9381) {
    lat = lat ? result['location']['latitude'] : 0
    lng = lng ? result['location']['longitude'] : 0
    myCenter = new google.maps.LatLng(lat, lng);
    map = new google.maps.Map(document.getElementById("map"), {
        center: myCenter,
        zoom: 8
    });
    marker = new google.maps.Marker({ position: myCenter });
    marker.setMap(map)
}

// Append the 'script' element to 'head'
document.head.appendChild(script);