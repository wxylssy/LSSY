const createMainTable = function (id) {
    $(id).DataTable({
        columns: [
            {
                "data": "bz",
                "title": "操作",
                render: function (data, type, row) {
                    if(data > 0){
                        return "<a href=\"javascript:void(0);\" class=\"badge badge-danger\" onclick=\"setbz('" + row.code + "', 0);\">重点</a>";
                    }
                    return "<a href=\"javascript:void(0);\" class=\"badge badge-dark\" onclick=\"setbz('" + row.code + "', 1);\">重点</a>";
                }
            },
            {
                "data": 'catch_zt',
                'title': '标记',
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
                "class": "text-center",
            },
            {
                "data": "name",
                "title": "名称",
            },
            {
                'data': 'hangye',
                'title': '行业',
                render: function (data, type, row){
                    return "<span class=\"text-secondary\">" + data + "</span>";
                }
            },
            {
                'data': 'datetime',
                'title': '时间'
            },
            {
                "data": 'price',
                'title': '价格',
            },
            {
                "data": 'zdf',
                'title': '涨跌幅',
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
                'data': 'zdf_open',
                'title': '开盘涨跌幅',
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
            },
            {
                'data': 'bi_amount_open_last',
                'title': '开盘量比昨日开盘',
            },
            {
                "data": 'bi_amount',
                'title': '量比',
            },
            {
                'data': 'speed_60s',
                'title': '速度',
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
                render: $.fn.dataTable.render.number(',', '.')
            },
            {
                'data': 'nums',
                'title': '总订单',
                render: $.fn.dataTable.render.number(',', '.')
            },
            {
                'data': 'max_speed_60s',
                'title': '最大涨速',
                render: function (data, type, row) {
                    if (data >= speed_60s) {
                        return "<div class='container bg-warning'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'bi_amount_60s_1_max_num',
                'title': '资金比昨日大数量'
            },
            {
                'data': 'bi_amount_60s_1_max_avg',
                'title': '资金比昨日大平均'
            },
            {
                'data': 'amount_reversed',
                'title': '反',
                render: function (data, type, row) {
                    if (data > 0) {
                        return "<div class='container bg-warning'>" + data + "</div>";
                    }
                    return data;
                }
            },
            {
                'data': 'max_amount_reversed',
                'title': '反最大'
            },
            {
                'data': 'amount_reversed_total',
                'title': '反总数'
            },
            {
                'data': 'amount',
                'title': '金额',
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
                render: function (data, type, row) {
                    return (data / 10000 / 10000).toFixed(2) + ' 亿元';
                }
            },
            {
                'data': 'bi_buy',
                'title': '买比'
            },
            {
                'data': 'buyorsell',
                'title': '方向',
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
        pageLength: 28,
        autoWidth: false,
        ordering: false,
        searching: true,
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