$(document).ready(() => {
    $('li#preview-action').click(() => render_item_page(get_page_qid(), 'preview'));
    $("input#lookup-input").keyup((event) => {
        if(event.keyCode === 13){
            lookupItem(get_value_from_event(event));
        }
    });
});


const initializeStatementPropertySelector = () => {
  const options = selectorToDataArray('.sidebar-property-li');
  renderPropertyPicker(
    '#statement-div',
    'Statement',
    options,
    false,
    false,
    handleStatementPropertyChange,
  );
};


const handleStatementPropertyChange = (uuid, propertyId) => {
  clear_claim_constructor();
  $('.add-claim-btn, .add-qualifier-btn').fadeOut('slow').remove();
  bindAddButton(uuid);
  fetch_qualifier_properties(propertyId, (data) => {
    $('<button class="add-qualifier-btn glow" />')
      .html('add qualifier')
      .prependTo('#statement-actions')
      .click(() => renderPropertyPicker(
        '#statement-div',
        'Qualifier',
        data,
        true,
        true,
        null,
      ));
  });
}


const renderPropertyPicker = (
  appendTo,
  propertyType,
  options,
  removable,
  multiple,
  callback,
) => {
  const uuid = `create-claim-property-${propertyType}-${new Date().getTime()}`;
  const uuidSelector = `#${uuid}`;
  const ctx = { type: propertyType, uuid };
  const $elem = get_template('#wikidp-contribute-input', ctx);
  $(uuidSelector, $elem).selectize({
    options,
    labelField:'label',
    valueField: 'id',
    placeholder: 'select a property',
    searchField: ['label', 'id'],
    render: {
      option: (item) => get_template('#wikidp-property-autocomplete', item)
    },
    onChange: (value) => {
      if (value !== ''){
        initializeClaim(uuidSelector);
        if (callback) return callback(uuidSelector, value);
      }
    }
  });
  if (removable){
    const closeHtml = '<i class="fa fa-times contribute-input-close" />';
    const $close = $(closeHtml).click(() => $elem.slideUp('slow').remove());
    $elem.append($close);
  }
  if (multiple) {
    $elem.hide(0).appendTo(appendTo).slideDown('slow');
  }
  else {
    $(appendTo).hide(0).html($elem).slideDown('slow');
  }
  return $elem;
}


function set_property_picker(selector, value){
    let selectizeObj = $(selector).eq(0).data('selectize');
    if (!!selectizeObj) return (value !== null) ? selectizeObj.setValue(value) : selectizeObj.clear();
    return false;
}


const sidebar_property_click = (elm) => {
  const pid = $(elm).data('id');
  console.log(elm, pid);
  set_property_picker('.property-selector.Statement-selectize', pid);
};


function get_property_from_selectize($elm){
    let val = $elm.val();
    return $elm.data().selectize.options[val];
}

const setAddClaimButton = (bool, msg= 'add claim') => {
  const $btn = $('.add-claim-btn').html(msg);
  if (bool){
    return $btn.addClass('btn-on').removeClass('btn-off')
      .attr('disabled', false);
  }
  return $btn.addClass('btn-off').removeClass('btn-on').attr('disabled', true);
}

const toQid = (idNumber) => `Q${idNumber}`;

const initializeClaim = (uuidSelector) => {
  const $selector = $(uuidSelector);
  const { value_type: type } = get_property_from_selectize($selector);
  let template = `
    <input
      class="claim-value text-medium"
      placeholder="enter value here"
    />
  `;
  const $div = $(`${uuidSelector}-value-div`).fadeOut(400, () => {
    $div.empty();
    switch (type) {
      case 'Time':
        const $dateInput = $(template);
        $div.append($dateInput);
        $dateInput.datepicker({
          changeMonth: true,
          changeYear: true,
          dateFormat: 'yy-mm-dd',
        });
        break;
      case 'Url':
        template = `
          <input
            class="claim-value text-medium"
            placeholder="https://example.com"
            type="url"
          />
        `;
        $div.append($(template));
        break;
      case 'WikibaseItem':
        template = `
          <input
            class="claim-value text-medium"
            placeholder="1234"
            type="number"
          />
        `;
        const $input = $(template).on('input', debounce(
          () => {
            setAddClaimButton(false, 'fetching...');
            getItemSummary(toQid($input.val()), (item) => {
              $input.data('item', item);
              setAddClaimButton(true);
            });
          },
          250
        ));
        $div.append('Q', $input);
        break;
      case 'ExternalId':
      case 'Monolingualtext':
      case 'Quantity':
      case 'String':
      default:
        $div.append($(template));
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

const getClaims = () => $('.added-claim-li');
const getClaimMessage = () => $('#claimsMessage');
const getSaveBtn = () => $('#saveClaimsBtn');
const getSaveContainer = () => $('#saveClaimsLi');
const getItemLinkLi = () => $('#goToClaimsLi');

function serializeClaimList(){
    return getClaims().map((index, elem) => $(elem).data('claim')).get();
}

const clearClaims = () => getClaims().remove();
const clearClaimMessage = () => getClaimMessage().html('');
const hideSave = () => {
  getSaveBtn().attr('disabled', true);
  getSaveContainer().hide();
}
const hideItemLink = () => getItemLinkLi().hide();
const enableSave = () => {
  getSaveBtn().attr('disabled', false).show();
  getSaveContainer().show();
};
const resetForm = () => {
  clearClaims();
  clearClaimMessage();
  hideSave();
  hideItemLink();
}

function claimFormValidation(){
  const uuid = $(this).data('uuid');
  const claimData = get_claim_data_from_input(uuid);
  claimData.qualifiers = $('select.Qualifier-selectize').map((index, elem) => {
    let uuid = $(elem).attr('id');
    return uuid ? get_claim_data_from_input('#'+uuid) : null;
  }).get();
  render_added_claim(claimData);
  enableSave();
  $('#clearClaimsLi').show();
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


const saveClaims = () => {
  const $saveBtn = $('#saveClaimsBtn').attr('disabled', true).html('Saving...');
  const qid = get_page_qid();
  const data = serializeClaimList();
  const $messageLi = $('#claimsMessage');
  $.ajax({
    type: 'POST',
    url: `/api/${qid}/claims/write`,
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
    data: JSON.stringify(data),
    success: (response) => {
      console.log(response);
      const { message } = response;
      $saveBtn.hide().html('SAVE TO WIKIDATA');
      $messageLi.html(message);
      getItemLinkLi().show();
    },
    error: (error) => {
      console.error(error);
      $messageLi.html('There was an Issue Saving this Data to Wikidata.');
      enableSave();
      $saveBtn.html('SAVE TO WIKIDATA');
    }
  });
};


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

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
const debounce = (func, wait, immediate) => {
	let timeout;
	return (...arguments) => {
		const context = this, args = arguments;
		const later = () => {
			timeout = null;
			if (!immediate) func.apply(context, args);
		};
		const callNow = immediate && !timeout;
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
		if (callNow) func.apply(context, args);
	};
};
