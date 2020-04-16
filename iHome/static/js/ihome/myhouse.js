function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    let user_id = getCookie("user_id")
    if (user_id) {
        $.get("/api/v1.0/user/" + user_id, function (res) {
            let user = res.data
            if (user.id_card == null || user.real_name == null) {
                $(".auth-warn").show();
            }
        });
        $.get("/api/v1.0/user/houses?uid=" + user_id, function (res) {
            if (res.errno == 0) {
                let html = template("my-house-template", {houses: res.data})
                $("#houses-list").html(html)
            } else {
                alert(res.errmsg)
            }
        })
    } else {
        $(".auth-warn").show();
    }
})