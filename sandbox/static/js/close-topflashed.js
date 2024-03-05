function closeTopFlashed() {
  let flashed = $(this).parents('.flashed-message');
  let next = flashed.next('.flashed-message');
  let cond = next.length + flashed.prev('.flashed-message').length;
  let ttop = flashed.parents('.top-flashed-block');
  let ttopnext = ttop.next();
  if (!flashed.hasClass('next-block')) {
    flashed.remove();
    next.removeClass('next-block');
  } else {
    flashed.remove();
  }
  if (!cond) {
    ttop.remove();
    ttopnext.removeClass('next-block');
    if ($('#right-panel').length) $('#right-panel').removeClass('next-block');
  }
}
