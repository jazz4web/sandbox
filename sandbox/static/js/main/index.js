$(function() {
  "use strict";
  if (!cu) {
    window.localStorage.removeItem('token');
  }
  let dt = luxon.DateTime.now();
  formatFooter(dt);
  showIndex(dt);
  $('body').on('click', '.close-top-flashed', closeTopFlashed);
  if (window.localStorage.getItem('token')) {
    if (window.location.hash === '#logout') {
      logout();
    }
    if (window.location.hash === '#logout-all') {
      logoutAll();
    }
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
    $('body').on('click', '#reg-submit', regSubmit);
    $('body').on('click', '#rcaptcha-reload',
      {field: '#rcaptcha-field', suffix: '#rsuffix', captcha: '#rcaptcha'},
      captchaReload);
    $('body').on('click', '#lcaptcha-reload',
      {field: '#lcaptcha-field', suffix: '#lsuffix', captcha: '#lcaptcha'},
      captchaReload);
    $('body').on('click', '#crp-submit', createUser);
    $('body').on('click', '#rsp-submit', resetPwd);
  }
  $(window).bind('hashchange', function() {
    if (window.localStorage.getItem('token')) {
      if (window.location.hash === '#logout') {
        logout();
      }
      if (window.location.hash === '#logout-all') {
        logoutAll();
      }
    } else {
      if (window.location.hash === '#login') {
        login();
      }
      if (window.location.hash === '#get-password') {
        reg();
      }
    }
    let crt = parseHash(window.location.hash, '#request-password');
    if (crt) {
      requestPasswd(crt);
    }
    let rst = parseHash(window.location.hash, '#reset-password');
    if (rst) {
      resetPasswd(rst);
    }
  });
  let crt = parseHash(window.location.hash, '#request-password');
  if (crt) {
    requestPasswd(crt);
  }
  let rst = parseHash(window.location.hash, '#reset-password');
  if (rst) {
    resetPasswd(rst);
  }
});
