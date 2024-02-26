$(function() {
  "use strict";
  if (!cu) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  if (!window.location.hash) showIndex(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  if (window.localStorage.getItem('token')) {
    //pass;
  } else {
    if (window.location.hash === '#login') {
      login();
      renderTF('.today-field', dt);
    }
    if (window.location.hash == '#get-password') {
      reg();
      renderTF('.today-field', dt);
    }
    $('body').on('click', '#login-submit', loginSubmit);
    $('body').on('click', '#login-reg', loginReg);
    $('body').on('click', '#rcaptcha-reload',
      {field: '#rcaptcha-field', suffix: '#rsuffix', captcha: '#rcaptcha'},
      captchaReload);
    $('body').on('click', '#lcaptcha-reload',
      {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
      captchaReload);
  }
  $(window).bind('hashchange', function() {
    if (window.localStorage.getItem('token')) {
      //pass;
    } else {
      if (window.location.hash === '#login') {
        login();
      }
      if (window.location.hash === '#get-password') {
        reg();
      }
    }
  });
});
