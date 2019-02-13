$(document).ready(() => {
    $('li#contribute-action').click(() => render_item_page(get_page_qid(), 'contribute'));
    $('.scroller').scroll(() => $.qLabel.switchLanguage(get_page_language()));
    $('#languageSelect').change(() => $.qLabel.switchLanguage(get_page_language()));
    $('img.property-image').fadeIn(4000);
});


function sidebar_property_click(elm){
    let $elm = $(elm);
    if($elm.data('count') > 0){
        let this_pid = $elm.data('id');
        let $scrollDiv = $(`.claims-table tr[data-pid="${this_pid}"]`);
        $scrollDiv.addClass('scroll-highlight');
        $('#claims-scroller').scrollTo($scrollDiv, 1000, {
            onAfter: () =>  setTimeout(() => $scrollDiv.removeClass('scroll-highlight'), 1000)
        })
    }
    else{
        alert('There are currently no statements with this property recorded. If you know of some to add, click ' +
            'the contribute button to create a statement for this property.')
    }
}
