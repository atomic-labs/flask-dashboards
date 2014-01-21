bar_chart = (div, data) ->
    nv.addGraph ->
        chart = nv.models.discreteBarChart()
            .x((d) -> d[0])
            .y((d) -> d[1])

        svg = $ "<svg style='height:300px; width:400px'>"
        $(div).append svg
        d3.select(div).select("svg").datum(data).transition().duration(500).call(chart)

        nv.utils.windowResize ->
            chart.update()
        chart

line_chart = (div, data) ->
    nv.addGraph ->
        chart = nv.models.lineChart()
            .x((d) -> d[0])
            .y((d) -> d[1])
        chart.xAxis.axisLabel("X Axis")
            .tickFormat d3.format(",r")
        chart.yAxis.axisLabel("Y Axis")
            .tickFormat d3.format(".02f")
        svg = $ "<svg style='height:300px; width:400px'>"
        $(div).append svg
        d3.select(div).select("svg").datum(data).transition().duration(500).call(chart)

        nv.utils.windowResize ->
            chart.update()
        chart

get_data = (div) ->
    data_name = div.getAttribute "dash-source"
    console.log "Fetching data for " + data_name

    request = $.get "../jobs/" + data_name + "/data", "",
        (data) ->
            switch div.getAttribute("dash-chart-type")
                when "bar" then bar_chart div, data
                when "line" then line_chart div, data

$(document).ready ->
    for div in $ "div[dash-source]"
        get_data div
