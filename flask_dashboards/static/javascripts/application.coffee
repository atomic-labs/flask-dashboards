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

    series_map = {}
    series_dates = []
    num_cols = 0
    for series in data
        series_map[series["key"]] = series["values"]
        if series["values"].length > num_cols
            num_cols = series["values"].length
        series_dates.push series["key"]

    row = $ "<tr>"
    row.append($ "<th></th>")
    row.append($ "<th>Sign Ups</th>")
    for i in [1..(num_cols - 1)]
        row.append($ "<th>" + i + "</th>")
    table.append row

    for name in series_dates.sort()
        row = $ "<tr>"
        start = series_map[name][0]
        row.append( $ "<td>" + name + "</td>")
        row.append( $ "<td>" + start + "</td>")
        for val in series_map[name][1..]
            count = (val / start * 100).toFixed(2)
            if count > 55
                cls = "dash-very-high"
            else if count > 40
                cls = "dash-high"
            else if count > 30
                cls = "dash-med"
            else if count > 20
                cls = "dash-low"
            else if count > 10
                cls = "dash-very-low"
            else
                cls = ""
            cell = $ "<td class='" + cls + "'>" + count + "%</td>"
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
