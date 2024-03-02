function slideBlock() {
  let body = $(this).siblings('.block-body');
  if (body.is(':hidden')) {
    body.slideDown('slow');
  } else {
    body.slideUp('slow');
  }
}
