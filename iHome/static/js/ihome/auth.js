function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function () {
    $("#real-name").val(getCookie("real_name") || "");
    $("#id-card").val(getCookie("id_card") || "");

    $("#form-auth").submit(function (e) {
        e.preventDefault()

        real_name = $("#real-name").val();
        id_card = $("#id-card").val();
        if (!real_name || !id_card) {
            $(".error-msg").show();
            return;
        }

        $.post("/api/v1.0/user/profile", {
            "real_name": real_name,
            "id_card": id_card,
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

