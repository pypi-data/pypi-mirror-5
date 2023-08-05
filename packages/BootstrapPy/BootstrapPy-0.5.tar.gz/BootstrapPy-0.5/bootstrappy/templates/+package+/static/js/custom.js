/*
 * BootstrapPy:
 * Custom JavaScript
 *
 * */

function nextUserGridPage() {
    bootstrapPyVm.vmUserGrid.pageNext();
}

function prevUserGridPage() {
    bootstrapPyVm.vmUserGrid.pagePrev();
}

function updateUserActive(data, event) {
    bootstrapPyVm.vmUserGrid.setActive(data);
}

function getUserEdit(data) {
    bootstrapPyVm.loadTemplate('user-edit');
    bootstrapPyVm.vmUser.getUser(data);
}

$(document).ready(function() {
    bootstrapPyVm = new BootstrapPyViewModel();
    bootstrapPyVm.loadTemplate('user-grid');
    ko.applyBindings(bootstrapPyVm, document.getElementById('main'));
});


