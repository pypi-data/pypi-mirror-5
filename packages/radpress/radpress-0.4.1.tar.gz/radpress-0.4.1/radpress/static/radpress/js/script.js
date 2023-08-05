/* Dear contributor, this code snippet is required to resize pre tag for
 * article div width. If you have a better idea about using horizontal
 * scrolling in pre, please fork radpress repository from github, and send me
 * pull request with your changes. thanks.
 */

// place any jQuery/helper plugins in here, instead of separate, slower script files.
var getParams = function() {
    var params = window.location.href.split('?')[1];
    if (typeof(params) === 'undefined') {
        return {};
    }

    params = params.split('&');
    var paramsObj = {};
    var item;

    $.each(params, function(key, value) {
        item = value.split('=');
        paramsObj[item[0]] = item[1];
    });

    return paramsObj;
};

var getParam = function(key) {
    var value;
    try {
        value = window.RADPESS_PARAMS[key];
        value = decodeURIComponent(value).replace(/\+/g, ' ');
    } catch(e) {
        value = null;
    }

    return value;
};

// Global Variables
window.RADPESS_PARAMS = getParams();

// Highlight table fixings
var alwaysCalculateHighlightTableWidth;
var postContentDiv;
if ($('body').hasClass('zen-mode')) {
    postContentDiv = $('#zen-preview').find('.content-space');
    alwaysCalculateHighlightTableWidth = true;
} else {
    postContentDiv = $('.post-content');
    alwaysCalculateHighlightTableWidth = false;
}

if (alwaysCalculateHighlightTableWidth || postContentDiv.length) {
    var preWidth;
    var spaces;

    $(window).on('load resize', function() {
        spaces = parseInt(postContentDiv.css('padding-left').split('px')[0])
            + parseInt(postContentDiv.css('padding-right').split('px')[0])
            + $('td.linenos').width() + 2;
        preWidth = postContentDiv.width() - spaces;
        $('td.code pre').css('width', preWidth);
    });
}

var searchForm = $('.search-form');
if (searchForm.length) {
    var qName = 'q';
    var q = getParam(qName);

    if (q != '' && q != 'undefined') {
        searchForm.find('input[name="' + qName + '"]').val(q);
    }
}

var shareUrls = $('.meta-info .share a');
if (shareUrls.length) {
    shareUrls.on('click', function() {
        window.open(
            $(this).attr('href'),
            $(this).text(),
            'width=450,height=300,left=' + (screen.availWidth / 2 - 375) + ',top=' + (screen.availHeight / 2 - 150) + '');
        return false;
    });
}
