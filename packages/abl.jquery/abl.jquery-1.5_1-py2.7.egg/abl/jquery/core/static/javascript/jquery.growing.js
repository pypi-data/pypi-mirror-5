/**
 * Copyright (c) 2009 ableton.com (robert.feldbinder at ableton.com)
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 *
 * A plugin that can replicate an existing part of a form. Additionally
 * it can delete a line and provide an undo for deleted links.
 * The form must be prepared for this plugin.
 * It was basically designed use in ToscaWidgets.
 * Deleted lines are not really removed from the DOM but are invisable
 * This can make problems with Ajax form sumit. So you have to remove
 * display:none elements before submiting the form.
 *
 * At the moment it can not be configured like other plugins.
 *
 * A form should look like:
 *
 * <form>
 *   <div id="my_grow_container">
 *     <div class="grow_form_elem">
 *       <input id="id_a_0" />
 *       <input id="id_a_0" />
 *       <div class="grow_form_delete_link">delete</div>
 *     </div>
 *     <!- There can be more elements lines -->
 *     <div class="grow_form_elem">
 *       <input id="id_a_1" />
 *       <input id="id_a_1" />
 *       <div class="grow_form_delete_link">delete</div>
 *     </div>
 *     <a class="grow_form_add_link" href="">Add</a>
 *     <a class="grow_form_undo_link" href="">Undo</a>
 *   </div>
 * </form>
 *
 * Its up to you how you style your ids but the first grow_form_elem
 * elements must contain a 0.
 *
 * * The growing part of the form is activated by:
 * $('#my_grow_container').grow_form();
**/
(function($) {

  $.fn.grow_form = function() {

    var undo_list = new Array();
    var root_id = $(this).attr('id').replace('.', '\\.');

    //use live here because this must also work we ne elements
    this.find('.grow_form_add_link').live('click', add_field);
    this.find('.grow_form_delete_link').live('click', del_field);
    this.find('.grow_form_undo_link').live('click', undo_field);
    this.find('input, select, textarea').live('change', show_del);

    function add_field(){
        //find all fields to get the length
        var len = $('#' + root_id + ' .grow_form_add_link').parent().find('.grow_form_elem').length;

        //clone the first child
        var copy = $('#' + root_id + ' .grow_form_add_link').parent().find('.grow_form_elem:first').clone();
        //hide the delete button
        copy.find('a.grow_form_delete_link').css('display', 'none');

        //modifies the copy elements recursively
        function apply_changes(elem) {

              elem.children().each(function() {
                  //change the id and name of the elem, if it has the attribute
                  //because its a copy of the first child it asumes the number 0
                  //was used as an indicator
                  if ($(this).attr('id')) {
                      $(this).attr('id', $(this).attr('id').replace('0', len));
                  }

                if ($(this).attr('name')) {
                       $(this).attr('name', $(this).attr('name').replace('0', len));
                }
                //cleaning value
                if ($(this).attr('value')) {
                       $(this).attr('value', '');
                }
                //cleaning textarea
                if (!($(this).children())) {
                    $(this).html('');
                }
                //cleaning select options
                $(this).find('option').each(function() {
                    $(this).removeAttr('selected');
                });
                //if there is a legend element with a number
                $(this).find('legend').each(function() {
                    $(this).html($(this).html().replace('1', len + 1));
                });
                //apply changes to children elements recursively
                apply_changes($(this));
              });
        }

        //apply changes to the copy element
        apply_changes(copy);
        //make sure that copy is visible
        copy.css('display', 'block');
        //insert the modified (by apply_changes) copy after the last element
        var last_child = $('#' + root_id + ' .grow_form_add_link').parent().find('.grow_form_elem:last').after(copy);
        return false;
    }

    function del_field(){
        var elem = $(this).parent();
        elem.css('display', 'none');
        undo_list.push(elem);
        // display the undo link
        $('#' + root_id + ' .grow_form_undo_link').css('display', 'block');
        return false;
    }

    function undo_field() {
        var field = undo_list.pop();
        field.css('display', 'block');
        if (undo_list.length == 0) {
            //hide the undo link
            $('#' + root_id + ' .grow_form_undo_link').css('display', 'none');
        }
        return false;
    }

    function show_del() {
    //If an element gets some content inserted a delete image becomes visible
        $(this).parents('.grow_form_elem').find('.grow_form_delete_link').css('display', 'block');
    }

  }
})(jQuery);
