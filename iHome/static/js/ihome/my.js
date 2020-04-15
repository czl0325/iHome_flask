function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.get("/api/logout", function (data) {
        if (0 == data.errno) {
            location.href = "/";
        }
    })
}

$(document).ready(function () {
    let user_id = getCookie("user_id")
    if (user_id) {
        $.get("/api/v1.0/user/" + user_id, function (res) {
            if (res.errno == 0) {
                $("#user-avatar").attr("src", res.data.avatar_url)
                $("#user-name").html(res.data.name)
                $("#user-mobile").html(res.data.mobile)
            }
        })
    }
})