var babyTracker = new BabyTracker('http://localhost:6543/api/');

$(document).bind("mobileinit", function() {
    $.mobile.touchOverflowEnabled = true;
    $.support.cors = true;
    $.mobile.allowCrossDomainPages = true;
    $.mobile.defaultPageTransition = 'pop';
});


// $("#login-page").live('pageinit', function(event) {

//     // Do we have a valid user?
//     if(localStorage.user) {
//         if(localStorage.user.constructor != BabyTracker.User) {
//             delete localStorage.user;
//         }
//     }

//     // ... if so, update and go to home page immediately
//     if(localStorage.user) {
//         localStorage.user.update(function(user) {
//             localStorage.user = user;
//             $.mobile.changePage('home.html', {
//                 transition: 'none'
//             });
//         }, function(status, error) {
//             delete localStorag.user;
//         });
//     }

//     $("#login-form").submit(function(event) {
//         event.preventDefault();

//         var username = $("#login-form input[name=username]").val();
//         var password = $("#login-form input[name=password]").val();

//         $.mobile.showPageLoadingMsg();
//         babyTracker.login(username, password, function(user) {
//             localStorage.user = user;
//             $.mobile.changePage('home.html', {
//                 transition: 'none'
//             });
//         }, function(status, error) {
//             $("#error-message-details").html(error.error);
//             $.mobile.changePage('#error-dialog', {
//                 transition: 'pop',
//                 role: 'dialog'
//             });
//         });

//         return false;
//     });
// });