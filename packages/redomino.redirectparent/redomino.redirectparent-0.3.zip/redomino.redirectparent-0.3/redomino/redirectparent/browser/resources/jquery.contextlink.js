(function ($){

/*

contextlink 

add the current url or another string as a parameter of another url
example:

link:
   http://www.example.com
in site:
   http://www.mysite.com
become:
   http://www.example.com?relatesto=http%3A%2F%2Fwww.mysite.com

querypar -> name of the parameter to pass
query -> string to add to the URL (if undefined it uses the current URL)

*/

$._addUrlToLink = function (href, here, querypar){
    var here_encoded = encodeURIComponent(here),
        here_path = window.location.protocol + '//' + window.host + window.pathname,
        url = href.match(/[^?#]*/)[0],
        queries = href.match(/\?[^#]*/),
        query = queries && queries[0],
        hashes = href.match(/#.*$/),
        hash = hashes && hashes[0];

    if (url === '' || url === here_path){
        return href;
    }

    href = url;
    if (query){
        href += query + '&' + querypar + "=" + here_encoded;
    }
    else{
        href += "?" + querypar + "=" + here_encoded;
    }
    if (hash){
        href += hash;
    }
    return href;
};


$.fn.contextlink = function (querypar, query){
    querypar = querypar || 'relatesto';
    query = query || window.location.toString();
    this.find('a').each(function (){
        var $this = $(this),
            href = $(this).attr('href'),
            newurl = $._addUrlToLink(href, query, querypar);
        $this.attr('href', newurl);
    });

    return this;
};

}(jQuery));
