$(document).ready(function () {
    // 表格创建
    createMainTable('#mainTableQuotation');
    createTickTable('#tickTable');
    createChengjiaoTable('#wtTable', [
        {
            "data": "datetime",
            "title": "委托时间",
        },
        {
            "data": "code",
            "title": "代码",
        },
        {
            "data": "name",
            "title": "名称",
        },
        {
            "data": "cz",
            "title": "操作",
        },
        {
            "data": "price",
            "title": "委托价格",
        },
        {
            "data": "tol",
            "title": "数量",
        },
        {
            "data": "cjtol",
            "title": "成交数量",
        },
        {
            "data": "cjprice",
            "title": "成交均价",
        }
    ]);
    // 主行情链接
    connectQuotation();

    // 买入
    $('#buy').click(function () {
        var cangwei = parseFloat($('#buyCangwei').val());
        if (!(cangwei > 0 && cangwei <= 1))
            return;
        $('#buy').attr('disabled', 'disabled');
        $.ajax({
            type: 'get',
            cache: false,
            url: `/Buy?code=${gp_row_data.code}&cangwei=${cangwei}`,
            success: function (data) {
                //获取成交
                startChengjiaoUpdate();
                show_success('买入成功', data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
                $('#buy').removeAttr("disabled");
            },
            complete: function (XMLHttpRequest, status) {
                $('#buyModal').modal('hide');
            }
        });
    });

    // 卖出
    $('#sell').click(function () {
        $('#sell').attr('disabled', 'disabled');
        $.ajax({
            type: 'get',
            cache: false,
            url: `/Sell?code=${gp_row_data.code}`,
            success: function (data) {
                //获取成交
                startChengjiaoUpdate();
                show_success('卖出成功', data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
                $('#sell').removeAttr("disabled");
            },
            complete: function (XMLHttpRequest, status) {
                $('#sellModal').modal('hide');
            }
        });
    });

    // 全撤
    $('#cancelOderAll').click(function () {
        $('#cancelOderAll').attr('disabled', 'disabled');
        $.ajax({
            type: 'get',
            cache: false,
            url: '/CancelOderAll',
            success: function (data) {
                show_success('撤单成功', data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
            },
            complete: function (XMLHttpRequest, status) {
                $('#cancelModal').modal('hide');
                $('#cancelOderAll').removeAttr("disabled");
            }
        });
    });

    // 今日复盘
    $('#fupan').click(function () {
        $('#fupan').attr('disabled', 'disabled');
        $.ajax({
            type: 'get',
            cache: false,
            url: '/FuPan',
            success: function (data) {
                show_success('复盘', data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
            },
            complete: function (XMLHttpRequest, status) {
                $('#fupan').removeAttr("disabled");
            }
        });
    });

    // 回测
    $('#backtest').click(function () {
        $('#backtest').attr('disabled', 'disabled');
        $.ajax({
            type: 'get',
            cache: false,
            url: `/QuotationPlayback?start_date=${$('#backtestDate1').val()}&end_date=${$('#backtestDate2').val()}`,
            success: function (data) {
                show_success('回测开始', data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
                $('#backtest').removeAttr("disabled");
            },
            complete: function (XMLHttpRequest, status) {
                //$('#backtest').removeAttr("disabled");
            }
        });
    });
    var dateformt = d3.timeFormat("%Y-%m-%d");
    var start_date = new Date();
    $('#backtestDate1').val(dateformt(start_date.setDate(start_date.getDate() - 365)));
    $('#backtestDate2').val(dateformt(new Date()));

    // 主表格行点击
    $('#mainTableQuotation').on('click', 'tr', function () {
        var table = $('#mainTableQuotation').DataTable();
        table.$('tr.table-active').removeClass('table-active');
        $(this).addClass('table-active');

        var row_data = table.row(this).data();
        if (Object.keys(row_data.chicang).length > 0 && row_data.chicang.status == 0) {
            $('#btnTogSell').removeAttr("disabled");
        } else {
            $('#btnTogSell').attr('disabled', 'disabled');
        }
        showTick(row_data);
    });
});