//module("Test contextlink");



test('checking simple link', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx',
                              'http://www.mysite.com/page',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?rel=http%3A%2F%2Fwww.mysite.com%2Fpage', 'url is ok');
});

test('checking query string link 1', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx',
                              'http://www.mysite.com/page?hello',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?rel=http%3A%2F%2Fwww.mysite.com%2Fpage%3Fhello', 'url is ok');
});

test('checking query string link 2', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx?hello',
                              'http://www.mysite.com/page',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?hello&rel=http%3A%2F%2Fwww.mysite.com%2Fpage', 'url is ok');
});

test('checking query string link 3', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx?hello',
                              'http://www.mysite.com/page?hello2',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?hello&rel=http%3A%2F%2Fwww.mysite.com%2Fpage%3Fhello2', 'url is ok');
});

test('checking query string link and hash 1', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx?hello#xyz',
                              'http://www.mysite.com/page?hello2',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?hello&rel=http%3A%2F%2Fwww.mysite.com%2Fpage%3Fhello2#xyz', 'url is ok');
});
test('checking query string link and hash 2', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx?hello',
                              'http://www.mysite.com/page?hello2#123',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?hello&rel=http%3A%2F%2Fwww.mysite.com%2Fpage%3Fhello2%23123', 'url is ok');
});

test('checking query string link and hash 2', function (){
    var url = $._addUrlToLink('http://www.mysite.com/page/xxx?hello#xyz',
                              'http://www.mysite.com/page?hello2#123',
                              'rel');
    ok(url === 'http://www.mysite.com/page/xxx?hello&rel=http%3A%2F%2Fwww.mysite.com%2Fpage%3Fhello2%23123#xyz', 'url is ok');
});


test('checking relative path', function (){
    var url = $._addUrlToLink('/xxx?hello#xyz',
                              'http://www.mysite.com/page?hello2#123',
                              'rel');
    ok(url === '/xxx?hello&rel=http%3A%2F%2Fwww.mysite.com%2Fpage%3Fhello2%23123#xyz', 'url is ok');
});

test('checking same path', function (){
    var url = $._addUrlToLink('?hello#xyz',
                              'http://www.mysite.com/page?hello2#123',
                              'rel');
    console.log(url);
    ok(url === '?hello#xyz', 'url is ok');
});

