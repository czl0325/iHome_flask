//模态框居中的控制
function centerModals() {
    $('.modal').each(function (i) {   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top - 30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    $(".order-comment").on("click", function () {
        var orderId = $(this).parents("li").attr("order-id");
        $(".modal-comment").attr("order-id", orderId);
    });
    // 查询房客订单
    $.get("/api/v1.0/user/orders", {
        role: "custom"
    }, function (res) {
        if (res.errno == 0) {
            $(".orders-list").html(template("orders-list-tmpl", {orders: res.data}))
            $(".order-pay").on("click", function () {
                console.log("执行...")
                let orderId = $(this).parents("li").attr("order-id");
                $.ajax({
                    url: "/api/v1.0/order/" + orderId + "/payment",
                    type: "post",
                    dataType: "json",
                    headers: {
                        "X-CSRFToken": $.cookie("csrf_token"),
                    },
                    success: function (res) {
                        if ("4101" == res.errno) {
                            location.href = "/login.html";
                        } else if (0 == res.errno) {
                            // 引导用户跳转到支付宝连接
                            location.href = res.data.pay_url;
                        }
                    }
                });
            })
        }
    })

});