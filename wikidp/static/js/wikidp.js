$(document).ready(() => {
  const $pagecontainer = $('div.page-container')
  $('form#navbarSearch').submit(() => $pagecontainer.fadeOut(500))
  $('div.side-icon-div i#searchToggle').click(toggleSearchForm)
  $('#loginBtn').click(() => { window.location.href = '/profile' })
  $pagecontainer.fadeIn(500)
})

function toggleSearchForm () {
  let $icon = $('div.side-icon-div i#searchToggle').fadeOut('slow')
  $('#main-nav-tabs-container').toggle(1000, () => $('#navbarSearch').fadeToggle(500))
  $icon.toggleClass('fa-search').toggleClass('fa-times-circle-o').fadeIn('slow')
}

function get_item_summary (qid, callback) {
  $.get(`/api/${qid}/summary`, (item) => {
    if (callback) return callback(item)
    return item
  }).fail((error) => console.log(error))
}

function selector_to_data_array (selector) {
  const output = []
  $(selector).each((index, elem) => output.push($(elem).data()))
  return output
}
