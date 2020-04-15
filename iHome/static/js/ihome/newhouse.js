function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get("/api/v1.0/area", function (res) {
        if (res.errno == 0) {
            var html = template("area-template", {areas: res.data})
            $("#area-id").html(html)
        } else {
            alert(res.errmsg)
        }
    })
    $.get("/api/v1.0/facility", function (res) {
        if (res.errno == 0) {
            var html = template("facility-template", {facilities: res.data})
            $("#facility-ul").html(html)
        } else {
            alert(res.errmsg)
        }
    })
    $("#form-house-info").submit(function (e) {
        e.preventDefault()


    })
})