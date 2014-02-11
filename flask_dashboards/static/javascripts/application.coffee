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

    series = data[0]
    row = $ "<tr>"
    row.append( $ "<th>" + series.key + "</th>")
    for val in series.values
        cell = $ "<th>" + val + "</th>"
        row.append cell
    table.append row

    for series in data[1..]
        row = $ "<tr>"
        row.append( $ "<td>" + series.key + "</td>")
        for val in series.values
            cell = $ "<td>" + val + "</td>"
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
