function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#user-name").val(getCookie("name")||"")

    $("#form-avatar").submit(function (e) {
        e.preventDefault()

        $(this).ajaxSubmit({
            url: "/api/v1.0/user/avatar",
            type: "post",
            dataType: "json",
            data: {
                "csrf_token": getCookie("csrf_token")
            },
            success: function (res) {
                if (res.errno == 0) {
                    console.log(getCookie("avatar_url"))
                    $("#user-avatar").attr("src", getCookie("avatar_url") || "")
                } else if (res.errno == "4101") {
                    window.location = "/login.html"
                } else {
                    alert(res.errmsg)
                }
            }
        })
    });

    $("#form-name").submit(function (e) {
        e.preventDefault();

        var name = $("#user-name").val();
        if (name == null) {
            alert("请填写用户名！");
            return;
        }

        $.post("/api/v1.0/user/profile", {
            "name": name,
            "csrf_token": getCookie("csrf_token")
        }, function (res) {
            if (res.errno == 0) {
                showSuccessMsg()
            } else {
                alert(res.errmsg)
            }
        })
    })
});
