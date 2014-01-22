set_conversion_funcs = (chart, data) ->
    if not data.x_axis_conversion?
        data["x_axis_conversion"] = "default"

    switch data["x_axis_conversion"]
        when "date"
            chart.x (d) -> new Date(d[0]).getTime()
            chart.xAxis.tickFormat (d) -> d3.time.format('%b %d')(new Date(d))
        else
            chart.x (d) -> d[0]

    chart.y (d) -> d[1]

create_chart = (div, data) ->
    nv.addGraph ->
        switch div.getAttribute "dash-chart-type"
            when "bar" then chart = nv.models.discreteBarChart()
            when "line" then chart = nv.models.lineChart()
            else
                console.log "Unknown chart type: " +
                    div.getAttribute "dash-chart-type"
                return

        # TODO(ben): Assumes all series has same axis type as first series
        set_conversion_funcs chart, data[0]

        svg = $ "<svg sytle='width: 100%; height: 100%;'></svg>"
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
            create_chart div, data

$(document).ready ->
    for div in $ "div[dash-source]"
        get_data div
