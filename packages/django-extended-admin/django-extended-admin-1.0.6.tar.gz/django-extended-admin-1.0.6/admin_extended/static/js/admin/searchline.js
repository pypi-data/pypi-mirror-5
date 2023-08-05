// Contains now is case insensetive
$.extend(
    $.expr[':'].iContains = function(a, i, m) {
        return $(a).text().toUpperCase().indexOf(m[3].toUpperCase())>=0;
    }
);

$.fn.addSearchLine = function(options) {
    return new FilteredCheckboxes(this, options);
}

function FilteredCheckboxes(controller, options) {
    $.extend(this, {
        label: "Search",
        notFound: "No match found",
        matchCase: false,
        attachMethod: "prependTo",
        attachSelector: null
    }, options)
    this.controller = controller;
    this.init();
}

FilteredCheckboxes.prototype.init = function() {
    var self = this;

    var place = this.attachSelector ? this.controller.find(this.attachSelector) : this.controller;
    var div = $("<div/>", {class: "searchContainer"})[this.attachMethod](place);
    var choices = this.controller.find("ul li label");
    var input = $("<input/>", {class: "search-line vTextField"}).appendTo(div);

    input.keyup(function() {
        var notFound = div.find(".not-found");

        if ($(this).val()) {
            var caseFilter = self.matchCase ? ":contains({0})" : ":iContains({0})";
            var contains = choices.filter(caseFilter.format($(this).val()));
            
            contains.length ? notFound.hide() : notFound.show();
            contains.show();
            choices.not(contains).hide();
        }
        else {
            choices.show();
            notFound.hide();
        }
    })

    $("<span/>", {text: self.label + " ", class: "search-label"}).prependTo(div);
    $("<span/>", {class: "deletelink"}).appendTo(div).click(function() {
        input.val("");
        input.trigger("keyup");
    })
    $("<div/>", {text: this.notFound, class: "not-found"}).appendTo(div).hide();
}
