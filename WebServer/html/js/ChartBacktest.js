
var drawBacktest = function (id, data) {
    // 颜色方案 https://github.com/d3/d3-scale-chromatic
    var datekey = 'datetime';
    var value_name = 'tol_yl';
    var margin = { top: 20, right: 30, bottom: 20, left: 30 },
        width = 2500 - margin.left - margin.right,
        height = 920 - margin.top - margin.bottom;
    var svg = d3
        .select(id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    const yMin = d3.min(data, function (d) {
        return d[value_name];
    });
    const yMax = d3.max(data, function (d) {
        return d[value_name];
    });
    var xScale = d3
        .scaleBand()
        .rangeRound([0, width], 0.05)
        .domain(data.map(function (d) { return d[datekey]; }))
        .padding(0.1);
    svg
        .append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%y-%m-%d"))
            .tickValues(xScale.domain().filter((d, i) => i % 2 === 0))
        );
    var yScale = d3
        .scaleLinear()
        .domain([yMin, yMax])
        .range([height - margin.bottom, margin.top]);
svg.append("g")
        .attr("class", "axisRed")
        .attr("transform", "translate( " + width + ", 0 )")
        .call(d3.axisRight(yScale));
    svg
            .append('path')
            .data([data])
            .attr('fill', 'none')
            .attr('stroke', d3.schemeCategory10[3])
            .attr('stroke-width', 3)
            .attr('d', d3.line()
                .x(d => xScale(d[datekey]))
                .y(d => yScale(d[value_name])));
};

$(document).ready(function () {
    wsTick = new WebSocket(wsCmdURL);

    wsTick.onopen = function () {
        var cmdData = {
            'cmd': 3
        };
        wsTick.send(JSON.stringify(cmdData));
    };

    wsTick.onmessage = function (e) {
        $('#zc_charts').html(e.data);
    };

    wsTick.onclose = function (e) {

    };

    wsTick.onerror = function (e) {

    };
});
