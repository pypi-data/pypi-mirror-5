"use strict";

var util = (function(){
    function getTemplate(url, selector, callback, log){
        callback = callback || $.noop;
        log = (log === null || log === undefined) ? true : log;
        if($(selector).length < 1){
            $.ajax({
                url : url,
                dataType : "html",
                success : function(templateData){
                    $("body").append(templateData);
                    var element = $(selector);
                    if(element.length < 1 && log){
                        console.warn("Tried to get element: " + selector + " in " + url + " but was not found.");
                    }
                    callback(element);
                }
            });
        }else{
            callback($(selector));
        }
    }

    return {
        getTemplate : getTemplate
    };

})();


