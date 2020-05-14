function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

$(document).ready(function () {
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function () {
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg();
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd) / (1000 * 3600 * 24) + 1;
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共" + days + "晚)");
        }
    });
    let params = decodeQuery()
    $(".submit-btn").on("click", function () {
        if ($(".order-amount>span").html()) {
            $(this).prop("disabled", true)
            let start_date = $("#start-date").val()
            let end_date = $("#end-date").val()
            $.post("/api/v1.0/order/save", {
                house_id: params.house_id,
                "start_date": start_date,
                "end_date": end_date,
                "csrf_token": getCookie("csrf_token")
            }, function (res) {
                if ("4101" == res.errno) {
                    window.location = "/login.html";
                } else if ("4004" == res.errno) {
                    showErrorMsg("房间已被抢定，请重新选择日期！");
                } else if (0 == res.errno) {
                    window.location = "/orders.html";
                }
            })
        }
    })
    $.get("/api/v1.0/house/detail", {
        id: params.house_id
    }, function (res) {
        $(".house-info").html(template("house-template", {house: res.data}))
    })
})
