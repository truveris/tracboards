function refreshData() {
    $.getJSON("/dashboard/calendar.json", function(data) {
        var previousGroup = "unknown";

        $("#events").empty();
        $("#today").html((new Date()).toDateString());

        for (var i = 0; i < data.events.length; i++) {
            var e = data.events[i];
            var rowClasses = [];

            if (e["class"])
                rowClasses.push(e["class"]);

            if (e["group"] != previousGroup && e["group"] !== null) {
                $("#events").append(
                    $("<tr/>", {"class": "header outline"}).append(
                        $("<td/>", {"class": "group", "html": e["group"]}),
                        $("<td/>"),
                        $("<td/>"),
                        $("<td/>")
                    )
                );
            }


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

            previousGroup = e["group"];
        }
    });
}

$(document).ready(function() {
    refreshData();
    setInterval(refreshData, 6000);
});
