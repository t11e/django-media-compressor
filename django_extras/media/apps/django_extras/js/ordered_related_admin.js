/**
 * Based on http://www.djangosnippets.org/snippets/1053/
 *
 * Automatically fills in the position field for ordered relationships.
 * Makes sure to only do so for existing related objects and allows
 * reordering of them via drag/drop.
 */
jQuery(function ($) {
    var filter = ':has(:input[id$=-id][value!=])';
    $('div.inline-group').sortable({
        items: 'div.inline-related' + filter,
        handle: 'h3:first',
        update: function () {
            $(this).find('div.inline-related' + filter).each(function (i) {
                $(this).find('input[id$=-position]').val(i + 1);
            });
        }
    });
    $('div.inline-related' + filter + ' h3').css('cursor', 'move');
    $('div.inline-related').find('input[id$=-position]').parent('div').hide();
});
