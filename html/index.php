<html>
    <head>
        <title>Nest History</title>

        <script src="https://code.highcharts.com/highcharts.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
        <script type="text/javascript">

        var offset=0;

        setInterval(drawChartTimer,60 * 1000);

        function createChart(offset)
        {
            switch (offset)
            {
                case 0:
                    $("#offset").text("Today");
                    break;

                case 1:
                    $("#offset").text("Yesterday");
                    break;

                default:
                    $("#offset").text(offset + " days ago");
                    break;
            }

            var dataURL = "getresults.php?offset="+offset;

            $.getJSON(dataURL, function(readData) {
                var globalOptions =
                {
                    global :
                    {
                        useUTC : false
                    }
                };

                Highcharts.setOptions(globalOptions);

                var chartOptions =
                {
                    chart:
                    {
                        type: 'line',
                        renderTo: 'graph'
                    },

                    title:
                    {
                        text: 'Nest History'
                    },

                    xAxis:
                    {
                        type: 'datetime'
                    },

                    yAxis:
                    [
                        {
                            title:
                            {
                                text: 'Temperature'
                            },

                            labels:
                            {
                                formatter: function() { return this.value; }
                            },
/*
                            max: 25,
                            min: -5,
                            tickInterval: 5,
*/
                        },
                        {
                            title:
                            {
                                text: 'State'
                            },

                            categories: [ 'Eco', 'Cool', 'Off', 'Heat', 'Heat-Cool'],

                            labels:
                            {
                                formatter: function() { return this.value; }
                            },

                            opposite: true

                        },
                        {
                            title:
                            {
                                text: 'Home / Away'
                            },

                            categories: [ 'Away', 'Home' ],

                            labels:
                            {
                                formatter: function() { return this.value; }
                            },

                            opposite: true

                        },
                        {
                            title:
                            {
                                text: 'Loft'
                            },

                            labels:
                            {
                                formatter: function() { return this.value; }
                            },

                        },
/*
                        {
                            title:
                            {
                                text: 'Humidity'
                            },

                            labels:
                            {
                                formatter: function() { return this.value; }
                            },
                            max: 60,
                            min: 30,
                            tickInterval: 5,

                        },
*/
                    ],
                };

                if (readData.length!=0)
                {
                    var series=[
                        {
                            name: "Actual",
                            yAxis: 0,
                            data: readData[0]["ambienttemp"]["data"]
                        },
                        {
                            name: "Target",
                            yAxis: 0,
                            data: readData[0]["targettemp"]["data"]
                        },
                        {
                            name: "State",
                            yAxis: 1,
                            data: readData[0]["hvacstate"]["data"]
                        },
                        {
                            name: "Home / Away",
                            yAxis: 2,
                            data: readData[0]["homeaway"]["data"]
                        },
                        {
                            name: "Loft",
                            yAxis: 0,
                            data: readData[0]["loft"]["data"]
                        },
/*
                        {
                            name: "Humidity",
                            yAxis: 2,
                            data: readData[0]["humidity"]["data"]
                        },
*/
                    ];

                    chartOptions.series=series;
                }

                chart = new Highcharts.Chart(chartOptions);
            });
        }

        function drawChartTimer()
        {
            if (offset==0)
            {
                drawChart();
            }
        }

        function drawChart()
        {
            $('#next').prop('disabled', offset==0);
            $('#prev').prop('disabled', offset>=10);
            createChart(offset);
        }

        function prevDay()
        {
            offset=offset+1;
            drawChart();
        }

        function nextDay()
        {
            offset=offset-1;
            drawChart();
        }

        </script>
    </head>
    <body onload="drawChart();">
    <div id="graph"></div>
    <div align="center">
        <button id='prev' type='button' onclick='prevDay()'>&lt;&lt;</button> <span id='offset'>0</span> <button id='next' type='button' onclick='nextDay()'>&gt;&gt;</button></div>
    </body>
</html>
