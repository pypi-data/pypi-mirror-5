// define the manifest url
var manifest_url = window.location.protocol + "//" + window.location.hostname + "/manifest.webapp";
var insert_element_id = "extras-section"
var button_id = "install-webapp"

function installWebapp(ev) {
    ev.preventDefault();

    // install the app
    var myapp = navigator.mozApps.install(manifest_url);
    myapp.onsuccess = function(data) {
      // App is installed, remove button
      removeButton();
    };
    myapp.onerror = function() {
      // App wasn't installed, info is in
      // installapp.error.name
     };
};

function insertButton() {
    $("#" + insert_element_id).append("<button id=\"" + button_id + "\">Als Webapp installieren</button>")

    $("#" + button_id).bind('click', installWebapp);
};

function removeButton() {
    $("#" + button_id).remove();
};

function init() {
    // check if client supports open web apps, othervise stop
    if(!navigator.mozApps) {
        return
    }

	try {
    	var request = navigator.mozApps.checkInstalled(manifest_url);
   	} catch(e) {
   		return
   	}
    
    request.onsuccess = function() {
        if (request.result) {
            // we're installed, do nothing
        } else {
            // not installed
            insertButton();
        }
    };
    request.onerror = function() {
        alert('Error checking installation status: ' + this.error.message);
    };
};

// Initialize when DOM is loaded
$(document).ready(init);
