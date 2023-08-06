function init() {

    var requirements_url = window.location.protocol + "//" + window.location.hostname + "/requirements";

    /* 
     * Modernizr Flexbox support not working yet, see https://github.com/Modernizr/Modernizr/issues/812
     *
     Modernizr.addTest('flexbox', testAllProps('flexBasis'));
     Modernizr.addTest('flexboxlegacy', testAllProps('boxDirection'));
     Modernizr.addTest('flexboxtweener', testAllProps('flexAlign'));

     alert(Modernizr.flexbox);
     alert(Modernizr.flexboxlegacy);
     alert(Modernizr.flexboxtweener);

     if (!(Modernizr.flexbox || Modernizr.flexboxlegacy || Modernizr.flexboxtweener)) {
     noty({
     text: 'Dein Browser unterstützt leider das sogenannte "Flexbox" nicht und Bonner Nacht wird dadurch <strong>nicht richtig angezeigt.</strong><br />'
     + '<a href="' + requirements_url + '">Mehr Informationen dazu</a>',
     type: 'warning'});
     } */


    if ($.browser.mozilla && $.browser.version < 17.0) {
        unsupported = true;
        browser_name = 'Mozilla Firefox';
    } else if ($.browser.msie && $.browser.version < 10.0) {
        unsupported = true;
        browser_name = 'Internet Explorer';
    } else if ($.browser.opera && $.browser.version < 12.1) {
        unsupported = true;
        browser_name = 'Opera';
    } else {
	unsupported = false;
    }

    if(unsupported) {
        noty({
            text: 'Sie scheinen ' + browser_name +  ' in einer alten Version auszuführen, die die sogenannte "Flexbox"-Funktion nicht unterstützt.<br />Daher wird Bonner Nacht vermutlich <strong>nicht richtig angezeigt.</strong><br />'
            + '<a href="' + requirements_url + '">Mehr Informationen dazu</a>',
            type: 'warning'});
    }
};

// Initialize when DOM is loaded
$(document).ready(init);
