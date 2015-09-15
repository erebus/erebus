jQuery(document).ready(function() {
    jQuery("#log-console").slimScroll({
        allowPageScroll: true, // allow page scroll when the element scroll is ended
        size: '7px',
        color: '#bbb',
        wrapperClass: 'slimScrollDiv',
        railColor: '#eaeaea',
        position: 'right',
        alwaysVisible: true,
        railVisible: true,
        disableFadeOut: false,
        start: 'bottom',
    });
});
