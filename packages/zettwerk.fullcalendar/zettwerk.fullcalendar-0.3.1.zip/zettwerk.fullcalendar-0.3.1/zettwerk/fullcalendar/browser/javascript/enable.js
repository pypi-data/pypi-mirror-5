var defaultCalendarOptions = null;
$(document).ready(function() {
    if (defaultCalendarOptions !== null) {
	if (defaultCalendarOptions.preview) {
	    defaultCalendarOptions['eventRender'] = function(event, element) {
		addPreviewText(event, element);
	    };
	}
	$('#jquery-fullcalendar').fullCalendar(defaultCalendarOptions);
    }
});

var addPreviewText = function(event, element) {
    var preview = '<a class="fc-event-title" href="'+element.attr('href')+'"><span>' + defaultCalendarOptions.preview + '</span></a>';
    if (element.find('div.fc-event-head').length) {
	// week and day view
	$(preview).appendTo(element.find('div.fc-event-head'));
    } else {
	// month view
	$(preview).appendTo(element.find('div'));
    }
    element.find('a').prepOverlay({
        subtype: 'ajax',
        filter: '#content > *'
    });
};
