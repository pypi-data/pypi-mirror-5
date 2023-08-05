/*
 * Table overlay
 */

$j = jQuery.noConflict();

$j(document).ready(function() {

    $j('table.display-overlay').each(function(i) {
        var table = $j(this);
        var id = table.attr('id');
        caption = table.find('caption');
        caption_text = caption.html();
        caption_text = caption_text==null ? '' : caption_text;
        $j('<a class="table-popup" href="' + ACTUAL_URL + '/@@show_table?id=' + id +'")">' + caption_text + '</a>').insertBefore(table);
        table.hide();
    });

    $j('.table-popup').each(function(i) {
        var anchor = $j(this);
        anchor.prepOverlay({
                subtype: 'ajax',
                width: '90%'
            }
        );
    });

})
