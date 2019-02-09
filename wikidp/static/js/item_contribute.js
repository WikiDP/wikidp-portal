
function pageTransition(form){
    $('div#content-frame').fadeOut(500, function(){
        $('body').append(form);
        form.submit();
    })
}


function initialize_statement_property_selector(){
    let opts = selector_to_data_array('.sidebar-property-li');
    render_property_picker('#statement-div', 'Statement', opts, false, (uuid, property_id) => {
        clear_claim_constructor();
        $('.add-claim-btn').fadeOut('slow').remove();
        bindAddButton(uuid);
        $('.add-qualifier-btn').fadeOut('slow').remove();
        fetch_qualifier_properties(property_id, (data) => {
            let $addQualifierBtn = $('<button class="add-qualifier-btn" />').html('add qualifier');
            $addQualifierBtn.click(() => render_property_picker('#statement-div', 'Qualifier', data, true, null));
            $('#statement-actions').prepend($addQualifierBtn);
        });
    });
}


function get_template(template_id, data){
    let template_html = $(template_id).html();
    return $(Mustache.render(template_html, data));
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
        let $close = $('<i class="fa fa-times contribute-input-close"/>').click(function(){
            $elem.slideUp('slow').remove();
        });
        $elem.append($close);
    }

    $elem.hide(0).appendTo(append_to_elem).slideDown('slow');
    return $elem
}

function set_property_picker(selector, value){
    let selectElm = $(selector).eq(0);
    let selectizeObj = selectElm.data('selectize');
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
    console.log('...initialing value data-type: ' + type);
    let $div = $(uuid_selector+'-value-div').fadeOut(400, () => {
        $div.empty();
        console.log('TYPE= ', type);
        switch (type) {
            case 'WikibaseItem':
                let $input = $('<input class="claim-value" placeholder="1234" type="number"/>').change(() => {
                    set_add_claim_button(false);
                    get_item_summary('Q'+$input.val(), (item) => {
                        $input.data('item', item);
                        set_add_claim_button(true);
                    })
                });
                $div.append('Q', $input);
                break;
            case 'url':
                $div.append('https://', $('<input class="claim-value" placeholder="www.website.com" type="url"/>'));
                break;
            case 'ExternalId':
            case 'String':
            default:
                $div.append($('<input class="claim-value" placeholder="enter value here"/>'));
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

  $('select#option-select').change(function(){
    let list = $('option.item-option');
    let options = [];
    for (let i = 0; i < list.length; i++){
      options.push([$(list[i]).data('qid').replace("'","&#39;"), $(list[i]).data('label').replace("'","&#39;"), $(list[i]).data('description').replace("'","&#39;") ])
    }
    options = JSON.stringify(options);
    let form = $('<form action="/preview" method="post">' +
      '<input type="text" name="qid" value="' + $(this).val() + '" />' +
      '<input type="text" name="optionList" '+"value='"+options+"' />" +
      '</form>');
    $('body').append(form);
    pageTransition(form);
    // return $.post("/preview", {qid:qid})
  });

  $('li#preview-action').click(function(){
    let list = $('option.item-option');
    let options = [];
    for (let i = 0; i < list.length; i++){
      options.push([$(list[i]).data('qid').replace("'","&#39;"), $(list[i]).data('label').replace("'","&#39;"), $(list[i]).data('description').replace("'","&#39;") ])
    }
    options = JSON.stringify(options);
    let form = $('<form action="/preview" method="post">' +
      '<input type="text" name="qid" value="' + $('div#panel-frame').data('qid') + '" />' +
      '<input type="text" name="optionList" '+"value='"+options+"' />" +
      '</form>').hide(0);
    pageTransition(form);

  });


function bindAddButton(uuid){
    // TO DO: Let the user submit by enter, below this code does not perform quite as expected
    let $addClaimBtn = $('<button class="add-claim-btn btn-on" data-uuid="'+uuid+'"/>').click(claimFormValidation).html('add claim');
    $('#statement-actions').append($addClaimBtn);
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
    if (!value.length){
      return null;
    }
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

  function save_claims(){
      let qid = get_page_qid();
    let data = serializeClaimList();
    $.ajax({
      type: 'POST',
      url: "/api/"+qid+"/claims/write",
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      data: JSON.stringify(data),
      success: function(response){
        console.log(response)
      },
      error: function(error){
        console.log(error)
      }
    })
  }


function lookupItem(string){
    //  TODO: Clean this function up and move html to contribute_input_templates.html
    let list = $('ul#lookup-results-list').hide(1000);
    $.get("/api/search/"+string, function(response){
      list.empty();
      for (let opt = 0; opt < response.length; opt++){
        let item = response[opt];
        let qid = item.id;
        let description = item.description;
        if (!description.length){
          description = 'this item has no description'
        }
        list.append(`
          <li class="lookup-result-li">
            <div class="result-main" id="result-main-${qid}" data-qid="${qid}">
              <button data-clipboard-text="${qid}" class="pull-left clipboardBtn" id="clipboardBtn-${qid}" data-qid="${qid}"><i class="fa fa-clipboard"></i> </button>
              <span class="result-label">${item.label}</span></br>
              ${qid} <span class="glyphicon glyphicon-menu-down"></span>
            </div>
            <div class="result-sub" id="result-sub-${qid}">
           <i> &mdash; ${description} &mdash; </i></br></br>
            <span class="sub-aka"><b>Also Referred To As:</b> ${item.aliases}</span>
            </div>
          </li>
          `);
        let btn = document.getElementById('clipboardBtn-'+qid);
        // Thanks to https://clipboardjs.com/ for this object below
        let clipboard = new Clipboard(btn);
        clipboard.on('success', function(e) {
          console.log(e);
        });
        clipboard.on('error', function(e) {
          console.log(e);
        });
      }
      $('div.result-main').click(function(){
        let id = $(this).data('qid');
        $('div#result-sub-'+id).slideToggle('slow');
      });
      list.fadeIn(1000);
      // createItemClaim(pid, pidLabel, response, type)
    }).fail(function(error){
      console.log(error)
    })
}


$("input#lookup-input").keyup((event) => {
    if(event.keyCode === 13){
        lookupItem(this.value);
    }
});
