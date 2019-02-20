$(document).ready(() => {
    $('li#preview-action').click(() => render_item_page(get_page_qid(), 'preview'));
    $("input#lookup-input").keyup((event) => {
        if(event.keyCode === 13){
            lookupItem(get_value_from_event(event));
        }
    });
});


function initialize_statement_property_selector(){
    let opts = selector_to_data_array('.sidebar-property-li');
    render_property_picker('#statement-div', 'Statement', opts, false, statement_property_change);
}


function statement_property_change(uuid, property_id){
    clear_claim_constructor();
    $('.add-claim-btn, .add-qualifier-btn').fadeOut('slow').remove();
    bindAddButton(uuid);
    fetch_qualifier_properties(property_id, (data) => {
        $('<button class="add-qualifier-btn glow" />').html('add qualifier').prependTo('#statement-actions')
            .click(() => render_property_picker('#statement-div', 'Qualifier', data, true, null));
    });
}


function render_property_picker(append_to_elem, property_type, options, removable, callback){
    let uuid = 'create-claim-property' + ($('.property-selector').length+1);
    let uuid_selector = '#'+uuid;
    let $elem = get_template('#wikidp-contribute-input', {type:property_type, uuid: uuid});
    $(uuid_selector, $elem).selectize({
        options: options,
        labelField:'label',
        valueField: 'id',
        placeholder:"select a property",
        searchField:['label', 'id'],
        render: {
            option: (item) => get_template('#wikidp-property-autocomplete', item)
        },
        onChange: (value) => {
            if (value !== ''){
                initializeClaim(uuid_selector);
                if (callback) return callback(uuid_selector, value);
            }
        }
    });
    if (removable){
        let $close = $('<i class="fa fa-times contribute-input-close"/>').click(() => $elem.slideUp('slow').remove());
        $elem.append($close);
    }
    $elem.hide(0).appendTo(append_to_elem).slideDown('slow');
    return $elem;
}


function set_property_picker(selector, value){
    let selectizeObj = $(selector).eq(0).data('selectize');
    if (!!selectizeObj) return (value !== null) ? selectizeObj.setValue(value) : selectizeObj.clear();
    return false;
}


function sidebar_property_click(elm){
    let pid = $(elm).data('id');
    set_property_picker('.property-selector:first', pid);
}


function get_property_from_selectize($elm){
    let val = $elm.val();
    return $elm.data().selectize.options[val];
}


function set_add_claim_button(bool){
    let $btn = $('.add-claim-btn');
    if (bool){
        return $btn.addClass('btn-on').removeClass('btn-off').attr('disabled', false);
    }
    return $btn.addClass('btn-off').removeClass('btn-on').attr('disabled', true);
}


function initializeClaim(uuid_selector) {
    let prop = get_property_from_selectize($(uuid_selector));
    let type = prop.value_type;
    let $div = $(uuid_selector+'-value-div').fadeOut(400, () => {
        $div.empty();
        switch (type) {
            case 'WikibaseItem':
                let $input = $('<input class="claim-value text-medium" placeholder="1234" type="number"/>').change(() => {
                    set_add_claim_button(false);
                    get_item_summary('Q'+$input.val(), (item) => {
                        $input.data('item', item);
                        set_add_claim_button(true);
                    })
                });
                $div.append('Q', $input);
                break;
            case 'url':
                $div.append('https://', $('<input class="claim-value text-medium" placeholder="www.website.com" type="url"/>'));
                break;
            case 'ExternalId':
            case 'String':
            default:
                $div.append($('<input class="claim-value text-medium" placeholder="enter value here"/>'));
        }
        $div.fadeIn('slow');
    });
}


function fetch_qualifier_properties(pid, callback){
    $.getJSON('/api/' + pid + '/qualifiers', function (data) {
        if (data.length && callback){
            return callback(data);
        }
    });
}


function clear_claim_constructor(){
    $('.contribute-input-div:not(:first)').remove();
    $('.claim-value:first').val(null);
}



function bindAddButton(uuid){
    // TO DO: Let the user submit by enter, below this code does not perform quite as expected
    $('<button class="add-claim-btn btn-on glow" data-uuid="'+uuid+'"/>').click(claimFormValidation).html('add claim')
        .appendTo('#statement-actions');
}


function render_added_claim(data) {
    let $list_item = get_template('#wikidp-added-claim-li', data);
    $list_item.hide(0).data('claim', data);
    $('ul#added-claims').prepend($list_item).scrollTop(0);
    $list_item.slideDown(750);
    $('#statement-actions button').fadeOut('slow').remove();
    set_property_picker('.property-selector:first', null);
    clear_claim_constructor();
}


function serializeClaimList(){
    return $('.added-claim-li').map((index, elem) => $(elem).data('claim')).get();
}


function claimFormValidation(){
    let uuid = $(this).data('uuid');
    let claim_data = get_claim_data_from_input(uuid);
    claim_data.qualifiers = $('select.Qualifier-selectize').map((index, elem) => {
            let uuid = $(elem).attr('id');
            return uuid ? get_claim_data_from_input('#'+uuid) : null;
        }).get();
    render_added_claim(claim_data);
    return $('#saveClaimsLi').show();
}


function get_claim_data_from_input(uuid){
    let $input = $(uuid + '-value-div .claim-value');
    let value = $input.val();
    if (value.length){
        let prop = get_property_from_selectize($(uuid));
        let val_type = prop.value_type;
        let claim_data = {type:val_type, value:value, label:value, pid:prop.id, pidLabel:prop.label};
        switch(val_type){
            case 'WikibaseItem':
                let item = $input.data('item');
                claim_data.value = item.qid;
                claim_data.label = item.label;
                claim_data.description = item.description;
                claim_data.aliases = item.aliases.join(", ");
                return claim_data;
            default:
                // TO DO: HAVE A CASE FOR EX-IDS AND URL'S
                return claim_data;
        }
    }
    return null;
}


function save_claims(){
    let qid = get_page_qid();
    let data = serializeClaimList();
    $.ajax({
        type: 'POST',
        url: "/api/"+qid+"/claims/write",
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(data),
        success: (response) => console.log(response),
        error: (error) => console.log(error)
    })
}


function lookupItem(string){
    $.get("/api/search/"+string, (response) => {
        let $list = $('ul#lookup-results-list').hide(1000);
        $list.empty();
        for (let opt = 0; opt < response.length; opt++){
            let item = response[opt];
            item.aliases = item.aliases.join(", ");
            let $item = get_template('#wikidp-lookup-item', item);
            $list.append($item);
            bind_clipboard_to_element('clipboardBtn-'+item.qid);
        }
        $('div.result-main').click((event) => $(event.target).next('.result-sub').slideToggle());
        $list.fadeIn(1000);
    }).fail((error) => console.log(error))
}


function bind_clipboard_to_element(element_id){
    let elem = document.getElementById(element_id);
    return new Clipboard(elem).on('success', (res) => console.log(res)).on('error', (error) => console.log(error));
}
