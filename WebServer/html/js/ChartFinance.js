
var financeSVGsize_margin = { top: 20, right: 30, bottom: 20, left: 30 },
    financeSVGsize_width = 390 - financeSVGsize_margin.left - financeSVGsize_margin.right,
    financeSVGsize_height = 280 - financeSVGsize_margin.top - financeSVGsize_margin.bottom;
var createSVG = function (id, title) {
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    var svg = d3
        .select(id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    svg
        .append("text")
        .attr("fill", "white")
        .attr('stroke', 'none')
        .attr("x", 0)
        .attr("y", 0)
        .attr("font-size", "16px")
        .text(title);
    return svg;
};
var createXTime = function (svg, data, datekey) {
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    const xMin = d3.min(data, d => {
        return d[datekey];
    });
    const xMax = d3.max(data, d => {
        return d[datekey];
    });
    var xScale = d3
        .scaleTime()
        .domain([xMin, xMax])
        .range([0, width]);
    svg
        .append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%y-%m-%d"))
        );
    return xScale;
};
var createXBand = function (svg, data, datekey) {
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    var xScale = d3
        .scaleBand()
        .rangeRound([width, 0], 0.05)
        .domain(data.map(function (d) { return d[datekey]; }))
        .padding(0.1);
    svg
        .append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%y-%m-%d"))
            .tickValues(xScale.domain().filter((d, i) => i % 2 === 0))
        );
    return xScale;
};
var drawBar = function (svg, xScale, data, datekey, value_name, show_lable) {
    //https://bl.ocks.org/vikkya/75bda04cd0c00e49cbda6cfee8d97aba
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    const yMin = d3.min(data, d => {
        return d[value_name];
    });
    const yMax = d3.max(data, d => {
        return d[value_name];
    });
    // 有负数
    if (yMin < 0)
        return drawBarFu(svg, xScale, data, datekey, value_name, show_lable);
    var yScale = d3
        .scaleLinear()
        .domain([yMin, yMax])
        .range([height, margin.top]);
    svg
        .append('g')
        .attr('transform', `translate(${width}, 0)`)
        .call(d3.axisRight(yScale));
    svg
        .selectAll()
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => {
            return xScale(d[datekey]);
        })
        .attr("y", d => {
            return yScale(d[value_name]);
        })
        .attr('fill', (d) => {
            return d[value_name] > 0 ? '#c0392b' : '#03a678';
        })
        .attr("width", xScale.bandwidth())
        .attr("height", d => {
            return height - yScale(d[value_name]);
        });
    if (show_lable)
        svg.append("g")
            .attr("text-anchor", "middle")
            .selectAll("text")
            .data(data)
            .join("text")
            .attr("fill", "white")
            .attr('stroke', 'none')
            .attr("x", d => xScale(d[datekey]) + (xScale.bandwidth() / 2))
            .attr("y", d => yScale(d[value_name]) - 5)
            .text(d => {
                return (d[value_name] / 10000 / 10000).toFixed(2);
            });
};
//有负数
var drawBarFu = function (svg, xScale, data, datekey, value_name, show_lable) {
    // http://jsfiddle.net/chrisJamesC/tNdJj/4/
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    const yMin = d3.min(data, d => {
        return d[value_name];
    });
    const yMax = d3.max(data, d => {
        return d[value_name];
    });
    var y0 = Math.max(Math.abs(yMin), Math.abs(yMax));
    var yScale = d3
        .scaleLinear()
        .domain([-y0, y0])
        .range([height, margin.top]);
    svg
        .append('g')
        .attr('transform', `translate(${width}, 0)`)
        .call(d3.axisRight(yScale));
    svg
        .selectAll()
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => {
            return xScale(d[datekey]);
        })
        .attr("y", d => {
            return yScale(Math.max(0, d[value_name]));
        })
        .attr('fill', (d) => {
            return d[value_name] > 0 ? '#c0392b' : '#03a678';
        })
        .attr("width", xScale.bandwidth())
        .attr("height", d => {
            return Math.abs(yScale(d[value_name]) - yScale(0));
        });
    svg.append("g")
        .attr("class", "y axis")
        .append("line")
        .attr("y1", yScale(0))
        .attr("y2", yScale(0))
        .attr("x1", 0)
        .attr("x2", width);
    if (show_lable)
        svg.append("g")
            .attr("text-anchor", "middle")
            .selectAll("text")
            .data(data)
            .join("text")
            .attr("fill", "white")
            .attr('stroke', 'none')
            .attr("x", d => xScale(d[datekey]) + (xScale.bandwidth() / 2))
            .attr("y", d => yScale(d[value_name]) - 5)
            .text(d => {
                return (d[value_name] / 10000 / 10000).toFixed(2);
            });
};
var drawLines = function (svg, xScale, data, datekey, value_names) {
    // https://observablehq.com/@yukokano/multi-line-chart-inline-labels
    // https://observablehq.com/@d3/inline-labels
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    var series = new Array();
    value_names.forEach(function (d_temp) {
        var a = data.map(item => ({ 'date': item[datekey], 'value': item[d_temp.key], 'name': d_temp.name, 'color': d_temp.color }));
        series.push(a);
    });
    series.forEach(function (d_temp) {
        var yScale = d3
            .scaleLinear()
            .domain([d3.min(d_temp, d => d.value), d3.max(d_temp, d => d.value)])
            .range([height - margin.bottom, margin.top]);
        svg
            .append('path')
            .data([d_temp])
            .attr('fill', 'none')
            .attr('stroke', d => d[0].color)
            .attr('stroke-width', 1.5)
            .attr('d', d3.line()
                .x(d => xScale(d.date))
                .y(d => yScale(d.value)));
        svg.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", 12)
            .attr("stroke-linecap", "round")
            .attr("stroke-linejoin", "round")
            .attr("text-anchor", "middle")
            .attr("font-weight", "bold")
            .selectAll("text")
            .data(d_temp)
            .join("text")
            .text(d => d.value)
            .attr("fill", d => d.color)
            .attr('stroke', 'none')
            .attr("dy", '0.35em')
            .attr("x", d => xScale(d.date))
            .attr("y", d => yScale(d.value))
            .clone(true).lower()
            .attr("fill", 'none')
            .attr("stroke", '#343a40')
            .attr("stroke-width", 3);
        svg.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", 14)
            .attr("stroke-linecap", "round")
            .attr("stroke-linejoin", "round")
            .attr("text-anchor", "end")
            .attr("font-weight", "bold")
            .selectAll("text")
            .data(d_temp.filter((d, i, d_temp) => i === 0))
            .join("text")
            .text(d => d.name)
            .attr("fill", d => d.color)
            .attr('stroke', 'none')
            .attr("x", d => xScale(d.date))
            .attr("y", d => yScale(d.value) - 10);
    });
};
var drawBaseinfo = function (data) {
    //https://observablehq.com/@d3/pie-chart
    //https://travishorn.com/self-contained-d3-pie-chart-function-e5b7422be676
    var margin = financeSVGsize_margin,
        width = financeSVGsize_width,
        height = financeSVGsize_height;
    var svg = d3
        .select('#baseinfo')
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("viewBox", [-width / 2, -height / 2, width, height]);
    const total = data.reduce((acc, cur) => acc + cur.value, 0);
    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.name))
        .range(d3.schemeCategory10);
    var radius = Math.min(width, height) / 2;
    const fourth = Math.min(width, height) / 4;
    var arc = d3.arc()
        .outerRadius(radius * 0.8)
        .innerRadius(radius * 0.6);
    var pie = d3.pie()
        .sort(null)
        .value(d => d.value);
    const arcs = pie(data);
    const labelOffset = fourth * 1.2;
    const arcLabel = d3.arc().innerRadius(labelOffset).outerRadius(labelOffset);
    svg.append("g")
        .selectAll("path")
        .data(arcs)
        .join("path")
        .attr("fill", d => color(d.data.name))
        .attr("d", arc)
        .append("title")
        .text(d => `${d.data.name}: ${d.data.value.toLocaleString()}`);
    svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 12)
        .attr("text-anchor", "end")
        .selectAll("text")
        .data(arcs)
        .join("text")
        .attr("transform", (d, i) => {
            var c = arcLabel.centroid(d),
                x = c[0],
                y = c[1];
            if ((d.endAngle - d.startAngle) < 0.25) {
                x = width / 2;
                y = -height / 2 + 30 + i * 30;
            }
            return `translate(${x}, ${y})`;
        })
        .call(text => text.append("tspan")
            .attr("y", "-0.4em")
            .attr('fill', 'white')
            .text(d => d.data.name))
        .call(text => text.append("tspan")
            .attr("x", 0)
            .attr("y", "0.7em")
            .attr("font-weight", "bold")
            .attr('stroke', 'none')
            .attr("fill", "white")
            .text(d => `${d.data.text}亿 (${Math.round(d.data.value / total * 100)}%)`));
};
var drawProfit = function (data) {
    var datekey = 'statDate';
    var svg = createSVG('#finance_profit', '主营收入（亿）');
    var xScale = createXBand(svg, data.profit, datekey);
    drawBar(svg, xScale, data.profit, datekey, 'MBRevenue', true);
    drawLines(svg, xScale, data.growth, datekey, [
        { 'key': 'YOYAsset', 'name': '总资产同比', 'color': d3.schemeCategory10[2] }
    ]);
    drawLines(svg, xScale, data.profit, datekey, [
        { 'key': 'roeAvg', 'name': '净资产收益率', 'color': d3.schemeCategory10[8] }
    ]);
};
var drawGrowth = function (data) {
    var datekey = 'statDate';
    var svg = createSVG('#finance_growth', '净利润（亿）');
    var xScale = createXBand(svg, data.profit, datekey);
    drawBar(svg, xScale, data.profit, datekey, 'netProfit', true);
    drawLines(svg, xScale, data.growth, datekey, [
        { 'key': 'YOYNI', 'name': '净利润同比', 'color': d3.schemeCategory10[2] }
    ]);
};
var drawBalance = function (data) {
    var datekey = 'statDate';
    var svg = createSVG('#finance_balance', '偿债能力');
    var xScale = createXTime(svg, data.balance, datekey);
    drawLines(svg, xScale, data.balance, datekey, [
        { 'key': 'quickRatio', 'name': '速动比率', 'color': d3.schemeCategory10[2] },
        { 'key': 'liabilityToAsset', 'name': '负债率', 'color': d3.schemeCategory10[3] }
    ]);
};
var drawOperation = function (data) {
    var datekey = 'statDate';
    var svg = createSVG('#finance_operation', '营运能力');
    var xScale = createXTime(svg, data.operation, datekey);
    drawLines(svg, xScale, data.operation, datekey, [
        { 'key': 'NRTurnRatio', 'name': '应收账款周转率', 'color': d3.schemeCategory10[2] },
        { 'key': 'INVTurnRatio', 'name': '存货周转率', 'color': d3.schemeCategory10[3] }
    ]);
};
var drawCashflow = function (data) {
    var datekey = 'statDate';
    var svg = createSVG('#finance_cash_flow', '现金流');
    var xScale = createXTime(svg, data.cash_flow, datekey);
    drawLines(svg, xScale, data.cash_flow, datekey, [
        { 'key': 'CAToAsset', 'name': '流动资产', 'color': d3.schemeCategory10[6] },
        { 'key': 'NCAToAsset', 'name': '非流动资产', 'color': d3.schemeCategory10[7] },
        { 'key': 'tangibleAssetToAsset', 'name': '有形资产', 'color': d3.schemeCategory10[8] }
    ]);
};