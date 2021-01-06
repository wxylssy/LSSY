var drawTick = function (id, data) {
    // 颜色方案 https://github.com/d3/d3-scale-chromatic
    min_time = d3.min(data, function (d) { return d.datetime; });
    var close_time1 = new Date(
        min_time.getFullYear(),
        min_time.getMonth(),
        min_time.getDate(),
        11,
        30,
        59
    );
    var open_time2 = new Date(
        min_time.getFullYear(),
        min_time.getMonth(),
        min_time.getDate(),
        13,
        0,
        0
    );
    var close_time2 = new Date(
        min_time.getFullYear(),
        min_time.getMonth(),
        min_time.getDate(),
        15,
        0,
        59
    );
    var d1 = new Array();
    var d2 = new Array();
    data.each(function (d_temp) {
        if (d_temp.datetime.getHours() < 12) {
            d1.push(d_temp);
        } else {
            d2.push(d_temp);
        }
    });
    var margin = { top: 20, right: 30, bottom: 20, left: 30 },
        width = 900 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;
    var svg = d3
        .select(id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    // 定义x轴
    var x0 = d3
        .scaleTime()
        .domain([min_time, close_time1])
        .range([0, width / 2]);
    var x1 = d3
        .scaleTime()
        .domain([open_time2, close_time2])
        .range([width / 2, width]);
    // 定义y轴
    var y0 = d3
        .scaleLinear()
        .domain([data[0].dt_price, data[0].zt_price])
        .range([height, 0]);
    var y1 = d3
        .scaleLinear()
        .domain([data[0].dt_chg, data[0].zt_chg])
        .range([height, 0]);
    var y2 = d3
        .scaleLinear()
        .domain([0, 30])
        .range([height, 0]);
    var y3 = d3
        .scaleLinear()
        .domain([0, 30])
        .range([height, 0]);
    // 通用线条的颜色
    var l_color_price = d3.schemeCategory10[3];
    var l_color_2 = d3.schemeCategory10[5];
    var l_color_3 = d3.schemeCategory10[0];
    var l_color_zero = d3.schemeCategory10[2];
    var l_color_five = d3.schemeCategory10[3];
    var z = d3.scaleSequential()
        .interpolator(d3.interpolateRdYlGn)
        .domain([data[0].zt_chg, data[0].dt_chg]);
    // 线
    var line_price_a = d3.line()
        .x(function (d) { return x0(d.datetime); })
        .y(function (d) { return y0(d.price); });
    var line_price_b = d3.line()
        .x(function (d) { return x1(d.datetime); })
        .y(function (d) { return y0(d.price); });
    var line3_a = d3.line()
        .x(function (d) { return x0(d.datetime); })
        .y(function (d) { return y2(d.bi_amount_60s); });
    var line3_b = d3.line()
        .x(function (d) { return x1(d.datetime); })
        .y(function (d) { return y2(d.bi_amount_60s); });
    var line4_a = d3.line()
        .x(function (d) { return x0(d.datetime); })
        .y(function (d) { return y3(d.bi_amount_60s_1); });
    var line4_b = d3.line()
        .x(function (d) { return x1(d.datetime); })
        .y(function (d) { return y3(d.bi_amount_60s_1); });
    // 画线
    svg.append("g")
        .append("line")
        .style('stroke', z(0))
        .style('stroke-width', 1)
        .style('opacity', 0.6)
        .attr('fill', 'none')
        .attr("y1", y1(0))
        .attr("y2", y1(0))
        .attr("x1", 0)
        .attr("x2", width);
    svg.append("g")
        .append("line")
        .style('stroke', z(5))
        .style('stroke-width', 1)
        .style('opacity', 0.6)
        .attr('fill', 'none')
        .attr("y1", y1(5))
        .attr("y2", y1(5))
        .attr("x1", 0)
        .attr("x2", width);
    svg.append("g")
        .append("line")
        .style('stroke', z(-5))
        .style('stroke-width', 1)
        .style('opacity', 0.6)
        .attr('fill', 'none')
        .attr("y1", y1(-5))
        .attr("y2", y1(-5))
        .attr("x1", 0)
        .attr("x2", width);
    // 持仓标记
    if (Object.keys(gp_row_data.chicang).length > 0) {
        svg.append("g")
            .append("line")
            .style('stroke', d3.schemeCategory10[3])
            .style('stroke-width', 1)
            .style('opacity', 0.6)
            .attr('fill', 'none')
            .attr("y1", y0(gp_row_data.chicang.price))
            .attr("y2", y0(gp_row_data.chicang.price))
            .attr("x1", 0)
            .attr("x2", width);
        if (gp_row_data.chicang.sell_price > 0)
            svg.append("g")
                .append("line")
                .style('stroke', d3.schemeCategory10[2])
                .style('stroke-width', 1)
                .style('opacity', 0.6)
                .attr('fill', 'none')
                .attr("y1", y0(gp_row_data.chicang.sell_price))
                .attr("y2", y0(gp_row_data.chicang.sell_price))
                .attr("x1", 0)
                .attr("x2", width);
    }

    svg.append("path")
        .data([d1])
        .attr("class", "line")
        .style('stroke', l_color_2)
        .style('stroke-width', 2)
        .style('opacity', 0.5)
        .attr('fill', 'none')
        .attr("d", line3_a);
    svg.append("path")
        .data([d2])
        .attr("class", "line")
        .style('stroke', l_color_2)
        .style('stroke-width', 2)
        .style('opacity', 0.5)
        .attr('fill', 'none')
        .attr("d", line3_b);
    svg.append("path")
        .data([d1])
        .attr("class", "line")
        .style('stroke', l_color_3)
        .style('stroke-width', 2)
        .style('opacity', 0.5)
        .attr('fill', 'none')
        .attr("d", line4_a);
    svg.append("path")
        .data([d2])
        .attr("class", "line")
        .style('stroke', l_color_3)
        .style('stroke-width', 2)
        .style('opacity', 0.5)
        .attr('fill', 'none')
        .attr("d", line4_b);
    svg.append("path")
        .data([d1])
        .attr("class", "line")
        .style("stroke", l_color_price)
        .style('stroke-width', 2)
        .attr('fill', 'none')
        .attr("d", line_price_a);
    svg.append("path")
        .data([d2])
        .attr("class", "line")
        .style('stroke', l_color_price)
        .style('stroke-width', 2)
        .attr('fill', 'none')
        .attr("d", line_price_b);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x0)
            .tickFormat(d3.timeFormat("%H:%M"))
        );
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x1)
            .tickFormat(d3.timeFormat("%H:%M"))
        );
    svg.append("g")
        .attr("class", "axisSteelBlue")
        .call(d3.axisLeft(y0));
    //svg.append("g")
    //    .attr("class", "axisSteelBlue")
    //    .call(d3.axisLeft(y2));
    //svg.append("g")
    //   .attr("class", "axisSteelBlue")
    //    .call(d3.axisLeft(y3));
    svg.append("g")
        .attr("class", "axisRed")
        .attr("transform", "translate( " + width + ", 0 )")
        .call(d3.axisRight(y1)
            .ticks(data[0].zt_chg - data[0].dt_chg)
        );
}
