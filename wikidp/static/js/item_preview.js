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
        let isExternalId = $elm.data("value_type") === "ExternalId";
        let tableClass = (isExternalId) ? ".ex-links-table" : ".claims-table";
        let scrollerId = (isExternalId) ? "#other-info-scroller" : "#claims-scroller";
        let $scrollDiv = $(`${tableClass} a[data-entity-id="${this_pid}"]`).parents('tr').addClass('scroll-highlight');

        $(scrollerId).scrollTo($scrollDiv, 1000, {
            onAfter: () =>  setTimeout(() => $scrollDiv.removeClass('scroll-highlight'), 1000)
        })
    }
    else{
        alert('There are currently no statements with this property recorded. If you know of some to add, click ' +
            'the contribute button to create a statement for this property.')
    }
}
