function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
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
    $.get("/api/v1.0/house/info", function (res) {
        alert(res.errmsg)
    })
    $("#form-house-info").submit(function (e) {
        e.preventDefault()

        var data = {}
        $(this).serializeArray().map(function (x) {
            if (x.value) {
                data[x.name] = x.value
            }
        })
        // 收集设置id信息
        var facilitity_str = "";
        $(":checked[name=facility]").each(function (index, x) {
            facilitity_str += `${$(x).val()},`
        })
        if (facilitity_str.length > 0) {
            facilitity_str = facilitity_str.substring(0, facilitity_str.length-1)
        }
        data.facility = facilitity_str
        data.csrf_token = getCookie("csrf_token")
        $.post("/api/v1.0/house/create", {
            ...data
        }, function (res) {
            if (res.errno == "4101") {
                location.href = "/login.html";
            } else if (res.errno == 0) {
                // 隐藏基本信息表单
                $("#form-house-info").hide();
                // 显示图片表单
                $("#form-house-image").show();
                // 设置图片表单中的house_id
                $("#house-id").val(res.data.house_id);
            } else {
                alert(res.errmsg)
            }
        })
    })
})