function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function logout() {
    $.get("/api/logout", function(data){
        if (0 == data.errno) {
            location.href = "/";
        }
    })
}

$(document).ready(function(){
    $("#user-avatar").attr("src", getCookie("avatar_url") || "")
    $("#user-name").html(getCookie("name") || "")
    $("#user-mobile").html(getCookie("mobile") || "")
})