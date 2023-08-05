$j = jQuery.noConflict();
$j(document).ready(function() {

    /* injects .multiselect into the MultiSelectionWidget for 'styles' field in 
     * edit mode and then turn it into a ui.multiselect widget
     */
    $j('select#styles').addClass('multiselect');
    $j('select#styles').multiselect();
});
