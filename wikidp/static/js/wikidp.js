$(document).ready(() => {
    let $page_container = $('div.page-container');
    $("form#navbarSearch").submit(() => $page_container.fadeOut(500));
    $('div.side-icon-div i#searchToggle').click(toggle_search_form);
    $("#loginBtn").click(() => $("#loginModal").modal());
    $page_container.fadeIn(500);

});


function toggle_search_form(){
    let $icon = $('div.side-icon-div i#searchToggle').fadeOut('slow');
    $('div.outer-list-div').toggle(1000, () => $('form.navbar-form.navbar-right').fadeToggle(500));
    $icon.toggleClass('fa-search').toggleClass('fa-times-circle-o').fadeIn('slow');
}


function get_item_summary(qid, callback){
    $.get(`/api/${qid}/summary`,  (item) => {
            if (callback) return callback(item);
            return item;
        }).fail((error) => console.log(error));
}


function selector_to_data_array(selector){
    let output = [];
    $(selector).each((index, elem) => output.push($(elem).data()));
    return output;
}
