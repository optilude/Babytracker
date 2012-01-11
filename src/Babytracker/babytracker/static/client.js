
/**
 * Main API object. Initialise with a base URL for the BabyTracker API,
 * usually http://<domain>/api/
 */
var BabyTracker = function(url) {
    this.url = url;
    this.user = null;
    this.login_url = url + '@@login';
    this.logout_url = url + '@@logout';
};

BabyTracker.prototype = {

    /**
     * Initialise.
     * Callback is called with the initialised root object.
     */
    initialize: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'GET',
            url: self.url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                self.login_url = data['login_url'];
                self.logout_url = data['logout_url'];
                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Log in.
     * Callback is called with the root BabyTracker object and a User
     * object for the logged in session.
     */
    login: function(username, password, callback) {
        var self = this;
        jQuery.ajax({
            type: 'POST',
            url: self.login_url,
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                password: password
            }),
            processData: false,
            xhrFields: {
                withCredentials: true
            },
            success: function(data, textStatus, jqXHR) {
                user = new BabyTracker.User(data);
                self.user = user;
                if(callback != undefined) {
                    callback(user);
                }
            }
        });
    },

    /**
     * Log out.
     * Callback is called with the root BabyTracker object.
     */
    logout: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'POST',
            url: self.logout_url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    }
};

/**
 * Entry factory. data must contain a key entry_type and whatever
 * data is required for that entry type.
 */
BabyTracker._createEntry = function(data) {
    entry_type = data['entry_type'];
    factory = BabyTracker._entryTypeMap[entry_type];
    return factory(data);
};
BabyTracker._entryTypeMap = {}; // poplated below

// Domain model (namespaced). These match the JSON representations
// expected/returned by the server-side API. Functions are augmented by
// prototype.

BabyTracker.User = function(data) {
    this.url = data['url'] || null;
    this.email = data['email'] || null;
    this.name = data['name'] || null;
    this.babies = [];

    babies = data['babies'];
    if(babies != null && babies != undefined) {
        for(var i = 0; i < babies.length; ++i) {
            this.babies.push(new BabyTracker.Baby(babies[i]));
        }
    }
};
BabyTracker.User.prototype = {

    /**
     * Update this user object with details from the server.
     * Callback is called with the updated User object.
     */
    update: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'GET',
            url: self.url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                jQuery.extend(self, data);

                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Save changes to this user object to the server.
     * Callback is called with the updated User object.
     */
    save: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'PUT',
            url: self.url,
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(self),
            processData: false,
            success: function(data, textStatus, jqXHR) {
                jQuery.extend(self, data);

                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Add a new Baby object
     * Callback is called with the User object and the new Baby object.
     */
    addBaby: function(baby, callback) {
        var self = this;
        jQuery.ajax({
            type: 'POST',
            url: self.url,
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(baby),
            processData: false,
            success: function(data, textStatus, jqXHR) {
                baby = BabyTracker.Baby(data);
                self.babies.push(baby)

                if(callback != undefined) {
                    callback(self, baby);
                }
            }
        });
    }

};

BabyTracker.Baby = function(data) {
    this.url = data['url'] || null;
    this.dob = data['dob'] || null; // TODO: Date conversion?
    this.name = data['name'] || null;
    this.gender = data['gender'] || null;
};
BabyTracker.Baby.prototype = {

    /**
     * Update this baby object with details from the server.
     * Callback is called with the updated Baby object.
     */
    update: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'GET',
            url: self.url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                jQuery.extend(self, data);

                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Save changes to this baby object to the server
     * Callback is called with the updated Baby object.
     */
    save: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'PUT',
            url: self.url,
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(self),
            processData: false,
            success: function(data, textStatus, jqXHR) {
                jQuery.extend(self, data);

                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Delete this baby object from the server
     * Callback is called with the parent User object.
     */
    delete: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'DELETE',
            url: self.url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                var user = new BabyTracker.User(data);

                if(callback != undefined) {
                    callback(user);
                }
            }
        });
    },

    /**
     * Get a list of entries for the baby in the date/time range start to end,
     * optionally filtering by entry type. start, end and entry_type may be
     * null.
     * Callback is called with the Baby object and a list of Entry objects.
     */
    getEntries: function(start, end, entry_type, callback) {
        // TODO: Date conversion?
        var self = this;
        jQuery.ajax({
            type: 'GET',
            url: self.url,
            dataType: 'json',
            data: JSON.stringify({
                start: start,
                end: end,
                entry_type: entry_type,
            }),
            processData: false,
            success: function(data, textStatus, jqXHR) {
                var arr = [];
                for(var i = 0; i < data.length; ++i) {
                    arr.push(BabyTracker._createEntry(data[i]));
                }

                if(callback != undefined) {
                    callback(self, arr);
                }
            }
        });
    },

    /**
     * Add a new entry object.
     * Callback is called with the Baby object and the new Entry object.
     */
    addEntry: function(entry, callback) {
        var self = this;
        jQuery.ajax({
            type: 'POST',
            url: self.url,
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(entry),
            processData: false,
            success: function(data, textStatus, jqXHR) {
                entry = BabyTracker._createEntry(data);

                if(callback != undefined) {
                    callback(self, entry);
                }
            }
        });
    }

};

BabyTracker.Entry = function(data) {
    // abstract
};
BabyTracker.Entry.prototype = {

    /**
     * Update this entry object with details from the server
     * Callback is called with the updated Entry object.
     */
    update: function(callback) {
        var self = this;
        jQuery.ajax({
            type: 'GET',
            url: self.url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                jQuery.extend(self, data);

                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Save changes to this entry object to the server
     * Callback is called with the updated Entry object.
     */
    save: function() {
        var self = this;
        jQuery.ajax({
            type: 'PUT',
            url: self.url,
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(self),
            processData: false,
            success: function(data, textStatus, jqXHR) {
                jQuery.extend(self, data);

                if(callback != undefined) {
                    callback(self);
                }
            }
        });
    },

    /**
     * Delete this baby object from the server
     * Callback is called with the parent Baby object.
     */
    delete: function() {
        var self = this;
        jQuery.ajax({
            type: 'DELETE',
            url: self.url,
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                var baby = new BabyTracker.Baby(data);

                if(callback != undefined) {
                    callback(baby);
                }
            }
        });
    },

};

BabyTracker.BreastFeed = function(data) {
    this.entry_type = 'breast_feed';
    this.url = data['url'] || null;
    this.start = data['start'] || null; // TODO: Date conversion?
    this.end = data['end'] || null; // TODO: Date conversion?
    this.note = data['note'] || null;
    this.left_duration = data['left_duration'] || null;
    this.right_duration = data['right_duration'] || null;
};
BabyTracker.BreastFeed.prototype = new BabyTracker.Entry();
BabyTracker._entryTypeMap['breast_feed'] = BabyTracker.BreastFeed;

BabyTracker.BottleFeed = function(data) {
    this.entry_type = 'bottle_feed';
    this.url = data['url'] || null;
    this.start = data['start'] || null; // TODO: Date conversion?
    this.end = data['end'] || null; // TODO: Date conversion?
    this.note = data['note'] || null;
    this.amount = data['amount'] || null;
};
BabyTracker.BottleFeed.prototype = new BabyTracker.Entry();
BabyTracker._entryTypeMap['bottle_feed'] = BabyTracker.BottleFeed;

BabyTracker.MixedFeed = function(data) {
    this.entry_type = 'mixed_feed';
    this.url = data['url'] || null;
    this.start = data['start'] || null; // TODO: Date conversion?
    this.end = data['end'] || null; // TODO: Date conversion?
    this.note = data['note'] || null;
    this.left_duration = data['left_duration'] || null;
    this.right_duration = data['right_duration'] || null;
    this.topup = data['topup'] || null;
};
BabyTracker.MixedFeed.prototype = new BabyTracker.Entry();
BabyTracker._entryTypeMap['mixed_feed'] = BabyTracker.MixedFeed;

BabyTracker.Sleep = function(data) {
    this.entry_type = 'sleep';
    this.url = data['url'] || null;
    this.start = data['start'] || null; // TODO: Date conversion?
    this.end = data['end'] || null; // TODO: Date conversion?
    this.note = data['note'] || null;
    this.duration = data['duration'] || null;
};
BabyTracker.Sleep.prototype = new BabyTracker.Entry();
BabyTracker._entryTypeMap['sleep'] = BabyTracker.Sleep;

BabyTracker.NappyChange = function(data) {
    this.entry_type = 'nappy_change';
    this.url = data['url'] || null;
    this.start = data['start'] || null; // TODO: Date conversion?
    this.end = data['end'] || null; // TODO: Date conversion?
    this.note = data['note'] || null;
    this.contents = data['contents'] || null;
};
BabyTracker.NappyChange.prototype = new BabyTracker.Entry();
BabyTracker._entryTypeMap['nappy_change'] = BabyTracker.NappyChange;
