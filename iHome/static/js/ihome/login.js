function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        password = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        let csrf_token = getCookie("csrf_token")
        $.post("/api/v1.0/user/login", {
            mobile: mobile,
            password: password,
            csrf_token: csrf_token
        }, function (res) {
            if (res.errno == 0) {
                window.location = "/index.html"
            } else {
                alert(res.errmsg)
            }
        })
    });
})