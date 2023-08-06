/**
 * Copyright (c) 2009 ableton.com (robert.feldbinder at ableton.com)
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 *
 * A pager plugin that supports regular and vertical paging
 * Its specially design for the abl.jquery.core.widgets.AjaxPager
 *
 * Requires HTML like the following:
 * 	<div id="my_id">
 *		<div class="pager_content">Whatever content to be paginated</p>
 *		<div class="pager">
 *			<a class="pager_link" href="/url/that/returns/partial/content">a link</a>
 *			...
 *		</div>
 *  </div>
 *
 * For a regular pager initialize the plugin:
 * $("#my_id").pager()
 *
 * For a vertical pager:
 * $("#vertical_list").pager({"pager_type": "vertical"})
 * the pager link should say something like 'more' and the URL
 * should return the content for the next page.
 *
 * Its up to you to configure your URL to indicate something like ?page=2
 * But the URL gets appended a
 * &partial=true (to indicate returning only partial content)
 * &_=1234556  (to prevent caching, IE issue)
 *
 * The returned content should look like the HTML above where
 * the pager_content and pager should reflect the content for the requested page
 **/

(function($) {
  $.fn.pager = function(options) {
    $('#' + $(this).attr('id') + ' .pager_link').live('click', function () {
        load_new_page(this, options);
        return false;
    });
  }
})(jQuery);

function load_new_page(elem, options) {
    if (!options) {
        var options = {};
    }
    //the pagers href defines the URL
    var page_url = $(elem).attr('href');

    //add a partial parameter to GET URL
    //to indicate only partial data is requested
    if (page_url.indexOf('partial') == -1) {
        page_url = page_url + '&partial=1';
    }
    //add a timestamp to prevent caching
    var timestamp = new Date().getTime();
    var arguments = '_=' + timestamp;
    //find the container elem and the old content
    var cont = $(elem).parent().parent();
    var old_content = cont.find('.pager_content');

    $('<div>').load(page_url, arguments, function() {
        //load the new content and find the specific elements
        var new_pager = $(this).find('.pager');
        var new_content = $(this).find('.pager_content').children();
        //replace the pager
        cont.find('.pager').html(new_pager.html());
        //append content for a 'more' pager
          if (options['pager_type'] == 'vertical') {
              old_content.append(new_content.fadeIn('slow'));
          }
          //replace content for a regular pager
        else {
            old_content.html(new_content.fadeIn('slow'));
        }

    });
}
