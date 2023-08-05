"use strict";

/**********************************************
 *    BootstrapPy Application ViewModels     *
 *********************************************/

function BootstrapPyViewModel() {
    var self = this;
    var $ = jQuery;

    self.user = ko.observable();
    self.selectedUser = ko.observable();
    self.selectedTemplate = ko.observable('user-grid');
    self.userGridTemplate = ko.observable();
    self.userEditTemplate = ko.observable();
    self.vmUserGrid = new userGridViewModel(self);
    self.vmUser = new userViewModel(self);
};

BootstrapPyViewModel.typesafe = function(that) {

    if (!(that instanceof BootstrapPyViewModel)) {
        throw 'This is not a BootstrapPyViewModel';
    }
    return that;
};

BootstrapPyViewModel.prototype.init = function(callback){
    var self = BootstrapPyViewModel.typesafe(this);

    var userDataAjax = self.getUserData()
        .done()
        .fail(function () {
            console.log('Error');
        });

    return $.when (
        userDataAjax
    )
};

BootstrapPyViewModel.prototype.loadTemplate = function(tmpltName) {
    var self = BootstrapPyViewModel.typesafe(this);
    self.selectedTemplate(tmpltName);

    switch (tmpltName) {
        case 'user-grid':
            if($('#user-grid').length == 0) {
                util.getTemplate('/js/app/templates/userGrid.tmplt.html',
                    '#user-grid', function(template) {
                        self.userGridTemplate('user-grid');
                    });
            }
            break;
        case 'user-edit':
            if($('#user-edit').length == 0) {
                util.getTemplate('/js/app/templates/userEdit.tmplt.html',
                    '#user-edit', function(template){
                        self.userEditTemplate('user-edit');
                    });
            }
            break;
    }
};

function userGridViewModel(rootVm) {
    var self = this;
    self.rootVm = rootVm;

    self.userData = ko.observableArray();
    self.pagesArray = ko.observableArray();
    self.startItemIndex = ko.observable(0);
    self.startItem = ko.observable(0);
    self.endItemIndex = ko.observable(0);
    self.endItem = ko.observable(0);
    self.itemCount = ko.observable(0);
    self.page = ko.observable(0);
    self.pageSize = ko.observable(25);
    self.pageIndex = ko.observable(0);
    self.totalPages = ko.observable(0);

    self.columns =  [{
        header: 'Name',
        field: 'name'
    },{
        header: 'Email',
        field: 'email'
    },{
        header: 'Telephone',
        field: 'telephone'
    },{
        header: 'Start Date',
        field: 'date'
    },{
        header: 'Active',
        field: 'active'
    },{
        field: '',
        header: ''
    }];

    self.setPage = function(idx) {
        self.pageIndex(--idx);
        self.getUserData();
    };

    self.setPageSize = function(pSize) {
        self.selectedPageSize(pSize);
        self.getUserData();
    };

    self.pageNext = function() {
        self.pageIndex((self.totalPages()>self.page()) ? self.pageIndex()+1 : self.pageIndex());
        self.getUserData();
    };

    self.pagePrev = function() {
        self.pageIndex((self.totalPages()>1 && self.page()>1) ? self.pageIndex()-1 : self.pageIndex());
        self.getUserData();
    };

    self.setActive = function(data) {
        var userData = self.userData;

        for (var i = 0; i < userData.length; i++) {
            if (userData[i].id == data.id) {
                userData[i].active = data.active;
            }
        }
        self.updateUserActive(data);
    };

    self.updateUserActive = function(data) {
        $.ajax({
            type: 'POST',
            url: "/api/user_active",
            data: data,
            dataType: 'json',
            success: function (data, textStatus, jqXhr) {
                self.serverResponse(data);
                self.getUserData();
            },
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });
    };

    self.serverResponse = function(data) {
        $.gritter.add({
            title: data.heading,
            text: data.content,
            time: data.timeout,
            sticky: data.sticky
        });
    };

    self.getUserData = function () {
        self.userData.removeAll();
        $.ajax({
            type: "GET",
            url: "/api/users.json",
            cache: false,
            dataType: 'json',
            success: function (data, textStatus, jqXhr) {
                var userData = data;

                self.itemCount(userData.length);
                self.startItemIndex(self.pageIndex() * self.pageSize());
                self.endItemIndex(self.startItemIndex() + self.pageSize());
                self.endItem(self.endItemIndex() > self.itemCount() ? self.itemCount() : self.endItemIndex());
                self.totalPages(Math.ceil(self.itemCount() / self.pageSize()));
                self.page(self.pageIndex() + 1);
                self.startItem(self.startItemIndex() + 1);
                self.pagesArray.removeAll();

                for (var i = 1; i <= self.totalPages(); i++) {
                    var klass =  (self.page() == i) ? 'active' : '';
                    self.pagesArray.push({'pageNum': i, 'klass': klass})
                }

                userData = userData.slice(self.startItemIndex(), self.endItemIndex());

                for (var i = 0; i < userData.length; i++) {
                    self.userData.push(userData[i]);
                }

            },
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });
    };
    // why not...
    self.getUserData();
};

function userViewModel(rootVm) {
    var self = this;
    self.rootVm = rootVm;
    var $ = jQuery;

    self.userData = ko.observable();
    self.selectedUserGroup = ko.observable();
    self.id = ko.observable();
    self.name = ko.observable();
    self.first_name = ko.observable();
    self.last_name = ko.observable();
    self.active = ko.observable();
    self.username = ko.observable();
    self.created = ko.observable();

    var UserGroup = function(name, value) {
        this.groupName = name;
        this.groupValue = value;
    };

    self.userGroups = ko.observableArray([
        new UserGroup('Admin','admin'),
        new UserGroup('User','user')
    ]);

    self.getUser = function(data) {
        $.ajax({
            type: "POST",
            url: "/api/user_by_id.json",
            data: data,
            cache: false,
            dataType: 'json',
            success: function (data, textStatus, jqXhr) {
                self.id(data.id)
                self.name(data.name);
                self.first_name(data.first_name);
                self.last_name(data.last_name);
                self.username(data.username);
                self.active(data.active);
                self.created(data.created);
            },
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });
    };

    self.setUser = function(method, id) {
        var data = $('#'+id).serialize();
        $.ajax({
            type: 'POST',
            url: method,
            data: data,
            dataType: 'json',
            success: function (data, textStatus, jqXhr) {
                self.serverResponse(data);
            },
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });
    };

    self.serverResponse = function(data) {
        $.gritter.add({
            title: data.heading,
            text: data.content,
            time: data.timeout,
            sticky: data.sticky
        });
        self.rootVm.vmUserGrid.getUserData();
        self.rootVm.selectedTemplate('user-grid');
        return true;
    }
};

