import math
from urllib.request import urlretrieve
# // An array holds values for meters_per_pixel based on the zoom 
# level 
# metersPerPixelForZoom = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# metersPerPixelForZoom[0] = 156543.03392 
# metersPerPixelForZoom[1] = 78271.51696 
# metersPerPixelForZoom[2] = 39135.75848 
# metersPerPixelForZoom[3] = 19567.87924 
# metersPerPixelForZoom[4] = 9783.93962 
# metersPerPixelForZoom[5] = 4891.96981 
# metersPerPixelForZoom[6] = 2445.98490 
# metersPerPixelForZoom[7] = 1222.99245 
# metersPerPixelForZoom[8] = 611.49622 
# metersPerPixelForZoom[9] = 305.74811 
# metersPerPixelForZoom[10] = 152.87405 
# metersPerPixelForZoom[11] = 76.43702 
# metersPerPixelForZoom[12] = 38.21851 
# metersPerPixelForZoom[13] = 19.10925 
# metersPerPixelForZoom[14] = 9.55462 
# metersPerPixelForZoom[15] = 4.77731 
# metersPerPixelForZoom[16] = 2.38865 
# metersPerPixelForZoom[17] = 1.19432 
# metersPerPixelForZoom[18] = 0.59716 
# metersPerPixelForZoom[19] = 0.29858


# https://jsfiddle.net/john_s/BHHs8/6/
# https://jsfiddle.net/tg0mw3zr/97/
# https://maps.googleapis.com/maps/api/js?key=AIzaSyBt_MCVG-uJti3DYrnCE1ElGkA8VBIl1so
ZOOM_MAX = 21
def latRad(lat):
    sin = math.sin(lat * math.pi / 180);
    radX2 = math.log((1 + sin) / (1 - sin)) / 2;
    return max([min([radX2, math.pi]), -math.pi]) / 2;

def findZoom(mapPx, worldPx, fraction):
    return math.floor(math.log(mapPx / worldPx / fraction) / math.log(2))

deltaPixelsWidth = 600
deltaPixelsHeight = 600

worldPixelsHeight = 256
worldPixelsWidth = 256
# https://groups.google.com/g/google-maps-js-api-v3/c/hDRO4oHVSeM/m/osOYQYXg2oUJ?pli=1
# metersPerPixel = 156543.03392 * math.cos(centerLatitude * math.pi / 180) / math.pow(2, zoom)
minLatitude = 40.0
maxLatitude = 44.0
minLongitude = -75.0
maxLongitude = -65.0

centerLatitude = (minLatitude + maxLatitude) / 2
centerLongitude = (minLongitude + maxLongitude) / 2

# print(latRad(minLatitude))
latFraction = (latRad(maxLatitude) - latRad(minLatitude)) / math.pi
lngDiff = maxLongitude - minLongitude
if(lngDiff < 0):
    lngFraction = lngDiff + 360
else:
    lngFraction = lngDiff
lngFraction = lngFraction / 360
print(latFraction, lngFraction)

latZoom = findZoom(deltaPixelsHeight, worldPixelsHeight, latFraction)
lngZoom = findZoom(deltaPixelsWidth, worldPixelsWidth, lngFraction)
print("zoom", latZoom, lngZoom)

zoom = min(latZoom, lngZoom, ZOOM_MAX)
url = "https://maps.googleapis.com/maps/api/staticmap?center=" + str(centerLatitude) + "," + str(centerLongitude) + "&zoom=" + str(zoom) + "&scale=1&size=" + str(deltaPixelsWidth) + "x" + str(deltaPixelsHeight) + "&maptype=satellite&format=png&visual_refresh=true&key=AIzaSyBt_MCVG-uJti3DYrnCE1ElGkA8VBIl1so"
urlretrieve(url, "satallite.png")
quit()

metersPerPixel = metersPerPixelForZoom[zoom]

print(metersPerPixel/1000)
# print("meters length of image", metersPerPixel * size)
deltaMetersWidth = metersPerPixel * deltaPixelsWidth
deltaMetersHeight = metersPerPixel * deltaPixelsHeight
# https://stackoverflow.com/questions/56741140/given-a-long-lat-convert-meters-into-longitude-latitude-degrees
minLatitude = centerLatitude - ((deltaMetersWidth/2) / 6371008.7714) * (180 / math.pi) / math.cos(centerLatitude * math.pi/180)
maxLatitude = centerLatitude + ((deltaMetersWidth/2) / 6371008.7714) * (180 / math.pi) / math.cos(centerLatitude * math.pi/180)

minLongitude = centerLongitude - ((deltaMetersHeight/2) / 6371008.7714) * (180 / math.pi) / math.cos(centerLongitude * math.pi/180)
maxLongitude = centerLongitude + ((deltaMetersHeight/2) / 6371008.7714) * (180 / math.pi) / math.cos(centerLongitude * math.pi/180)

print("latitude bounds",math.degrees(maxLatitude), minLatitude)
print("longitude bounds", minLongitude, maxLongitude)


urlretrieve(url, "satallite.png")



# JS Code
# https://jsfiddle.net/tg0mw3zr/48/
# https://jsfiddle.net/tg0mw3zr/97/
# // Change this array to test.
# var points = [
#     { lat: 30.0, lng: -60.0 },
#     { lat: 45.0, lng: -75.0 }
# ];
# 
# function getBoundsZoomLevel(bounds, mapDim) {
#     var WORLD_DIM = { height: 256, width: 256 };
#     var ZOOM_MAX = 21;
# 
#     function latRad(lat) {
#         var sin = Math.sin(lat * Math.PI / 180);
#         var radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
#         return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
#     }
# 
#     function zoom(mapPx, worldPx, fraction) {
#         return Math.floor(Math.log(mapPx / worldPx / fraction) / Math.LN2);
#     }
# 
#     var ne = bounds.getNorthEast();
#     var sw = bounds.getSouthWest();
# 		console.log(ne.lat())
#     console.log("lat bounds and center", ne.lat(), sw.lat(), bounds.getCenter().lat())
#     console.log("lon bounds and center", ne.lng(), sw.lng(), bounds.getCenter().lng())
#     var latFraction = (latRad(ne.lat()) - latRad(sw.lat())) / Math.PI;
#     
#     var lngDiff = ne.lng() - sw.lng();
#     var lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;
#     console.log(latFraction, lngFraction)
#     
#     console.log(mapDim.height, mapDim.width)
#     var latZoom = zoom(mapDim.height, WORLD_DIM.height, latFraction);
#     var lngZoom = zoom(mapDim.width, WORLD_DIM.width, lngFraction);
#     console.log(latZoom, lngZoom)
# 
#     return Math.min(latZoom, lngZoom, ZOOM_MAX);
# }
# 
# function createMarkerForPoint(point) {
#     return new google.maps.Marker({
#         position: new google.maps.LatLng(point.lat, point.lng)
#     });
# }
# 
# function createBoundsForMarkers(markers) {
#     var bounds = new google.maps.LatLngBounds();
#     $.each(markers, function() {
#         bounds.extend(this.getPosition());
#     });
#     return bounds;
# }
# 
# var $mapDiv = $('#mapDiv');
# 
# var mapDim = {
#     height: $mapDiv.height(),
#     width: $mapDiv.width()
# }
# 
# var markers = [];
# $.each(points, function() { markers.push(createMarkerForPoint(this)); });
# 
# var bounds = (markers.length > 0) ? createBoundsForMarkers(markers) : null;
# 
# var map;
# var overlay;
# 
# function initialize() {
#     var mapOptions = {
#       center: (bounds) ? bounds.getCenter() : new google.maps.LatLng(0, 0),
#       mapTypeId: google.maps.MapTypeId.ROADMAP,
#       zoom: (bounds) ? getBoundsZoomLevel(bounds, mapDim) : 0
#     };
#     map = new google.maps.Map(document.getElementById('mapDiv'), mapOptions);
#     overlay = new google.maps.OverlayView();
#     overlay.draw = function() {};
#     overlay.setMap(map);
# }
# initialize()
# 
# google.maps.event.addListenerOnce(map,"tilesloaded", function() {
#    var projection= map.getProjection()
#    /* console.log("overlay", overlay) */
#    var overlayProjection = overlay.getProjection()
#    console.log("overlayProjection", overlayProjection);
#    console.log("projection:"+ projection);
#    console.log("map.getCenter", map.getCenter().lat(), map.getCenter().lng());
#    var centerLatLng = overlayProjection.fromLatLngToContainerPixel(map.getCenter())
#    console.log("location of center in div", centerLatLng)
#    var centerPoint = new google.maps.Point(centerLatLng.x, centerLatLng.y);
#    console.log("lat long of center", overlayProjection.fromContainerPixelToLatLng(centerPoint).toString());
#    var northEastPoint = new google.maps.Point(mapDim.width, 0);
#    var southWestPoint = new google.maps.Point(0, mapDim.height);
#    console.log("lat long of north east", overlayProjection.fromContainerPixelToLatLng(northEastPoint).toString());
#    console.log("lat long of south west", overlayProjection.fromContainerPixelToLatLng(southWestPoint).toString());
#    console.log(projection.fromContainerPixelToLatLng(point));
#    map.getProjection().fromContainerPixelToLatLng(point);
#    console.log("HI");
#    console.log("WHY", map.getProjection().fromContainerPixelToLatLng(point))
#    console.log("overlay", overlay);
#    console.log(overlay.getProjection());
#    var pixelLatLng = overlay.getProjection().fromContainerPixelToLatLng(new google.maps.Point(200,200));
#    console.log("pixelLatLng", pixelLatLng.lat());
#  }); 
# //https://stackoverflow.com/questions/7938096/google-maps-api-v3-fromdivpixeltolatlng-not-consistent
# 
# 
# 
# /* console.log(map.getBounds().lat())
# 
# $.each(markers, function() { this.setMap(map); });
# console.log(bounds.getCenter().lat())
# var neLat =  map.getBounds().getNorthEast().lat()
# var neLng =  map.getBounds().getNorthEast().lng()
# var swLat =  map.getBounds().getSouthWest().lat()
# var swLng =  map.getBounds().getSouthWest().lng()
# console.log("map bounds", neLat, neLng, swLat, swLng) */
