$(document).ready(() => {
    // Initialize property checklist based on default schema:
    loadOptionSelector();
    $('select#schema-select').change(load_property_checklist_by_schema).change();
    //TODO: Only call qLabel in Prod Config
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


function render_item_page(qid, page){
  const _options = [];
  $('option.item-option').each(function() {
    _options.push($(this).data('qid').replace("'","&#39;"));
  });
  const options = JSON.stringify(_options);
  const ctx = { options, page, qid };
  const $form = get_template('#wikidp-change-item-form', ctx).hide(0);
  pageTransition($form);
}

const get_item_options = () => {
  const data = JSON.stringify(QID_OPTIONS);
  return $.ajax({
    data,
    dataType: 'json',
    type: 'POST',
    contentType: 'application/json',
    url: '/api/items',
  });
}

const loadOptionSelector = async () => {
  const options = await get_item_options();
  const ctx = { options };
  const $html = get_template('#wikidp-item-options',ctx);
  $html.val(get_page_qid());
  $html.change(change_item);
  $('#item-options-container').html($html);
};
