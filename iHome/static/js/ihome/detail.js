function hrefBack() {
    history.go(-1);
}

function decodeQuery() {
    let search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function updateHouseInfo(house) {
    $(".swiper-container").html(template("detail-template1", {"house": house}))
    $(".detail-con").html(template("detail-template2", {"house": house}))
    var mySwiper = new Swiper('.swiper-container', {
        loop: true,
        autoplay: 5000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    })
    if (house.isMe) {
        $(".book-house").hide()
    } else {
        $(".book-house").show()
        $(".book-house").attr("href", "/booking.html?house_id="+house.house_id)
    }
}

$(document).ready(function () {
    $(".book-house").show();
    let dict = decodeQuery()
    $.get("/api/v1.0/house/detail?id=" + dict["id"], function (res) {
        if (res.errno == 0) {
            updateHouseInfo(res.data)
        } else {
            alert(res.errmsg)
        }
    })
})