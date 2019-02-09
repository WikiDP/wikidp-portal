
function get_page_qid(){
    return $('#panel-frame').data('qid');
}


function load_property_checklist_by_schema(schema){
    let qid = get_page_qid();
    $('ul#sidebar-property-list').html('');
    $.get(`/${qid}/checklist/${schema}`, (response) => {
        $('ul#sidebar-property-list').html(response);
        //  TODO: Move to item_contribute.
        if (typeof initialize_statement_property_selector !== 'undefined') {
            initialize_statement_property_selector();
        }
    })
}

// Initialize property checklist based on default schema:
$('select#schema-select').change();
