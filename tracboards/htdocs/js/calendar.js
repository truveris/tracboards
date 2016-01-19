function refreshData() {
    $.getJSON("/dashboard/calendar.json", function(data) {
        var previousDate = "unknown";

        $("#events").empty();
        $("#today").html((new Date()).toDateString());

        for (var i = 0; i < data.event_dates.length; i++) {
            var e = data.event_dates[i];
            var rowClasses = [];

            if (e["class"])
                rowClasses.push(e["class"]);

            if (previousDate == "Today" && e["date"] != previousDate)
                rowClasses.push("outline");

            $("#events").append(
                $("<tr/>", {"class": rowClasses.join(" ")}).append(
                    $("<td/>", {"class": "date", "html": e["date"]}),
                    $("<td/>", {"class": "milestone", "html": e["milestone"]}),
                    $("<td/>", {"class": "icon"}).append(
                        $("<i/>", {"class": "fa fa-"+e["icon"]})
                            .css("color", e["color"])
                    ),
                    $("<td/>", {"class": "name", "html": e["name"]})
                )
            );

            previousDate = e["date"];
        }
    });
}

$(document).ready(function() {
    refreshData();
    setInterval(refreshData, 6000);
});
