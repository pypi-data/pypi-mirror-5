from urllib  import quote
from socket  import timeout
from ssl     import SSLError

from cloudfiles import consts
from cloudfiles.storage_object import Object
from cloudfiles.errors  import ResponseError

from ftpcloudfs.utils import smart_str

class ChunkObject(Object):
    def prepare_chunk(self):
        self.size = None
        self._name_check()

        # This method implicitly disables verification
        if not self._etag_override:
            self._etag = None

        if not self.content_type:
            self.content_type = 'application/octet-stream'

        path = "/%s/%s/%s" % (self.container.conn.uri.rstrip('/'),
                              quote(smart_str(self.container.name)),
                              quote(smart_str(self.name)),
                              )
        headers = self._make_headers()
        if self.size is None:
            del headers['Content-Length']
            headers['Transfer-Encoding'] = 'chunked'
        headers['X-Auth-Token'] = self.container.conn.token
        headers['User-Agent'] = consts.user_agent
        if self.container.conn.real_ip:
            headers['X-Forwarded-For'] = self.container.conn.real_ip
        self.chunkable_http = self.container.conn.connection
        self.chunkable_http.putrequest('PUT', path)
        for key, value in headers.iteritems():
            self.chunkable_http.putheader(key, value)
        self.chunkable_http.endheaders()

    def send_chunk(self, chunk):
        try:
            self.chunkable_http.send("%X\r\n" % len(chunk))
            self.chunkable_http.send(chunk)
            self.chunkable_http.send("\r\n")
        except (timeout, SSLError), err:
            raise ResponseError(408, err.message)

    def finish_chunk(self):
        try:
            self.chunkable_http.send("0\r\n\r\n")
            response = self.chunkable_http.getresponse()
        except (timeout, SSLError), err:
            raise ResponseError(408, err.message)

        try:
            response.read()
        except (timeout, SSLError):
            # this is not relevant, keep going
            pass

        if (response.status < 200) or (response.status > 299):
            raise ResponseError(response.status, response.reason)

        for hdr in response.getheaders():
            if hdr[0].lower() == 'etag':
                self._etag = hdr[1]

