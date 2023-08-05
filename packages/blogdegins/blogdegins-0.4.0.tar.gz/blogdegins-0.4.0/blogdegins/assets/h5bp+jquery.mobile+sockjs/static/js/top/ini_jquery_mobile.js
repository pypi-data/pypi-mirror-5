/*
 *  This file must be before jquery.mobile.js
 *  in order to receive and process the "mobileinit" event.
 */

;(function (exports) {
    'use strict';

    $.support.cors = true;

    $(document).one("mobileinit", function () {
        $.mobile.allowCrossDomainPages = true;
        $.mobile.defaultPageTransition = 'none';
    });

}(this));
