"""Demo app for the War Dragons API."""
import hashlib
import json
import time
import urllib
import webapp2

from google.appengine.api import urlfetch

# fill in your applications data here:
CLIENT_ID = '???'
CLIENT_SECRET = '???'

AUTH_SERVER = API_SERVER = 'api-dot-pgdragonsong.appspot.com'


class AuthCallback(webapp2.RequestHandler):
    """Retrieves an API token for a player.

    This API is called by the War Dragons API server when a user grants
    permission to our application.
    """
    def get(self):
        player_id = self.request.get('player_id')
        auth_code = self.request.get('auth_code')
        params = dict(auth_code=auth_code,
                      client_id=CLIENT_ID,
                      client_secret=CLIENT_SECRET)
        token_url = 'https://%s/api/dev/retrieve_token?%s' % (
            AUTH_SERVER, urllib.urlencode(params))
        resp = urlfetch.fetch(token_url, method=urlfetch.GET)
        resp_data = json.loads(resp.content)
        self.response.out.write('the API key for %s is %s (on this app)' % (
            player_id, resp_data['api_key']))


class Authorize(webapp2.RequestHandler):
    """Asks a user to authenticate with our application.

    This endpoint immediately redirects to the War Dragons API server to ask
    permission. A more sophisticated app should ask the user first, and explain
    that they will be redirected and asked to authenticate before actually
    doing so.
    """
    def get(self):
        params = dict(client_id=CLIENT_ID,
                      scopes='atlas.read,player.public.read')
        auth_url = 'https://%s/api/authorize?%s' % (
            AUTH_SERVER, urllib.urlencode(params))
        self.redirect(auth_url)


class ProxyAPIRequest(webapp2.RequestHandler):
    """Proxies an API request."""
    def get(self):
        self._proxy(urlfetch.GET)

    def post(self):
        self._proxy(urlfetch.POST)

    def _proxy(self, method):
        # an api key is required to make an API call
        api_key = self.request.headers.get('X-WarDragons-APIKey',
                                           self.request.get('apikey'))
        if not api_key:
            self.error(400)
            self.response.out.write('api key missing')
            return

        now = int(time.time())
        headers = {
            'X-WarDragons-APIKey': api_key,
            'X-WarDragons-Request-Timestamp': now
        }

        message = ':'.join([
            CLIENT_SECRET,
            api_key,
            str(now)])
        message = str(message)
        generated_signature = hashlib.sha256(message).hexdigest()

        headers['X-WarDragons-Signature'] = generated_signature

        # get the para
        url = 'https://%s%s' % (API_SERVER, self.request.path_qs)
        print url
        resp = urlfetch.fetch(url, method=method, headers=headers)
        self.response.out.write(resp.content)


app = webapp2.WSGIApplication([
    ('/auth_callback', AuthCallback),
    ('/authorize', Authorize),
    ('/.*', ProxyAPIRequest),
], debug=False)
