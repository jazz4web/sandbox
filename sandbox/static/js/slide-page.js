function slidePage(eid) {
  let block = $(eid);
  block.slideDown('slow');
  block.siblings().each(function() {
    $(this).slideUp('slow', function() { $(this).remove(); });
  });
}
