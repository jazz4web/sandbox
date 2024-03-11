function formatFooter(dt) {
  let footer = $.trim($('#footer-link').text());
  let html = footer + ', ' + dt.year;
  $('#footer-link').html(html);
}
