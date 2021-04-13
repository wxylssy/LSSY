const wsCmdURL = 'ws://' + window.location.host + '/CmdWebSocket';
//涨速条件
const speed_60s = 2;
var wsTick;
var wsChengjiao;
var gp_row_data;

const datetimeFormat = d3.timeFormat("%Y%m%d %H:%M:%S");
const datetimeParse = d3.timeParse("%Y%m%d %H:%M:%S");
const dateFormat = d3.timeFormat("%Y%m%d");
const dateParse = d3.timeParse("%Y%m%d");

const show_success = function (title, msg) {
    var md = $('#info_toast');
    md.removeClass('border-danger');
    md.addClass('border-success');
    md.find('.toast-body').find('img').attr('src', 'img/success.png');
    md.find('.toast-body').find('span').text(msg);
    md.find('.mr-auto').text(title);
    md.toast('show');
};

const show_error = function (title, msg) {
    var md = $('#info_toast');
    md.removeClass('border-success');
    md.addClass('border-danger');
    md.find('.toast-body').find('img').attr('src', 'img/error.png');
    md.find('.toast-body').find('span').text(msg);
    md.find('.mr-auto').text(title);
    md.toast('show');
};

const setbz = function (code, v){
    $.ajax({
            type: 'get',
            cache: false,
            url: `/SetBz?code=${code}&bz=${v}`,
            success: function (data) {
                show_success('设置成功', data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
            }
        });
};

const getTicksDay = function (code, d){
    show_success('获取Ticks', '请稍候...');
    $('#modal_tick').modal('hide');
    $.ajax({
            type: 'get',
            cache: false,
            url: `/GetTicks?code=${code}&date=${d}`,
            success: function (data) {
                show_success('获取Ticks', data);
                gp_row_data.datetime = datetimeFormat(dateParse(d));
                showTick(gp_row_data);
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                show_error(XMLHttpRequest.status, XMLHttpRequest.responseText);
            }
        });
};

const format_datetime = function (data, date_val_name) {
    data.forEach(function (d_temp) {
        d_temp[date_val_name] = datetimeParse(d_temp[date_val_name]);
    });
};

const showTick = function (row_data) {
    gp_row_data = row_data;

    $("#tick").find("svg").remove();
    $("#kline_day").find("svg").remove();
    $('#tickTable').DataTable().clear().draw();
    $("#finance_profit").find("svg").remove();
    $("#finance_growth").find("svg").remove();
    $("#finance_balance").find("svg").remove();
    $("#finance_operation").find("svg").remove();
    $("#finance_cash_flow").find("svg").remove();
    $("#baseinfo").find("svg").remove();

    $('#modal_tick').modal('show')

    $.ajax({
        type: 'get',
        cache: false,
        url: '/Get_ky_balance',
        success: function (data) {
            $('#modal_tick').find('.modal-title').text(`${gp_row_data.code} ${gp_row_data.name}（${gp_row_data.hangye}） 账户可用资金：${data}`);
        }
    });

    $.ajax({
        type: 'get',
        cache: false,
        url: '/GetKline?code=' + row_data.code + '&date=' + row_data.datetime,
        success: function (data) {
            drawKline("#kline_day", JSON.parse(data));
        }
    });

    $.ajax({
        type: 'get',
        cache: false,
        url: '/GetBaseinfo?code=' + row_data.code,
        success: function (data) {
            data_j = JSON.parse(data);
            format_datetime(data_j.finance.profit, 'statDate');
            format_datetime(data_j.finance.operation, 'statDate');
            format_datetime(data_j.finance.growth, 'statDate');
            format_datetime(data_j.finance.balance, 'statDate');
            format_datetime(data_j.finance.cash_flow, 'statDate');
            drawProfit(data_j.finance);
            drawGrowth(data_j.finance);
            drawBalance(data_j.finance);
            drawOperation(data_j.finance);
            drawCashflow(data_j.finance);
            drawBaseinfo(data_j.cgbl);
        }
    });

    wsTick = new WebSocket(wsCmdURL);

    wsTick.onopen = function () {
        var cmdData = {
            'cmd': 1,
            'code': gp_row_data.code
        };
        wsTick.send(JSON.stringify(cmdData));
    };

    wsTick.onmessage = function (e) {
        datas = JSON.parse(e.data);
        if (datas.length > 0) {
            format_datetime(datas, 'datetime');
            var table = $('#tickTable').DataTable();
            table.rows.add(datas).draw(false);
            $("#tick").find("svg").remove();
            drawTick("#tick", table.rows().data());
        }
    };

    wsTick.onclose = function (e) {

    };

    wsTick.onerror = function (e) {

    };
};

const startChengjiaoUpdate = function () {
    wsChengjiao = new WebSocket(wsCmdURL);

    wsChengjiao.onopen = function () {
        var cmdData = {
            'cmd': 2
        };
        wsChengjiao.send(JSON.stringify(cmdData));
    };

    wsChengjiao.onmessage = function (e) {
        var data = JSON.parse(e.data);
        if (data.status == 0) {
            $('#buy').attr('disabled', 'disabled');
            $('#sell').attr('disabled', 'disabled');
            $('#cancelOderAll').attr('disabled', 'disabled');
            $('#cjLoading').show();
            return;
        }
        $('#cjLoading').hide();
        $('#cancelOderAll').removeAttr("disabled");
        $('#sell').removeAttr("disabled");
        $('#buy').removeAttr("disabled");
        var wttable = $('#wtTable').DataTable();
        wttable.clear();
        wttable.rows.add(data.wt).draw();
    };

    wsChengjiao.onclose = function (e) {

    };

    wsChengjiao.onerror = function (e) {

    };
};

const stopChengjiaoUpdate = function () {
    if (wsChengjiao) {
        var cmdData = {
            'cmd': 999
        };
        wsChengjiao.send(JSON.stringify(cmdData));
    }
};

const connectQuotation = function () {
    var dateParse = d3.timeParse("%Y%m%d %H:%M:%S.%L");
    var dateFormat = d3.timeFormat("%Y%m%d %H:%M:%S.%L");
    $('#last_time').text(dateFormat(new Date()));

    var wsObj = new WebSocket(wsCmdURL);

    wsObj.onopen = function () {
        var cmdData = {
            'cmd': 0
        };
        wsObj.send(JSON.stringify(cmdData));
    };

    wsObj.onmessage = function (e) {
        var data = JSON.parse(e.data);
        data.sort(function (a, b) {
            if (Object.keys(a.chicang).length > 0 && Object.keys(b.chicang).length > 0) {
                return 0;
            } else if (Object.keys(a.chicang).length > 0) {
                return -1;
            } else if (Object.keys(b.chicang).length > 0) {
                return 1;
            }
            if (a.bz > 0 && b.bz > 0){
                return 0;
            }else if(a.bz > 0){
                return -1;
            }else if(b.bz > 0){
                return 1;
            }
            if (Object.keys(a.catch_zt).length > 0 && Object.keys(b.catch_zt).length > 0) {
                return a.catch_zt.time - b.catch_zt.time;
            } else if (Object.keys(a.catch_zt).length > 0) {
                return -1;
            } else if (Object.keys(b.catch_zt).length > 0) {
                return 1;
            }
            return b.bi_amount_60s_1_max_num - a.bi_amount_60s_1_max_num;
        });
        var table = $('#mainTableQuotation').DataTable();
        var tb_len = table.rows().data().length;
        var qx_total = 0;
        var cc_total = 0;
        if (data.length != tb_len) {
            table.clear();
            table.rows.add(data).draw();
        } else {
            for (var i = 0; i < data.length; i++) {
                if (Object.keys(data[i].chicang).length > 0)
                {
                    cc_total++;
                }else{
                    if (data[i].qx > 0)
                        qx_total++;
                }
                table.row(i).data(data[i]);
            }
        }
        //计算市场情绪
        var ld = data.length - cc_total - qx_total;
        if (ld == 0)
            ld = 1;
        var qx = (qx_total / ld).toFixed(2);
        var html = qx;
        if (qx > 1){
            html = "<span class=\"text-danger\">" + qx + "</span>";
        }
        $('#info_schyd').html(html);

        var t = dateParse($('#last_time').text());
        var n = new Date();
        $('#info_y').text((n.getTime() - t.getTime()) + 'ms')
        $('#last_time').text(dateFormat(n));
    };

    wsObj.onclose = function (e) {

    };

    wsObj.onerror = function (e) {

    };
};