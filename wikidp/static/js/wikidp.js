var oauthController = {
  authorized: false,
  initiate: function () {
    $.ajax({
      url: '/auth',
      type: 'GET',
      dataType: 'json',
      contentType: false,
      processData: false,
      success: function (data, textStatus, jqXHR) {
        console.log(data)
        if (data.auth === false) {
          sessionStorage.setItem('returnTo', window.location.pathname  + window.location.search)
          oauthController.authorize(null)
        } else {
          window.location.href = '/profile'
        }
      },
      // HTTP Error handler
      error: function (jqXHR, textStatus, errorThrown) {
        // Log full error to console
        console.log('Validation Error: ' + textStatus + errorThrown)
        console.log(jqXHR)
      }
    })
  },
  authorize: function (callback) {
    $.ajax({
      url: '/profile',
      type: 'POST',
      data: JSON.stringify({
        authorization: 'sending',
        current_path: window.location.pathname,
        initiate: true
      }),
      dataType: 'json',
      contentType: false,
      processData: false,
      success: function (data, textStatus, jqXHR) {
        console.log(data)
        window.location.href = data.wikimediaURL
      },
      // HTTP Error handler
      error: function (jqXHR, textStatus, errorThrown) {
        // Log full error to console
        console.log('Validation Error: ' + textStatus + errorThrown)
        console.log(jqXHR)
      }
    })
  },
  authCheck: function () {
    $.ajax({
      url: '/auth',
      type: 'GET',
      dataType: 'json',
      contentType: false,
      processData: false,
      success: function (data, textStatus, jqXHR) {
        if (data.auth === false) {
          oauthController.forward()
        } else {
          window.location.href = '/profile'
        }
      },
      // HTTP Error handler
      error: function (jqXHR, textStatus, errorThrown) {
        // Log full error to console
        console.log('Validation Error: ' + textStatus + errorThrown)
        console.log(jqXHR)
      }
    })
  },
  forward: function () {
    $.ajax({
      type: 'POST',
      data: JSON.stringify({
        url: window.location.pathname + window.location.search
      }),
      dataType: 'json',
      contentType: false,
      processData: false,
      success: function (data, textStatus, jqXHR) {
        var gotoURL = sessionStorage.getItem('returnTo') || null
        sessionStorage.removeItem('returnTo')
        if (gotoURL) {
          window.location = gotoURL
        }

        console.log(data)
      },
      // HTTP Error handler
      error: function (jqXHR, textStatus, errorThrown) {
        alert('forward.fail')
        // Log full error to console
        console.log('Validation Error: ' + textStatus + errorThrown)
        console.log(jqXHR)
      }
    })
  }
}

$(document).ready(() => {
  const $pagecontainer = $('div.page-container')
  $('form#navbarSearch').submit(() => $pagecontainer.fadeOut(500))
  $('div.side-icon-div i#searchToggle').click(toggleSearchForm)
  $pagecontainer.fadeIn(500)
  const urlParams = new URLSearchParams(window.location.search)
  if (urlParams.has('oauth_verifier')) {
    oauthController.authCheck()
  }
})

function toggleSearchForm () {
  let $icon = $('div.side-icon-div i#searchToggle').fadeOut('slow')
  $('#main-nav-tabs-container').toggle(1000, () => $('#navbarSearch').fadeToggle(500))
  $icon.toggleClass('fa-search').toggleClass('fa-times-circle-o').fadeIn('slow')
}

const getItemSummary = (qid, callback) => {
  $.get(`/api/${qid}/summary`, (item) => {
    if (callback) return callback(item)
    return item
  }).fail((error) => console.log(error))
}

const selectorToDataArray = (selector) => $(selector).map(
  (index, elem) => $(elem).data()
);
