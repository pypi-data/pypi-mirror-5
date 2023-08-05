/*global window, document, $, githubsurvivor */

(function () {
    'use strict';

    // Parse an ISO-8601-formatted date string
    function parseDate(s) {
        return new Date(Date.parse(s));
    }

    // Transform an HTML <table> into a two-dimensional array of strings
    function slurp(table) {
        return $.makeArray($(table).find('tbody tr')).map(function (tr) {
            return $.makeArray($(tr).find('td')).map(function (td) {
                return $(td).text();
            });
        });
    }

    // Extract data from each row in the <tbody> of `dataTable`. Each function
    // in `mappers` transforms values in a single column
    function extractData(dataTable, mappers) {
        return slurp(dataTable).map(function (row) {
            return mappers.map(function (mapper, idx) {
                return mapper(row[idx]);
            });
        });
    }

    function initBugRateChart(args) {
        var $dataTable = $('#bug-rate-data');

        var data = extractData($dataTable, [parseDate, parseInt, parseInt]);
        var rawValues = data.map(function (group) {
            // drop date; we don't display it
            return group.slice(1);
        });

        // Normalise values into the range [0, 1]
        var max = Math.max.apply(null, rawValues.map(function (group) {
            return Math.max.apply(null, group);
        }));
        var relativeValues = rawValues.map(function (group) {
            return group.map(function (val) {
                return val / max;
            });
        });

        var chart = new githubsurvivor.charts.ColumnChart($dataTable.attr('summary'));
        $dataTable.replaceWith(chart.element);
        chart.draw(relativeValues);
    }

    function initBugCountChart() {
        var $dataTable = $('#open-bug-data');

        var data = extractData($dataTable, [parseDate, parseInt]);
        var rawValues = data.map(function (row) {
            // drop date; we don't display it
            return row[1];
        });

        // Normalise values into the range [0, 1]
        var max = Math.max.apply(null, rawValues);
        var relativeValues = rawValues.map(function (val) {
            return val / max;
        });

        var chart = new githubsurvivor.charts.LineChart($dataTable.attr('summary'));
        $dataTable.replaceWith(chart.element);
        chart.draw(relativeValues);
    }

    $(function () {
        initBugRateChart();
        initBugCountChart();
        // Refresh every 10 minutes to get latest data
        window.setTimeout(function () { window.location.reload(); }, 1000 * 60 * 10);
    });
}());
