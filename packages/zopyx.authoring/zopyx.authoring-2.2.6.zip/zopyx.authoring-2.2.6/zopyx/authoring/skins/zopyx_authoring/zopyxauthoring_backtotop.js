/*
 * Add a link to the page top in front before every H2 tag
 */

$j = jQuery.noConflict();
$j(document).ready(function() {
    var count=0;
    $j('h2').each(function(i) {
        if (count > 0)
            $j('<a href="#" class="back-to-top"><img src="++resource++zopyx.authoring/back2top.png"/></a>').insertBefore($j(this));
        count++;
    });
})
