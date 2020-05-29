var infowindowArray = [];
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


$.get("/static/seoulbitz.json", function(data){
    var markers = $(data).map(function(i, d) {
        var marker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(d.Y, d.X), // 마커를 표시할 위치
            image: markerImage, // 마커 이미지
            clickable: true // 마커를 클릭했을 때 지도의 클릭 이벤트가 발생하지 않도록 설정합니다
        });
        
        // 마커에 표시할 인포윈도우를 생성합니다 
        var infowindow = new kakao.maps.InfoWindow({
            content: makeInfoWindowContent(d.insta) // 인포윈도우에 표시할 내용
        });

        infowindowArray.push(infowindow);

        // 마커에 클릭이벤트 등록
        kakao.maps.event.addListener(marker, 'click', function () {
            closeInfoWindow(infowindowArray);
            // 마커 위에 인포윈도우를 표시합니다
            infowindow.open(map, marker);
        });

        // 맵에 클릭이벤트 등록
        kakao.maps.event.addListener(map, 'click', function () {
            // 인포윈도우를 초기화
            infowindow.close();
        });
        return marker
    });
    
    clusterer.addMarkers(markers)
})

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

    var iframeWidth = "300";
    var iframeHeight = "500"

    if (isMobile()) { 
        iframeWidth = "600";
        iframeHeight = "800"
    }

    var content = '<iframe src="' + insta + 'embed" width="'+ iframeWidth +'" height="'+ iframeHeight + '" frameborder="0" scrolling="no" allowtransparency="true"></iframe>'
    return content;
}

function init(centerLoc) {
    if (isMobile()) {
        console.log("모바일");
    }
    else {
        console.log("PC");
    }
    // 마커를 생성합니다
    var marker = new kakao.maps.Marker({
        map: map, // 마커를 표시할 지도
        position: centerLoc, // 마커를 표시할 위치
        image: centerMarkerImage, // 마커 이미지
    });
}


// 주소로 좌표 검색
// var addressSearch = function (data) {
//     // 주소-좌표 변환 객체를 생성합니다
// 	var geocoder = new kakao.maps.services.Geocoder();
	
//     geocoder.addressSearch(data.addr, function (result, status) {
//         // 정상적으로 검색이 완료됐으면 
//         if (status === kakao.maps.services.Status.OK) {

//             // 마커를 생성합니다
//             var marker = new kakao.maps.Marker({
//                 map: map, // 마커를 표시할 지도
//                 position: new kakao.maps.LatLng(result[0].y, result[0].x), // 마커를 표시할 위치
//                 image: markerImage, // 마커 이미지
//                 clickable: true // 마커를 클릭했을 때 지도의 클릭 이벤트가 발생하지 않도록 설정합니다
//             });

//             infowindowArray.push(infowindow);

//             // 마커에 mouseover 이벤트와 mouseout 이벤트를 등록합니다
//             // 이벤트 리스너로는 클로저를 만들어 등록합니다 
//             // for문에서 클로저를 만들어 주지 않으면 마지막 마커에만 이벤트가 등록됩니다
//             // kakao.maps.event.addListener(marker, 'mouseover', makeOverListener(map, marker, infowindow));
//             // kakao.maps.event.addListener(marker, 'mouseout', makeOutListener(infowindow));

//             // 마커에 표시할 인포윈도우를 생성합니다 
//             var infowindow = new kakao.maps.InfoWindow({
//                 content: makeInfoWindowContent(data) // 인포윈도우에 표시할 내용
//             });
//             // 마커에 클릭이벤트 등록
//             kakao.maps.event.addListener(marker, 'click', function () {
//                 closeInfoWindow(infowindowArray);
//                 // 마커 위에 인포윈도우를 표시합니다
//                 infowindow.open(map, marker);
//             });

//             // 맵에 클릭이벤트 등록
//             kakao.maps.event.addListener(map, 'click', function () {
//                 // 마커 위에 인포윈도우를 표시합니다
//                 infowindow.close();
//             });
//         }
//     })
// }

