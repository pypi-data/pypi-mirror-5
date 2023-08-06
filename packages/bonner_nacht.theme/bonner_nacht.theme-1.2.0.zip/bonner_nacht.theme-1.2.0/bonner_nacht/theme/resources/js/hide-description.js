function insertHideButton() {
    $(".event-metainfo").append('<a class="toggle-description" href="#">Beschreibung anzeigen</a>')

    $("#" + button_id).bind('click', installWebapp);
};

function init() {

	insertHideButton();

	$("a.toggle-description").click(function(e){
		e.preventDefault();
			
		$(this).parent().parent().parent().children(".event-description").slideToggle("slow");
	});

	$(".hideable-description").hide();
};

// Initialize when DOM is loaded
$(document).ready(init);