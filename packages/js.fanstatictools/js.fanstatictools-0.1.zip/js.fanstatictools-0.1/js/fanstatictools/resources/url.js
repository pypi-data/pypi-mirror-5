(function($) {

namespace.declare('fanstatictools');

fanstatictools.get_library_url = function(name) {
    // Return url to fanstatic library.
    var url;
    $('script').each(function(i, tag) {
        var src = $(tag).attr('src');
        if (namespace.isUndefinedOrNull(src)) {
            return true;  //continue
        }
        src = src.split('/');
        var index = src.indexOf(name);
        if (index == -1) {
            return true;  // continue
        }
        while (index < src.length) {
            index += 1;
            if (src[index].indexOf(':') == -1 ||
                src[index].indexOf(':bundle:') === 0) {
                url = src.slice(0, index).join('/');
                return false;  // break
            }
        }
        return true;
    });
    return url + '/';
};

})(jQuery);
