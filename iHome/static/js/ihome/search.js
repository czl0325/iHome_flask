let cur_page = 1;       // 当前页
let total_page = 1;     // 总页数
let house_data_querying = true;   // 是否正在向后台获取数据

function decodeQuery() {
    let search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        let values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function updateFilterDateDisplay() {
    let startDate = $("#start-date").val();
    let endDate = $("#end-date").val();
    let $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}

//搜索房屋列表
function updateHouseData(refresh) {
    let areaId = $(".filter-area>li.active").attr("area-id");
    if (undefined == areaId) areaId = "";
    let startDate = $("#start-date").val();
    let endDate = $("#end-date").val();
    let sortKey = $(".filter-sort>li.active").attr("sort-key");
    if (refresh) {
        cur_page = 1
    } else {
        cur_page++
    }
    let params = {
        aid: areaId,
        sd: startDate,
        ed: endDate,
        sk: sortKey,
        p: cur_page
    };
    house_data_querying = true
    $.get("/api/v1.0/house/search", params, function (res) {
        house_data_querying = false
        if (res.errno == 0) {
            if (res.data.total_page == 0) {
                $(".house-list").html("暂时没有符合您查询的房屋信息。");
            } else {
                total_page = res.data.total_page;
                if (refresh) {
                    $(".house-list").html(template("house-list-template", {houses: res.data.houses}))
                } else {
                    $(".house-list").append(template("house-list-template", {houses: res.data.houses}))
                }
            }
        }
    })
}

$(document).ready(function () {
    let queryData = decodeQuery();
    let startDate = queryData["sd"];
    let endDate = queryData["ed"];
    $("#start-date").val(startDate);
    $("#end-date").val(endDate);
    updateFilterDateDisplay();
    let areaName = queryData["aname"];
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    let $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function (e) {
        let index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function (e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function (e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function (e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })
    updateHouseData(true)

    //监听滚动到底部加载更多
    // 获取页面显示窗口的高度
    let windowHeight = $(window).height();
    window.onscroll = function () {
        let b = document.documentElement.scrollTop == 0 ? document.body.scrollTop : document.documentElement.scrollTop
        let c = document.documentElement.scrollTop == 0 ? document.body.scrollHeight : document.documentElement.scrollHeight
        // 如果滚动到接近窗口底部
        if (c - b < windowHeight + 50) {
            // 如果没有正在向后端发送查询房屋列表信息的请求
            if (!house_data_querying) {
                // 将正在向后端查询房屋列表信息的标志设置为真，
                house_data_querying = true;
                // 如果当前页面数还没到达总页数
                if (cur_page < total_page) {
                    // 向后端发送请求，查询下一页房屋数据
                    updateHouseData(false);
                } else {
                    house_data_querying = false;
                }
            }
        }
    }
})