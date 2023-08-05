// Avoid `console` errors in browsers that lack a console.
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());

// Place any jQuery/helper plugins in here.

/*!
 * jQuery scrollbarWidth - v0.2 - 2/11/2009
 * http://benalman.com/projects/jquery-misc-plugins/
 *
 * Copyright (c) 2010 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */

// Calculate the scrollbar width dynamically!

(function($,undefined,width){
  '$:nomunge'; // Used by YUI compressor.

  $.scrollbarWidth = function() {
    var parent,
      child;

    if ( width === undefined ) {
      parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
      child = parent.children();
      width = child.innerWidth() - child.height(99).innerWidth();
      parent.remove();
    }

    return width;
  };

})(jQuery);
