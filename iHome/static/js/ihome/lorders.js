//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    $(".order-accept").on("click", function(){
        var orderId = $(this).parents("li").attr("order-id");
        $(".modal-accept").attr("order-id", orderId);
    });
    $(".order-reject").on("click", function(){
        var orderId = $(this).parents("li").attr("order-id");
        $(".modal-reject").attr("order-id", orderId);
    });
    $.get("/api/v1.0/user/orders", {
        role: "landlord"
    }, function (res) {
        if (res.errno == 0) {
            $(".orders-list").html(template("orders-list-tmpl", {orders:res.data}));
            //接单点击事件
            $(".order-accept").on("click", function () {
                let order_id = $(this).parents("li").attr("order-id")
                $(".modal-accept").attr("order-id", order_id)
            })
            $(".modal-accept").on("click", function () {
                var orderId = $(this).attr("order-id");
                $.ajax({
                    url: "/api/v1.0/order/" + orderId + "/status",
                    type: "PUT",
                    data: { action: "accept" },
                    dataType: "json",
                    headers: { "X-CSRFTOKEN":$.cookie("csrf_token") },
                    success: function (res) {
                        if (res.errno == "4101") {
                            window.location = "/login.html"
                        } else if (res.errno == 0) {
                            $("#accept-modal").modal("hide")
                            $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul>li:eq(4)>span").html("已接单")
                            $(".orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide()
                        }
                    }
                })
            })
            //拒单点击事件
            $(".order-reject").on("click", function(){
                let orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });
            $(".modal-reject").on("click", function () {
                let orderId = $(this).attr("order-id");
                let reject_reason = $("#reject-reason").val()
                if (!reject_reason) {
                    alert("拒单原因必填")
                }
                $.ajax({
                    url: "/api/v1.0/order/" + orderId + "/status",
                    type: "PUT",
                    data: { action: "reject", reason: reject_reason },
                    dataType: "json",
                    headers: { "X-CSRFTOKEN":$.cookie("csrf_token") },
                    success: function (res) {
                        if (res.errno == "4101") {
                            window.location = "/login.html"
                        } else if (res.errno == 0) {
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            $("#reject-modal").modal("hide");
                        }
                    }
                })
            })
        }
    })
});