// TODO: Bring inline javascript into js file
$(document).ready(function(){
    $("#loginBtn").click(function(){
        $("#loginModal").modal();
    });
});
$("form#navbarSearch").submit(function(){
  $('div.page-container').fadeOut(500);
  $('form.navbar-form.navbar-right').fadeOut('slow');


});
$('div.side-icon-div i#searchToggle').on('click', function(){
  var icon = $(this);
  if(icon.hasClass('fa-search')){
    $('div.outer-list-div').hide(1000, function(){
      $('form.navbar-form.navbar-right').fadeIn(500);
      icon.fadeOut('slow', function(){
        icon.removeClass('fa-search');
        icon.addClass('fa-times-circle-o');
        icon.fadeIn('slow');
      });
    });
  }
  else{
    $('form.navbar-form.navbar-right').fadeOut('slow', function(){
      $('div.outer-list-div').show(1000)
      icon.fadeOut('slow', function(){
        icon.removeClass('fa-times-circle-o')
        icon.addClass('fa-search')
        icon.fadeIn('slow')
      });
    });
  }
})
$.qLabel.switchLanguage('en')
$(document).ready(function(){$('div.page-container').fadeIn(500)});

function get_item_summary(qid, callback){
    $.get(`/api/${qid}/summary`,  (item) => {
            if (callback) return callback(item);
            else return item;
        }).fail((error) => console.log(error));
}


function selector_to_data_array(selector){
    let output = [];
    $(selector).each((index, elem) => output.push($(elem).data()));
    return output;
}