function sortedList(obj) {
    var items = [];

    var sortable = [];
    for (var key in obj) {
        sortable.push([key, obj[key]])
    }
    sortable.sort(function(a, b) {return b[1] - a[1]})

    $.each(sortable, function(key, val) {
        items.push($("<li/>").append(
            $("<span/>").html(val[0]),
            $("<span/>").html(val[1])
        ))
    });

    return items;
}

function total(c) {
    var total = 0;
    $.each(c, function(key, val) {
        total += val;
    });
    return total;
}

function refreshData() {
    $.getJSON("/dashboard/defects.json", function(data) {
        var newOpenedByComponent = data["new_opened_by_component"];
        var triagedOpenedByComponent = data["triaged_opened_by_component"];
        var closedByOwner = data["closed_by_owner"];

        var totalTriagedDefects = total(triagedOpenedByComponent);
        var totalNewDefects = total(newOpenedByComponent);
        if (totalNewDefects > 50) {
            totalClass = "critical";
        } else if (totalNewDefects > 25) {
            totalClass = "warning";
        } else {
            totalClass = "ok";
        }

        $("#left .total-new")
            .empty()
            .append($("<div/>",{
                "class": totalClass,
                "html": totalNewDefects + "<p>new</p>"
            }));
        $("#left .total-triaged")
            .empty()
            .append($("<div/>",{
                "html": totalTriagedDefects + "<p>triaged</p>"
            }));

        $("#left .content .leaders")
            .empty()
            .append(sortedList(newOpenedByComponent));

        var totalClosed = total(closedByOwner);
        $("#right .total")
            .empty()
            .append($("<div/>",{
                "html": totalClosed + "<p>bugfixes</p>"
            }));

        $("#right .content .leaders")
            .empty()
            .append(sortedList(closedByOwner));
    });
}

$(document).ready(function() {
    refreshData();
    setInterval(refreshData, 5000);
});
