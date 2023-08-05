(function($) {

var isUndefinedOrNull = function(o) {
    if (!(typeof(o) == 'undefined' || o === null)) {
        return false;
    }
    return true;
};

var declare = function(namespace) {
    var obj = window;
    $.each(namespace.split('.'), function(i, name) {
        if (isUndefinedOrNull(obj[name])) {
            obj[name] = {};
        }
        obj = obj[name];
    });
};

declare('namespace');
namespace.declare = declare;
namespace.isUndefinedOrNull = isUndefinedOrNull;

})(jQuery);
