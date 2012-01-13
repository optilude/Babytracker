// ==========
// Page setup
// ==========

$(document).ready(function() {
    $.mobile.touchOverflowEnabled = true;
    $.support.cors = true;
    $.mobile.allowCrossDomainPages = true;
    $.mobile.defaultPageTransition = 'none';
});

// =======
// Helpers
// =======

/**
 * Fairly ugly hack to show the error.html page
 * as a dialog with a custom title and detail message.
 * It seems query string parameters are lost with
 * the 'dialog' role.
 */
function showError(title, detail) {
    sessionStorage['error-title'] = title;
    sessionStorage['error-detail'] = detail;
    $.mobile.changePage('error.html', {
        transition: 'pop',
        role: 'dialog'
    });
}
$("#error-dialog").live('pageinit', function(event, data) {
   $("#error-message-title").html(sessionStorage['error-title']);
   $("#error-message-details").html(sessionStorage['error-detail']);
});

function normalizeName(name) {
    return name.replace(' ', '-').toLowerCase();
}

/**
 * Local storage abstraction
 */

var BabyTrackerLocal = function(session, storage) {
    this.session = session;
    this.storage = storage;
};
BabyTrackerLocal.prototype = {

    _storageGet: function(key) {
        if(key in this.storage)
            try {
                return JSON.parse(this.storage[key]);
            } catch(e) {
                console.log("Invalid value " + this.storage[key] + "under key " + key);
                delete this.storage[key];
                return null;
            }
        return null;
    },

    _storageSet: function(key, value) {
        this.storage[key] = JSON.stringify(value);
    },

    // Preferences

    getDefaultEntryType: function() {
        return this.storage['prefs.defaultEntryType'] || 'breast_feed';
    },

    setDefaultEntryType: function(value) {
        this.storage['prefs.defaultEntryType'] = value;
    },

    getDaysOfHistory: function() {
        return parseInt(this.storage['prefs.daysOfHistory'] || 14);
    },

    setDaysOfHistory: function(value) {
        this.storage['prefs.daysOfHistory'] = value;
    },

    getInactiveBabies: function() {
        var inactive = this.storage['prefs.inactiveBabies'];
        if(!inactive) {
            return [];
        }
        try {
            return JSON.parse(inactive);
        } catch(e) {
            return [];
        }
    },

    setInactiveBabies: function(value) {
        this.storage['prefs.inactiveBabies'] = JSON.stringify(value);
    },


    // User

    getUser: function(refresh) {
        var user = this._storageGet('user');
        if(user) {
            user = new BabyTracker.User(user);
        }
        if(refresh && user) {
            var self = this;
            user.update(function(user) {
                self.setUser(user);
            }, function(status, error) {
                user = null;
                self.setUser(null);
            }, false); // synchronous
        }
        return user;
    },

    setUser: function(user) {
        this._storageSet('user', user);
    }

};


// =======================================================
// Globals handles to the remote API and the local storage
// =======================================================

babyTracker = new BabyTracker('http://localhost:6543/api/');
babyTrackerLocal = new BabyTrackerLocal(sessionStorage, localStorage);

// ===============
// Page flow logic
// ===============

/**
 * All logged in pages
 */
$(".logged-in-page").live('pagebeforecreate', function(event) {
    var page = this;

   // Do we have a valid user? If not, go to the login page
    var user = babyTrackerLocal.getUser(true);
    if(user == null) {
        $.mobile.changePage('index.html');
    } else {
        $(".user-name", page).html(user.name);
    }
});

/**
 * Login page
 */
$("#login-page").live('pageinit', function(event) {
    var page = this;

    // Do we have a valid user? If so, go straight to home.
    var user = babyTrackerLocal.getUser(true);
    if(user != null) {
        $.mobile.changePage('home.html');
    }

    // When we submit the form, log in.
    $("#login-form", page).submit(function(event) {
        event.preventDefault();

        var username = $("#login-form input[name=username]").val();
        var password = $("#login-form input[name=password]").val();

        $.mobile.showPageLoadingMsg();
        babyTracker.login(username, password, function(user) {
            babyTrackerLocal.setUser(user);
            $.mobile.changePage('home.html');
        }, function(status, error) {
            switch(status) {
                case 200:
                    break;
                case 401:
                    showError("Login failure", error.error);
                    break;
                default:
                    showError("Unkonwn error", error.error);
            }

        });

        return false;
    });
});

/**
 * Home page
 */
$("#home-page").live('pageinit', function(event) {
    var page = this;

    $(".logout-button", page).bind('vclick', function(event) {
        event.preventDefault();

        babyTracker.logout(function(root) {
            $.mobile.changePage('index.html');
        }, function(status, error) {
            showError("Unable to log out", error.error);
        });

        return false;
    });

});

/**
 * New entry page
 */
$("#new-entry-page").live('pagebeforecreate', function(event) {
    var page = this;

    // Duplicate the baby entry once for each baby

    var user = babyTrackerLocal.getUser();
    var inactiveBabies = babyTrackerLocal.getInactiveBabies();

    $(".babyEntryClone").remove();
    for(var i = 0; i < user.babies.length; ++i) {
        var baby = user.babies[i];
        var normalizedName = normalizeName(baby.name);

        if(inactiveBabies.indexOf(normalizedName) != -1)
            continue;

        $("#baby-entry-template", page)
            .clone()
            .appendTo("#new-entry-form")
            .attr('id', '')
            .addClass('babyEntryClone')
            .each(function () {
                $(".babyName", this).html(baby.name);
                $("input,select,label", this).each(function() {
                    var id = $(this).attr('id');
                    var name = $(this).attr('name');
                    var for_ = $(this).attr('for');

                    if(id)
                        $(this).attr('id', normalizedName + '.' + id);
                    if(name)
                        $(this).attr('name', normalizedName + '.' + name);
                    if(for_)
                        $(this).attr('for', normalizedName + '.' + for_);
                });
            });
    }
    $("#baby-entry-template", page).hide();
});

$("#new-entry-page").live('pagebeforeshow', function(event) {
    var page = this;

    function initEntryType() {
        var type = $("input[name=entry_type]:checked", page).val();

        $("[data-entry-type]", page).each(function() {
            var allowedTypes = $(this).attr('data-entry-type').split(" ");
            if(allowedTypes.indexOf(type) == -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    }

    // Show/hide form elements when the entry type is changed
    $("input[name=entry_type]").change(initEntryType);

    // Set the default entry type
    var defaultEntryType = babyTrackerLocal.getDefaultEntryType();
    $("input[name='entry_type']", page).filter("[value='" + defaultEntryType + "']").attr('checked', true).checkboxradio("refresh");
    initEntryType();

    // Set the start date and time
    var now = new Date();
    $("select[name='start.day'] option[value='" + now.getDate() + "']", page).attr('selected', true);
    $("select[name='start.day']").selectmenu("refresh");
    $("select[name='start.month'] option[value='" + (now.getMonth() + 1) + "']", page).attr('selected', true);
    $("select[name='start.month']").selectmenu("refresh");
    $("select[name='start.year'] option[value='" + now.getFullYear() + "']", page).attr('selected', true);
    $("select[name='start.year']").selectmenu("refresh");
    $("select[name='start.hour'] option[value='" + (now.getHours() < 10 ? "0" + now.getHours() : now.getHours()) + "']", page).attr('selected', true);
    $("select[name='start.hour']").selectmenu("refresh");
    $("select[name='start.minute'] option[value='" + (now.getMinutes() < 10 ? "0" + now.getMinutes() : now.getMinutes()) + "']", page).attr('selected', true);
    $("select[name='start.minute']").selectmenu("refresh");
});

$("#new-entry-page").live('pageinit', function(event) {
    var page = this;

    $("#new-entry-save", page).bind("vclick", function(event) {

        

    });

});

/**
 * Settings page
 */
$("#settings-page").live('pagebeforeshow', function(event) {
    var page = this;

    var user = babyTrackerLocal.getUser();

    var inactiveBabies = babyTrackerLocal.getInactiveBabies();
    $("#active-babies-list", page).html("");
    for(var i = 0; i < user.babies.length; ++i) {
        var baby = user.babies[i];
        var normalizedName = normalizeName(baby.name);

        var babyHTML = '<input type="checkbox" name="activeBaby" value="'
                     + normalizedName + '" id="settings-baby-'
                     + normalizedName + '"';
        if(inactiveBabies.indexOf(normalizedName) == -1) {
            babyHTML += ' checked="checked" />';
        } else {
            babyHTML += '/>';
        }
        babyHTML += '\n<label for="settings-baby-' + normalizedName + '">' + baby.name + '</label>';

        $("#active-babies-list", page).append(babyHTML);
    }

    var defaultEntryType = babyTrackerLocal.getDefaultEntryType();
    $("input[name='entry_type']", page).filter("[value='" + defaultEntryType + "']").attr('checked', true).checkboxradio("refresh");

    var daysOfHistory = babyTrackerLocal.getDaysOfHistory();
    $("input[name='daysOfHistory']", page).val(daysOfHistory);

    $(page).trigger("create");

});
$("#settings-page").live('pageinit', function(event) {
    var page = this;

    $("#settings-save", page).bind("vclick", function(event) {

        var daysOfHistory = $("input[name='daysOfHistory']").val();
        var defaultEntryType = $("input[name='entry_type']:checked", page).val();

        var inactiveBabies = [];
        $("input[name='activeBaby']:not(:checked)", page).each(function () {
            inactiveBabies.push($(this).val());
        });

        babyTrackerLocal.setDaysOfHistory(daysOfHistory);
        babyTrackerLocal.setDefaultEntryType(defaultEntryType);
        babyTrackerLocal.setInactiveBabies(inactiveBabies);

    });

});