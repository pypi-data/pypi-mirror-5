/**
 * Copyright (c) 2009 ableton.com (robert.feldbinder at ableton.com)
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 *
 * A simple plugin that can update
 * the content of multiple container elements
 *
 * Lets say there are 2 elements with specific ids
 *  <div id="box1">some content</div>
 *  <div id="box2">some other content</div>
 * then the given URL will return
 *  <div id="update_container">
 *    <div id="update_box1">new content</div>
 *    <div id="update_box2">more new content</div>
 *  </div>
 *
 * Only the content will be replaced, the elements are
 * containers that make the connection between old and
 * new content.
 *
 * The URL is given by the clicked element
 *   <a href="replace_content.html" class="selector_cls">click me<a>
 *   $('selector_cls').update_content()
 * or with the plugin call
 *   <div class="selector_cls">click me</div>
 *   $('selector_cls').update_content('replace_content.html')
**/
(function($) {
  jQuery.fn.update_content = function(url) {
    jQuery(this).live('click', function() {
        if (!url) {
            var url = jQuery(this).attr('href');
        }
        update(url);
        return false;
    });
  }
})(jQuery);

// Gets the content from a given url and callbacks update_content
function update(url) {
    jQuery('<div>').load(url + ' div', update_content);
};

//Tries to update elements for a given content
//this only works if the surrounding element has the
//id 'update_container' and the containing elements match
//with the existing elements like
//<div id="update_elem1" /> will update <div id="elem1"
function update_content(content, target) {
    var elem = jQuery(content);
    if (elem[1]) {
        //in case the content is wrapped in a <body>
        var container = jQuery(elem[1]);
    }
    else {
        var container = elem;
    }
    if (container.attr('id') == 'update_container') {
        container.children().each(function() {
            child_id = jQuery(this).attr('id').slice(7);
            jQuery('#' + child_id).fadeOut('fast');
            jQuery('#' + child_id).html(jQuery(this).html());
            jQuery('#' + child_id).fadeIn('slow');
        });
        if (elem[3]) {
            //again, in case the content is wrappend
            //in a body tag there might be also a script tag
            //that enables new js function for the content.
            eval(jQuery(elem[3]).html());
        }
        return true;
    }
    else if (container.attr('id') == 'redirect_url') {
        window.location.href = container.attr('longdesc');
    }
    else {
        //for simply loading some content in a specific target
        $(target).html(content);
        return false;
    }
}


