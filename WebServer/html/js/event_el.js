
// 弹出层关闭事件
$('#modal_tick').on('hide.bs.modal', function (event) {
    wsTick.close();
    stopChengjiaoUpdate();
});

// 买卖确认弹出事件
$('#buyModal').on('show.bs.modal', function (event) {
    stopChengjiaoUpdate();
    $('#buyText').text(`${gp_row_data.code} ${gp_row_data.name}（${gp_row_data.hangye}）`);
});
$('#sellModal').on('show.bs.modal', function (event) {
    stopChengjiaoUpdate();
    $('#sellText').text('立即全部卖出 ' + gp_row_data.code + ' ？');
});

// 全撤确认弹出事件
$('#cancelModal').on('show.bs.modal', function (event) {
    stopChengjiaoUpdate();
    $('#cancelModalText').text('是否撤销全部委托？');
});

// 提示信息的显示和隐藏
$('#info_toast').on('show.bs.toast', function () {
    $('#info_toast').parent().attr('style', 'z-index: 1070 !important; position: absolute !important;');
});
$('#info_toast').on('hidden.bs.toast', function () {
    $('#info_toast').parent().attr('style', 'display: none !important;');
});
