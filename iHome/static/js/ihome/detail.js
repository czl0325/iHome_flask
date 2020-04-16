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
    $(".detail-con").html(template("detail-template2", {"house": house}))
    var mySwiper = new Swiper('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    })
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