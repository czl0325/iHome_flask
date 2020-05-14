function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function () {
    let param = decodeQuery()
    $("#pay-finish").on("click", function () {

        let orderId = param["out_trade_no"]
        $.ajax({
            url: "/api/v1.0/order/" + orderId + "/status",
            type: "PUT",
            data: {action: "payment"},
            dataType: "json",
            headers: {"X-CSRFTOKEN": $.cookie("csrf_token")},
            success: function (res) {
                if (res.errno == 0) {
                    window.location = "/"
                } else {
                    alert(res.errmsg)
                }
            }
        })
    })
})