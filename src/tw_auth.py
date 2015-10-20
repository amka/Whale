# coding: utf-8
import json
import webbrowser

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urllib import urlopen


__author__ = 'meamka'


# Twitch.tv OAuth Data
TWITCH_CLIENT_ID = '3mgta7s961ldrhjpn8n378msvitpxi3'
TWITCH_CLIENT_SECRET = 'dmv083mhgzmlwk8jrlxlpm7qxizeczw'
TWITCH_REDIRECT_URI = 'http://localhost:8989/'


def get_access_token_from_url(url):
    """
    Parse the access token from Facebook's response
    Args:
        uri: the facebook graph api oauth URI containing valid client_id,
             redirect_uri, client_secret, and auth_code arguements
    Returns:
        a string containing the access key
    """
    token_response = str(urlopen(url, data='').read())
    try:
        return json.loads(token_response)
    except Exception:
        return None


class TwitchHTTPResponseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # self.wfile.write("<html><head><title>Title goes here.</title></head>")
        # self.wfile.write("<body><p>This is a test.</p>")
        # # If someone went to "http://something.somewhere.net/foo/bar/",
        # # then self.path equals "/foo/bar/".
        # self.wfile.write("<p>You accessed path: %self</p>" % self.path)
        # self.wfile.write("</body></html>")

        TWITCH_API_AUTH_URI = 'https://api.twitch.tv/kraken/oauth2/token?' \
                              'grant_type=authorization_code' \
                              '&client_id={client_id}' \
                              '&client_secret={client_secret}' \
                              '&redirect_uri={redirect_url}' \
                              '&code='.format(
            client_id=TWITCH_CLIENT_ID,
            client_secret=TWITCH_CLIENT_SECRET,
            redirect_url=TWITCH_REDIRECT_URI,
        )

        if 'code' in self.path:
            self.auth_code = self.path.split('=')[1]
            print 'Got OAuth code: ', self.auth_code
            # Display to the user that they no longer need the browser window
            self.wfile.write('<html><h1>You may now close this window. </h1></html>')

            print 'Token URL: ', TWITCH_API_AUTH_URI + self.auth_code

            access_token = get_access_token_from_url(TWITCH_API_AUTH_URI + self.auth_code)
            self.server.access_token = access_token


class TokenHandler(object):
    def get_access_token(self, callback):
        """
         Fetches the access key using an HTTP server to handle oAuth
         requests
            Args:
                appId:      The Facebook assigned App ID
                appSecret:  The Facebook assigned App Secret
        """

        ACCESS_URI = 'https://api.twitch.tv/kraken/oauth2/authorize?' \
                     'response_type=code' \
                     '&client_id={client_id}' \
                     '&redirect_uri={redirect_url}' \
                     '&scope={scope}'.format(
            client_id=TWITCH_CLIENT_ID,
            redirect_url=TWITCH_REDIRECT_URI,
            scope='+'.join(['user_read', 'user_subscriptions'])
        )

        access_token = None
        error = None

        webbrowser.open(ACCESS_URI)
        httpServer = HTTPServer(('localhost', 8989), TwitchHTTPResponseHandler)
        # This function will block until it receives a request
        httpServer.handle_request()
        #Return the access token
        access_token_response = httpServer.access_token
        if isinstance(access_token_response, dict) and 'access_token' in access_token_response:
            access_token = access_token_response.get('access_token')
        else:
            error = access_token_response.get('error')

        callback(access_token, error)