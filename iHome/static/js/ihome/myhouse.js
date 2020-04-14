function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
$(document).ready(function(){
    $.get("/api/v1.0/user/" + getCookie("user_id"), function (res) {
        var user = res.data
        if (user.id_card == null || user.real_name == null) {
            $(".auth-warn").show();
        }
    });
})