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
    chart.yAxis.tickFormat d3.format(",")

create_chart = (div, data) ->
    nv.addGraph ->
        switch div.getAttribute "dash-chart-type"
            when "bar" then chart = nv.models.discreteBarChart()
            when "line" then chart = nv.models.lineChart()
            when "stacked-area" then chart = nv.models.stackedAreaChart().showControls(false)
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

create_table = (div, data) ->
    console.log "Creating table"
    table = $ "<table class='dash-table'>"

    row = $ "<tr>"
    for s in data
        cell = $ "<th>" + s.key + "</th>"
        row.append cell
    table.append row

    rows = (Math.max.apply null, (s.values.length for s in data)) - 1
    for i in [0..rows]
        row = $ "<tr>"
        for s in data
            if s.values.length > i
                cell = $ "<td>" + s.values[i] + "</td>"
                row.append cell
        table.append row

    $(div).append table

get_data = (div) ->
    data_name = div.getAttribute "dash-source"
    console.log "Fetching data for " + data_name

    request = $.get "../jobs/" + data_name + "/data", "",
        (data) ->
            if div.getAttribute("dash-chart-type") in ["bar", "line", "stacked-area"]
                create_chart div, data
            else
                create_table div, data

$(document).ready ->
    for div in $ "div[dash-source]"
        get_data div
