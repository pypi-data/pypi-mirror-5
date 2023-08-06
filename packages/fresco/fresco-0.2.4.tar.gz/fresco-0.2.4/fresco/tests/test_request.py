from nose.tools import assert_equal

from fresco import FrescoApp

context = FrescoApp().requestcontext


class TestRequestProperties(object):

    def test_url_script_name_only(self):
        with context(SCRIPT_NAME='/foo/bar', PATH_INFO='') as c:
            assert_equal(c.request.url, "http://localhost/foo/bar")

    def test_url_script_name_path_info(self):
        with context(SCRIPT_NAME='/foo/bar', PATH_INFO='/baz') as c:
            assert_equal(c.request.url, "http://localhost/foo/bar/baz")

    def test_url_normalizes_host_port(self):
        with context(HTTP_HOST='localhost:80') as c:
            assert_equal(c.request.url, "http://localhost/")
        with context(HTTP_HOST='localhost:81') as c:
            assert_equal(c.request.url, "http://localhost:81/")

    def test_url_normalizes_host_ssl_port(self):
        with context(environ={'wsgi.url_scheme': 'https'},
                     HTTP_HOST='localhost:443') as c:
            assert_equal(c.request.url, "https://localhost/")

    def test_url_ignores_server_port_if_host_header_present(self):
        with context(environ={'wsgi.url_scheme': 'https', 'SERVER_PORT': '81'},
                     HTTP_HOST='localhost') as c:
            assert_equal(c.request.url, "https://localhost/")

    def test_as_string(self):
        with context('http://example.org/foo?bar=baz') as c:
            assert_equal(str(c.request),
                         '<Request GET http://example.org/foo?bar=baz>')

    def test_url_returns_full_url(self):
        with context('http://example.org/foo?bar=baz') as c:
            assert_equal(c.request.url, 'http://example.org/foo?bar=baz')

    def test_path_returns_correct_path_when_script_name_empty(self):
        with context(SCRIPT_NAME='', PATH_INFO='/foo/bar') as c:
            assert_equal(c.request.path, '/foo/bar')

    def test_path_returns_correct_path(self):
        with context(SCRIPT_NAME='/foo', PATH_INFO='/bar') as c:
            assert_equal(c.request.path, '/foo/bar')


class TestMakeURL(object):

    def test_returns_request_url(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.make_url(),
                         'http://localhost/script/pathinfo')

    def test_can_replace_path(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.make_url(path='/foo'),
                         'http://localhost/foo')

    def test_query_not_included_by_default(self):
        with context(QUERY_STRING='query=foo') as c:
            assert_equal(c.request.make_url(),
                         'http://localhost/')

    def test_query_dict(self):
        with context() as c:
            assert_equal(c.request.make_url(query={'a': 1, 'b': '2 3'}),
                         'http://localhost/?a=1;b=2+3')

    def test_query_kwargs(self):
        with context() as c:
            assert_equal(c.request.make_url(query={'a': 1}, b=2),
                         'http://localhost/?a=1;b=2')



class TestResolveURL(object):

    def test_relative_path(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('foo'),
                         'http://localhost/script/foo')

    def test_absolute_path_unspecified_relative(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('/foo', relative='app'),
                         'http://localhost/script/foo')

    def test_absolute_path_app_relative(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('/foo', relative='app'),
                         'http://localhost/script/foo')

    def test_absolute_path_server_relative(self):
        with context(SCRIPT_NAME='/script', PATH_INFO='/pathinfo') as c:
            assert_equal(c.request.resolve_url('/foo', relative='server'),
                         'http://localhost/foo')

    def test_ignores_server_port_if_host_header_present(self):
        with context(environ={'wsgi.url_scheme': 'https', 'SERVER_PORT': '81'},
                     HTTP_HOST='localhost') as c:
            assert_equal(c.request.resolve_url('/foo'),
                         'https://localhost/foo')


class TestCurrentRequest(object):

    def test_currentrequest_returns_current_request(self):
        from fresco import currentrequest
        with context() as c:
            assert currentrequest() is c.request

    def test_currentrequest_returns_None(self):
        from fresco import currentrequest
        assert currentrequest() is None

#def test_parsing_cookie_header():
#    @to_wsgi
#    def app(request):
#        return Response([
#            str(cookie) + '\n' for name, cookie in request.cookies.allitems()
#        ])
#
#    assert_equal(
#        TestApp(app).get(HTTP_COOKIE='$Version=1; NAME=a; $Path="/"; $Domain=".some.domain.org"; NAME=b;').body,
#        "NAME=a;Domain=.some.domain.org;Path=/;Version=1\n"
#        "NAME=b;Version=1\n",
#    )
#
#
#def test_method_not_allowed_dispatcher():
#    dispatcher = dispatcher_app()
#
#    @dispatcher.match('/blah', 'DELETE', 'PUT')
#    def app(request):
#        return Response.method_not_allowed(request)
#
#    response = TestApp(dispatcher).get('/blah')
#    assert 'not allowed' in response.body.lower()
#    assert_equal(response.status, "405 Method Not Allowed")
#    assert_equal(response.get_header('Allow'), 'PUT,DELETE')
#

#def test_request_path():
#
#    request = Request(make_environ(SCRIPT_NAME='/foo', PATH_INFO='/bar', HTTP_HOST='localhost:80'))
#    assert_equal(request.request_path, "/foo/bar")
#
#    request = Request(make_environ(SCRIPT_NAME='/foo/bar', PATH_INFO='', HTTP_HOST='localhost:80'))
#    assert_equal(request.request_path, "/foo/bar")
#
#    request = Request(make_environ(SCRIPT_NAME='/', PATH_INFO='foo/bar', HTTP_HOST='localhost:80'))
#    assert_equal(request.request_path, "/foo/bar")
#
#def test_form():
#
#    request = Request(make_environ(QUERY_STRING='foo=bar'))
#    assert_equal(request.get('foo'), u'bar')
#    assert_equal(request['foo'], u'bar')
#    assert_equal(request.get('fuz'), None)
#
#    request = Request(make_environ(QUERY_STRING='foo=bar&foo=baz'))
#    assert_equal(request.get('foo'), u'bar')
#    assert_equal(request['foo'], u'bar')
#    assert_equal(request.getlist('foo'), [u'bar', u'baz'])
#
#def test_remote_addr():
#    request = Request(make_environ(REMOTE_ADDR="1.2.3.4", HTTP_X_FORWARDED_FOR="4.3.2.1"))
#    assert request.remote_addr == "1.2.3.4"
#
#
#def test_encoding():
#
#    # Test UTF-8 decoding works (this should be the default)
#    request = Request(make_environ(QUERY_STRING=make_query(foo=u'\xa0'.encode('utf8'))))
#    assert_equal(request.get('foo'), u'\xa0')
#
#    # Force a different encoding
#    request = Request(make_environ(QUERY_STRING=make_query(foo=u'\xa0'.encode('utf7'))))
#    request.charset = 'utf-7'
#    assert_equal(request.get('foo'), u'\xa0')
#
#    # Force an incorrect encoding
#    request = Request(make_environ(QUERY_STRING=make_query(foo=u'\xa0'.encode('utf8'))))
#    request.charset = 'utf-7'
#    assert_raises(RequestParseError, request.get, 'foo')
#
#def test_form_getters():
#
#    alpha = u'\u03b1' # Greek alpha
#    beta = u'\u03b2' # Greek beta
#    gamma = u'\u03b3' # Greek gamma
#
#    request = Request(make_environ(
#        QUERY_STRING='foo=%s;foo=%s;bar=%s' % (
#            quote(alpha.encode('utf-8')),
#            quote(beta.encode('utf-8')),
#            quote(gamma.encode('utf-8'))
#        )
#    ))
#    assert request.get('foo') == request.form.get('foo') == alpha
#    assert request.getlist('foo') == request.form.getlist('foo') == [alpha, beta]
#
#    assert request.get('cheese') == request.form.get('cheese') == None
#    assert request.getlist('cheese') == request.form.getlist('cheese') == []
#
#    assert request.get('bar') == request.form.get('bar') == gamma
#    assert request.getlist('bar') == request.form.getlist('bar') == [gamma]
#
#
#def test_file_test():
#
#    filename = 'test.txt'
#    filedata = 'whoa nelly!\n'
#    content_type = 'text/plain'
#    boundary = '---------------------------1234'
#
#    post_data = (
#          '--%s\r\n' % boundary
#        + 'Content-Disposition: form-data; name="uploaded_file"; filename="%s"\r\n' % filename
#        + 'Content-Type: %s\r\n' % content_type
#        + '\r\n'
#        + filedata + '\r\n--' + boundary + '--\r\n'
#    )
#    request = Request(make_environ(
#        wsgi_input=StringIO(post_data),
#        REQUEST_METHOD='POST',
#        CONTENT_TYPE='multipart/form-data; boundary=%s' % boundary,
#        CONTENT_LENGTH=str(len(post_data)),
#    ))
#    assert_equal(request.files['uploaded_file'].filename, filename)
#    assert_equal(request.files['uploaded_file'].headers['Content-Type'], content_type)
#
#    ntf = NamedTemporaryFile()
#    request.files['uploaded_file'].save(ntf)
#    ntf.flush()
#
#    f = open(ntf.name, 'r')
#    testdata = f.read()
#    f.close()
#    ntf.close()
#    assert_equal(testdata, filedata)
#
#    ntf = NamedTemporaryFile()
#    request.files['uploaded_file'].save(ntf.name)
#
#    f = open(ntf.name, 'r')
#    testdata = f.read()
#    f.close()
#    ntf.close()
#    assert_equal(testdata, filedata)
#
