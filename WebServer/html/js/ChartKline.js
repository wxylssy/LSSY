var drawKline = function (id, data) {
    // https://www.freecodecamp.org/news/how-to-build-historical-price-charts-with-d3-js-72214aaf6ba3/
    // https://observablehq.com/@d3/candlestick-chart
    var margin = { top: 20, right: 30, bottom: 20, left: 30 },
        width = 1400 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;
    var svg = d3
        .select(id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    data.forEach(function (d_temp) {
        d_temp.datetime = dateParse(d_temp.datetime);
    });
    var xScale = d3.scaleBand()
        .domain(data.map(function (d) { return d.datetime; }))
        .range([width, 0])
        .padding(0.2);
    var yScale = d3.scaleLinear()
        .domain([d3.min(data, d => d.low), d3.max(data, d => d.high)])
        .range([height - 5, 0]);
    svg
        .append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%y-%m-%d"))
            .tickValues(xScale.domain().filter((d, i) => i % 30 === 0))
        );
    svg
        .append('g')
        .attr('transform', `translate(${width}, 0)`)
        .call(d3.axisRight(yScale));
    // 标记K线
    const tradeDate = dateParse(dateFormat(datetimeParse(gp_row_data.datetime)));
    //d3.selectAll('.focus line').remove();
    if (tradeDate <= data[0].datetime) {
        svg.append("g")
            .attr('class', 'focus')
            .append("line")
            .style('stroke', '#67809f')
            .style('stroke-width', 0.6)
            .style('stroke-dasharray', 3.3)
            .attr('fill', 'none')
            .attr("y1", 0)
            .attr("y2", height)
            .attr("x1", xScale(tradeDate))
            .attr("x2", xScale(tradeDate));
    }
    if (Object.keys(gp_row_data.chicang).length > 0) {
        const buyDate = dateParse(dateFormat(datetimeParse(gp_row_data.chicang.datetime)));
        svg.append("g")
            .attr('class', 'focus')
            .append("line")
            .style('stroke', '#c0392b')
            .style('stroke-width', 0.6)
            .style('stroke-dasharray', 3.3)
            .attr('fill', 'none')
            .attr("y1", 0)
            .attr("y2", height)
            .attr("x1", xScale(buyDate))
            .attr("x2", xScale(buyDate));
        svg.append("g")
            .attr('class', 'focus')
            .append("line")
            .style('stroke', '#c0392b')
            .style('stroke-width', 1)
            .style('stroke-dasharray', 3.3)
            .attr('fill', 'none')
            .attr("y1", yScale(gp_row_data.chicang.price))
            .attr("y2", yScale(gp_row_data.chicang.price))
            .attr("x1", 0)
            .attr("x2", width);
    }
    svg.append("g")
        .append("line")
        .style('stroke', '#67809f')
        .style('stroke-width', 1)
        .style('stroke-dasharray', 3.3)
        .attr('fill', 'none')
        .attr("y1", yScale(data[0].close))
        .attr("y2", yScale(data[0].close))
        .attr("x1", 0)
        .attr("x2", width);
    svg.append("g")
        .append("line")
        .style('stroke', '#67809f')
        .style('stroke-width', 1)
        .style('stroke-dasharray', 3.3)
        .attr('fill', 'none')
        .attr("y1", yScale(data[0].zt_price))
        .attr("y2", yScale(data[0].zt_price))
        .attr("x1", 0)
        .attr("x2", width);
    ////////////////////
    /* Amount series bars */
    const yMinAmount = d3.min(data, d => {
        return d['amount'];
    });
    const yMaxAmount = d3.max(data, d => {
        return d['amount'];
    });
    const yAmountScale = d3
        .scaleLinear()
        .domain([yMinAmount, yMaxAmount])
        .range([height, 0]);
    const g = svg.append("g")
        .attr("stroke-linecap", "round")
        .selectAll("g")
        .data(data)
        .join("g")
        .attr("transform", d => `translate(${xScale(d.datetime)},0)`);
    g.append('line')
        .style('opacity', 0.2)
        .attr('y1', d => yAmountScale(d['amount']))
        .attr('y2', height)
        .attr('stroke-width', xScale.bandwidth())
        .attr('stroke', d => d.open > d.close ? '#03a678'
            : d.close > d.open ? '#c0392b'
                : d3.schemeSet1[8]);
    g.append("line")
        .attr("y1", d => yScale(d.low))
        .attr("y2", d => yScale(d.high))
        .attr("stroke-width", xScale.bandwidth() * 0.3)
        .attr("stroke", d => d.open > d.close ? '#03a678'
            : d.close > d.open ? '#c0392b'
                : d3.schemeSet1[8]);
    g.append("line")
        .attr("y1", d => yScale(d.open))
        .attr("y2", d => yScale(d.close))
        .attr("stroke-width", xScale.bandwidth())
        .attr("stroke", d => d.open > d.close ? '#03a678'
            : d.close > d.open ? '#c0392b'
                : d3.schemeSet1[8]);
    g.append("title")
        .text(d => `${dateFormat(d.datetime)}
                    Open: ${d.open}
                    Close: ${d.close} (${d.pctChg})
                    Low: ${d.low}
                    High: ${d.high}
                    ma5: ${d.ma_5}
                    cr: ${d.cr}
                    vc(越大越好): ${d.vc}
                    vc2(越小越好): ${d.vc2}
                    vcc(对比N日前): ${d.vcc}
                    `
        );
    //均线
    var avgColor = d3.scaleOrdinal(d3.schemeSet3);
    svg
        .append('path')
        .data([data])
        .style('fill', 'none')
        .attr('stroke', avgColor(0))
        .attr('d', d3
            .line()
            .x(d => {
                return xScale(d['datetime']);
            })
            .y(d => {
                return yScale(d['ma_5']);
            }));
    svg
        .append('path')
        .data([data])
        .style('fill', 'none')
        .attr('stroke', avgColor(1))
        .attr('d', d3
            .line()
            .x(d => {
                return xScale(d['datetime']);
            })
            .y(d => {
                return yScale(d['ma_10']);
            }));
    svg
        .append('path')
        .data([data])
        .style('fill', 'none')
        .attr('stroke', avgColor(2))
        .attr('d', d3
            .line()
            .x(d => {
                return xScale(d['datetime']);
            })
            .y(d => {
                return yScale(d['ma_20']);
            }));
    svg
        .append('path')
        .data([data])
        .style('fill', 'none')
        .attr('stroke', avgColor(3))
        .attr('d', d3
            .line()
            .x(d => {
                return xScale(d['datetime']);
            })
            .y(d => {
                return yScale(d['ma_60']);
            }));
    svg
        .append('path')
        .data([data])
        .style('fill', 'none')
        .attr('stroke', avgColor(4))
        .attr('d', d3
            .line()
            .x(d => {
                return xScale(d['datetime']);
            })
            .y(d => {
                return yScale(d['ma_120']);
            }));
    svg
        .append('path')
        .data([data])
        .style('fill', 'none')
        .attr('stroke', avgColor(5))
        .attr('d', d3
            .line()
            .x(d => {
                return xScale(d['datetime']);
            })
            .y(d => {
                return yScale(d['ma_240']);
            }));
    g.on('click', function (e) {
        getTicksDay(gp_row_data.code, dateFormat(e.datetime));
    });
}