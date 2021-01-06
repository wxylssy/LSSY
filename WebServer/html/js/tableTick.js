const createTickTable = function (id) {
    $(id).DataTable({
        columns: [
            {
                "data": 'catch_zt',
                'title': '标记',
                'orderable': false,
                render: function (data, type, row) {
                    var html = '';
                    if (Object.keys(data).length > 0) {
                        var zdf = (row.price / data.price - 1) * 100;
                        zdf = zdf.toFixed(2);
                        if (zdf > 0) {
                            html += "<span class=\"badge badge-danger\">" + zdf + "</span>";
                        } else if (zdf < 0) {
                            html += "<span class=\"badge badge-success\">" + zdf + "</span>";
                        } else {
                            html += "<span class=\"badge badge-secondary\">" + zdf + "</span>";
                        }
                    }
                    if (Object.keys(row.chicang).length > 0) {
                        var zdf = (row.price / row.chicang.price - 1) * 100;
                        zdf = zdf.toFixed(2);
                        if (row.chicang.status == 1) {
                            zdf = (row.chicang.sell_price / row.chicang.price - 1) * 100;
                            zdf = zdf.toFixed(2);
                            html += "<span class=\"badge badge-info\">卖出" + zdf + "</span>";
                        } else if(row.chicang.status == 2){
                            html += "<span class=\"badge badge-info\">锁定" + zdf + "</span>";
                        } else {
                            html += "<span class=\"badge badge-warning\">持仓" + zdf + "</span>";
                        }
                    }
                    return html;
                }
            },
            {
                "data": "code",
                "title": "代码",
                'orderable': false,
                "class": "text-center",
            },
            {
                'data': 'datetime',
                'title': '时间',
                render: function (data, type, row) {
                    return datetimeFormat(data);
                }
            },
            {
                "data": 'price',
                'title': '价格',
                'orderable': false,
            },
            {
                "data": 'zdf',
                'title': '涨跌幅',
                'orderable': false,
                render: function (data, type, row) {
                    if (data > 0) {
                        return "<span class=\"text-danger\">" + data + "</span>";
                    } else if (data < 0) {
                        return "<span class=\"text-success\">" + data + "</span>";
                    } else {
                        return data;
                    }
                }
            },
            {
                "data": 'zdf_diff',
                'title': '涨跌幅变化',
                render: function (data, type, row) {
                    if (data > 0) {
                        return "<span class=\"text-danger\">" + data + "</span>";
                    } else if (data < 0) {
                        return "<span class=\"text-success\">" + data + "</span>";
                    } else {
                        return data;
                    }
                }
            },
            {
                "data": 'zdf_diff_count',
                'title': '涨跌幅连续',
                render: function (data, type, row) {
                    if (data > 0) {
                        return "<span class=\"text-danger\">" + data + "</span>";
                    } else if (data < 0) {
                        return "<span class=\"text-success\">" + data + "</span>";
                    } else {
                        return data;
                    }
                }
            },
            {
                'data': 'zdf_open',
                'title': '开盘涨跌幅',
                'orderable': false,
                render: function (data, type, row) {
                    if (data > 0) {
                        return "<span class=\"text-danger\">" + data + "</span>";
                    } else if (data < 0) {
                        return "<span class=\"text-success\">" + data + "</span>";
                    } else {
                        return data;
                    }
                }
            },
            {
                'data': 'bi_amount_open',
                'title': '开盘量比',
                'orderable': false,
            },
            {
                'data': 'bi_amount_open_last',
                'title': '开盘量比昨日开盘',
                'orderable': false,
            },
            {
                "data": 'bi_amount',
                'title': '量比',
                'orderable': false,
            },
            {
                'data': 'speed_60s',
                'title': '速度',
                'orderable': false,
                render: function (data, type, row) {
                    if (data >= speed_60s) {
                        //var t = "<div class=\"alert bg-danger float-left rounded-pill\" role=\"alert\"><strong>" + row.code + "</strong> 符合条件，请立即查看。</div>";
                        //$('#zs').append(t);
                        return "<div class='container bg-danger'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'bi_amount_60s',
                'title': '资金驱动',
                'orderable': false,
                render: function (data, type, row) {
                    if (data >= 5) {
                        return "<span class=\"text-danger\">" + data + "</span>";
                    }
                    return data;
                }
            },
            {
                'data': 'bi_amount_60s_1',
                'title': '资金驱动比昨日',
                'orderable': false,
                render: function (data, type, row) {
                    if (data >= 5) {
                        return "<div class='container bg-success'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'bi_num_60s',
                'title': '订单驱动',
                'orderable': false,
                render: function (data, type, row) {
                    if (data >= 2) {
                        return "<div class='container bg-info'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'num',
                'title': '订单',
                'orderable': false,
                render: $.fn.dataTable.render.number(',', '.')
            },
            {
                'data': 'nums',
                'title': '总订单',
                'orderable': false,
                render: $.fn.dataTable.render.number(',', '.')
            },
            {
                'data': 'max_speed_60s',
                'title': '最大涨速',
                'orderable': false,
                render: function (data, type, row) {
                    if (data >= speed_60s) {
                        return "<div class='container bg-warning'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'bi_amount_60s_1_max_total',
                'title': '资金比昨日大总',
                'orderable': false,
            },
            {
                'data': 'bi_amount_60s_1_max_num',
                'title': '资金比昨日大数量',
                'orderable': false,
            },
            {
                'data': 'bi_amount_60s_1_max_avg',
                'title': '资金比昨日大平均',
                'orderable': false,
            },
            {
                'data': 'amount_reversed',
                'title': '反',
                'orderable': false,
                render: function (data, type, row) {
                    if (data > 0) {
                        return "<div class='container bg-warning'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'max_amount_reversed',
                'title': '反最大',
                'orderable': false,
            },
            {
                'data': 'amount_reversed_total',
                'title': '反总数',
                'orderable': false,
            },
            {
                'data': 'amount',
                'title': '金额',
                'orderable': false,
                render: function (data, type, row) {
                    var m = (data / 10000).toFixed(2)
                    if (m >= 90) {
                        if (row.buyorsell == 0) {
                            return "<span class='text-danger'>" + m + " 万元</span>";
                        } else {
                            return "<span class='text-success'>" + m + " 万元</span>";
                        }
                    }
                    return m + ' 万元';
                }
            },
            {
                'data': 'bi_amount_avg',
                'title': '金额变化',
                'orderable': false,
                render: function (data, type, row) {
                    if (data >= 10) {
                        return "<span class='text-danger'>" + data + "</span>";
                    }
                    return data;
                }
            },
            {
                'data': 'amounts',
                'title': '总金额',
                'orderable': false,
                render: function (data, type, row) {
                    return (data / 10000 / 10000).toFixed(2) + ' 亿元';
                }
            },
            {
                'data': 'bi_buy',
                'title': '买比',
                'orderable': false,
            },
            {
                'data': 'buyorsell',
                'title': '方向',
                'orderable': false,
                render: function (data, type, row) {
                    if (data == 0) {
                        return "<span class='text-danger'>买</span>";
                    } else if (data == 1) {
                        return "<span class='text-success'>卖</span>";
                    }
                    return data;
                }
            }
        ],
        /*
        createdRow: function (row, data, dataIndex){
            if(data.catch_zt == 1){
                $(row).find('td').addClass('border-bottom border-danger');
            }
        },*/
        buttons: [
            'copy', 'excel'
        ],
        destroy: true,
        lengthChange: false,
        paging: true,
        pageLength: 8,
        autoWidth: false,
        ordering: true,
        order: [2, 'desc'],
        searching: false,
        language: {
            "sProcessing": "处理中...",
            "sLengthMenu": "显示 _MENU_ 项结果",
            "sZeroRecords": "没有匹配结果",
            "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
            "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
            "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
            "sInfoPostFix": "",
            "sSearch": "搜索:",
            "sUrl": "",
            "sEmptyTable": "表中数据为空",
            "sLoadingRecords": "载入中...",
            "sInfoThousands": ",",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "上页",
                "sNext": "下页",
                "sLast": "末页"
            },
            "oAria": {
                "sSortAscending": ": 以升序排列此列",
                "sSortDescending": ": 以降序排列此列"
            }
        },
    });
};