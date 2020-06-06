var infowindowArray = [];
var markers = [];
var subways = new Set();
var subwayData;
var centerLoc = new kakao.maps.LatLng(37.5065591, 127.018721);
var imageSize = new kakao.maps.Size(24, 35);


// 마커 이미지
var imageSrc = "https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png";
var centerImageSrc = "/static/img/pin.png";

// 마커 이미지를 생성합니다    
var markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize);
var centerMarkerImage = new kakao.maps.MarkerImage(centerImageSrc, imageSize);

var mapContainer = document.getElementById('map'), // 지도를 표시할 div 
    mapOption = {
        center: centerLoc, // 지도의 중심좌표
        level: 6 // 지도의 확대 레벨
    };

// 지도를 생성합니다    
var map = new kakao.maps.Map(mapContainer, mapOption);

// 지도에 확대 축소 컨트롤을 생성한다
var zoomControl = new kakao.maps.ZoomControl();

// 지도의 우측에 확대 축소 컨트롤을 추가한다
map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

// 마커 클러스터러를 생성합니다 
var clusterer = new kakao.maps.MarkerClusterer({
    map: map, // 마커들을 클러스터로 관리하고 표시할 지도 객체 
    averageCenter: true, // 클러스터에 포함된 마커들의 평균 위치를 클러스터 마커 위치로 설정 
    minLevel: 5 // 클러스터 할 최소 지도 레벨 
});

// Foodie items
$.get("/static/data/seoulbitz_foodie.json", function(data){
    var markers = $(data).map(function(i, d) {
        var marker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(d.Y, d.X), // 마커를 표시할 위치
            image: markerImage, // 마커 이미지
            clickable: true // 마커를 클릭했을 때 지도의 클릭 이벤트가 발생하지 않도록 설정합니다
        });
        
        // 마커에 클릭이벤트 등록
        kakao.maps.event.addListener(marker, 'click', function () {
            var content = makeInfoWindowContent(d.insta);
            var insta_embed = document.getElementById('insta-embed');
            while (insta_embed.firstChild) insta_embed.removeChild(insta_embed.firstChild);
            insta_embed.append(content);

        });
        return marker
    });
    
    clusterer.addMarkers(markers)
})

// Shopping items
$.get("/static/data/seoulbitz_shopping.json", function(data){
    var markers = $(data).map(function(i, d) {
        console.log(d)
        var marker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(d.Y, d.X), // 마커를 표시할 위치
            image: markerImage, // 마커 이미지
            clickable: true // 마커를 클릭했을 때 지도의 클릭 이벤트가 발생하지 않도록 설정합니다
        });
        
        // 마커에 클릭이벤트 등록
        kakao.maps.event.addListener(marker, 'click', function () {
            var content = makeInfoWindowContent(d.insta);
            var insta_embed = document.getElementById('insta-embed');
            while (insta_embed.firstChild) insta_embed.removeChild(insta_embed.firstChild);
            insta_embed.append(content);

        });
        return marker
    });
    
    clusterer.addMarkers(markers)
})

function iframeOnload(){
    fullpage_api.moveTo(3);
}

// 인포윈도우를 표시하는 클로저를 만드는 함수입니다 
function makeOverListener(map, marker, infowindow) {
    return function () {
        infowindow.open(map, marker);
    };
}

// 인포윈도우를 닫는 클로저를 만드는 함수입니다 
function makeOutListener(infowindow) {
    return function () {
        infowindow.close();
    };
}

// 인포윈도우 전체 닫기 
function closeInfoWindow(array) {
    for(var idx=0; idx<array.length; idx++){
        array[idx].close();
    }
}

// 모바일 기기 체크
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 인포윈도우 내용 작성 함수
function makeInfoWindowContent(insta) {

    var iframeWidth = "600";
    var iframeHeight = "800"

    if (isMobile()) { 
        iframeWidth = "350";
        iframeHeight = "405"
    }

    var link = insta + 'embed';
    var iframe = document.createElement('iframe');
    iframe.frameBorder = 0;
    iframe.width= iframeWidth;
    iframe.height = iframeHeight;
    iframe.setAttribute("src", link);
    iframe.onload = iframeOnload;

    return iframe;
}

function panTo(moveLatLon) {   
    // 지도 중심을 부드럽게 이동시킵니다
    // 만약 이동할 거리가 지도 화면보다 크면 부드러운 효과 없이 이동합니다
    map.panTo(moveLatLon);            
}     

function init(centerLoc) {
    // 마커를 생성합니다
    var marker = new kakao.maps.Marker({
        position: centerLoc, // 마커를 표시할 위치
        image: centerMarkerImage, // 마커 이미지
    });

    markers.push(marker);

    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
        if (i == markers.length -1) {
            markers[i].setMap(map);
        }
    } 
}

function getLocation() {
    if (navigator.geolocation) { // GPS를 지원하면
      navigator.geolocation.getCurrentPosition(function(position) {
        var gpsX = position.coords.latitude
        var gpsY = position.coords.longitude

        var centerLoc = new kakao.maps.LatLng(gpsX, gpsY);
        init(centerLoc);
        map.panTo(centerLoc);

      }, function(error) {
        console.error(error);
        init(centerLoc);
        map.panTo(centerLoc);
      }, {
        enableHighAccuracy: false,
        maximumAge: 0,
        timeout: Infinity
      });
    } else {
      console.log('GPS를 지원하지 않습니다');
    }
  }

function getSubwayList(){
    $.get('/static/data/subway.json', function(data){
        subwayData = data.DATA;
        $.each(data.DATA, function(i,d) {
            subways.add(d.station_nm);
        });
        subways = Array.from(subways); 
        subwayAutoCompelete();
    });

    
}


function subwayAutoCompelete(){
    $('#subway_input').autocomplete({
        source : subways,
        select : function(e, ui){
            subwaySearch(ui.item.value);
        },
        focus : function(e, ui){
            return false;
        },
        minLength: 1,
        autoFocus: true,
        classes:{
            "ui-autocomplete": "highlight"
        },
        delay: 500,
        disabled: false,
        position: {
            my : "right top",
            at : "right bottom"
        },
        close : function(e){
        }
    });
}

function subwaySearch(query) {
    var query = query.replace('역','');
    $.each(subwayData, function(i,d) {
        if (subwayData[i].station_nm == query){
            var centerLoc = new kakao.maps.LatLng(subwayData[i].xpoint_wgs, subwayData[i].ypoint_wgs);
            panTo(centerLoc);
            init(centerLoc);
            fullpage_api.moveTo(2);
        };
    });
}

function wrapWindowByMask(){
    //화면의 높이와 너비를 구한다.
    var maskHeight = $('.section-map').height();  
    var maskWidth = $('.section-map').width();  
    
    //마스크의 높이와 너비를 화면 것으로 만들어 전체 화면을 채운다.
    $('#mask').css({'width':maskWidth,'height':maskHeight});  
    
    //애니메이션 효과
    $('#mask').fadeTo('fast',0.8);

}

//주소로 좌표 검색
var addressSearch = function (data) {
    // 주소-좌표 변환 객체를 생성합니다
	var geocoder = new kakao.maps.services.Geocoder();
	
    geocoder.addressSearch(data.addr, function (result, status) {
        // 정상적으로 검색이 완료됐으면 
        if (status === kakao.maps.services.Status.OK) {

            // 마커를 생성합니다
            var marker = new kakao.maps.Marker({
                map: map, // 마커를 표시할 지도
                position: new kakao.maps.LatLng(result[0].y, result[0].x), // 마커를 표시할 위치
                image: markerImage, // 마커 이미지
                clickable: true // 마커를 클릭했을 때 지도의 클릭 이벤트가 발생하지 않도록 설정합니다
            });

            infowindowArray.push(infowindow);

            // 마커에 mouseover 이벤트와 mouseout 이벤트를 등록합니다
            // 이벤트 리스너로는 클로저를 만들어 등록합니다 
            // for문에서 클로저를 만들어 주지 않으면 마지막 마커에만 이벤트가 등록됩니다
            // kakao.maps.event.addListener(marker, 'mouseover', makeOverListener(map, marker, infowindow));
            // kakao.maps.event.addListener(marker, 'mouseout', makeOutListener(infowindow));

            // 마커에 표시할 인포윈도우를 생성합니다 
            var infowindow = new kakao.maps.InfoWindow({
                content: makeInfoWindowContent(data) // 인포윈도우에 표시할 내용
            });
            // 마커에 클릭이벤트 등록
            kakao.maps.event.addListener(marker, 'click', function () {
                closeInfoWindow(infowindowArray);
                // 마커 위에 인포윈도우를 표시합니다
                infowindow.open(map, marker);
            });

            // 맵에 클릭이벤트 등록
            kakao.maps.event.addListener(map, 'click', function () {
                // 마커 위에 인포윈도우를 표시합니다
                infowindow.close();
            });
        }
    })
}

