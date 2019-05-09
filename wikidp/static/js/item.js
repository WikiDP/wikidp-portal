$(document).ready(() => {
    // Initialize property checklist based on default schema:
    $('select#schema-select').change(load_property_checklist_by_schema).change();
    $.qLabel.switchLanguage('en');
    $('select#option-select').change(change_item);
});


function get_page_qid(){
    return $('#panel-frame').data('qid');
}


function get_item_page(){
    return $('#panel-frame').data('item_page');
}


function get_page_language(){
    return $('#languageSelect').val();
}


function get_value_from_event(event){
    return event.currentTarget.value;
}


function pageTransition(form){
    $('div#content-frame').fadeOut(500, () => {
        $('body').append(form);
        form.submit();
    });
}


function load_property_checklist_by_schema(event){
    let schema = get_value_from_event(event);
    let qid = get_page_qid();
    $.get(`/${qid}/checklist/${schema}`, (response) => {
        $('ul#sidebar-property-list').html(response);
        //  TODO: Move to item_contribute.
        if (typeof initialize_statement_property_selector !== 'undefined') {
            initialize_statement_property_selector();
        }
    })
}


function get_template(template_id, data){
    let template_html = $(template_id).html();
    return $(Mustache.render(template_html, data));
}


function change_item(event){
    let qid = get_value_from_event(event);
    let page = get_item_page();
    render_item_page(qid, page)
}


function render_item_page(item_id, page){
    let list = $('option.item-option');
	let options = [];
	for (let i = 0; i < list.length; i++){
	    let $item = $(list[i]).data();
        options.push([
            $item.qid.replace("'","&#39;"),
            $item.label.replace("'","&#39;"),
            $item.description.replace("'","&#39;")
        ])
    }
    options = JSON.stringify(options);
    let $form = get_template('#wikidp-change-item-form', {qid:item_id, options:options, page:page}).hide(0);
    pageTransition($form);
}
