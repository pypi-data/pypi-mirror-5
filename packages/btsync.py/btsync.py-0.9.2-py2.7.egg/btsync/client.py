import requests
import time
import json
import urllib


def _current_timestamp():
    return int(time.time() * 1000)


def _make_action_method(action_name, key=None):
    def getter(self):
        response = self._make_request(
            params={'action': action_name})

        result = json.loads(response.text)
        if key is None:
            return result
        else:
            return result[key]

    return getter


class BtsyncException(StandardError):
    def __init__(self, error):
        self.error = error
        self.code = error['error']
        self.message = error['message']

    def __str__(self):
        return self.message


class Client(object):
    def __init__(self, **kwargs):
        self._host = kwargs.pop('host', '127.0.0.1')
        self._port = kwargs.pop('port', '8888')
        self._username = kwargs.pop('username', 'admin')
        self._password = kwargs.pop('password', 'password')
        self._session = self._authenticate()

    def _make_request(self, **kwargs):
        endpoint = kwargs.pop('endpoint', '')
        params = kwargs.pop('params', {})
        with_token = kwargs.pop('with_token', True)
        method = kwargs.pop('method', 'get')
        session = kwargs.pop('session', None)

        params['t'] = _current_timestamp()
        if with_token:
            params['token'] = self._token

        url = 'http://{host}:{port}/gui/{endpoint}?{qs}'.format(
            host=self._host,
            port=self._port,
            endpoint=endpoint,
            qs=urllib.urlencode(params),
        )

        method = getattr(
            session if session is not None else self._session, method)
        assert method is not None, 'Invalid method: %s' % method

        response = method(url)
        response.raise_for_status()
        return response

    def _get_token(self, session):
        response = self._make_request(
            endpoint='token.html', method='post',
            session=session, with_token=False)
        return (
            response.text
            .split("<html><div id='token' style='display:none;'>")[1]
            .split("</div></html>")[0]
        )

    def _authenticate(self):
        session = requests.Session()
        session.auth = (self._username, self._password)
        self._token = self._get_token(session)
        return session

    os_type = property(_make_action_method('getostype', key='os'))

    version = property(_make_action_method('getversion', key='version'))

    new_version = property(
        _make_action_method('checknewversion', key='version'))

    sync_folders = property(
        _make_action_method('getsyncfolders', key='folders'))

    generate_secret = _make_action_method('generatesecret')

    def add_sync_folder(self, name, secret, force=False):
        params = {'action': 'addsyncfolder',
                  'name': name,
                  'secret': secret}
        if force:
            params['force'] = 1

        response = self._make_request(params=params)
        result = json.loads(response.text)
        if result['error']:
            raise BtsyncException(result)

    def remove_sync_folder(self, name, secret):
        self._make_request(params={
            'action': 'removefolder',
            'name': name,
            'secret': secret,
        })

    settings = property(_make_action_method('getsettings', key='settings'))

    def set_settings(self, **settings):
        params = {
            'action': 'setsettings',
        }
        params.update(settings)
        self._make_request(params=params)

    def get_folder_preference(self, name, secret):
        response = self._make_request(params={
            'action': 'getfolderpref',
            'name': name,
            'secret': secret,
        })
        return json.loads(response.text)['folderpref']

    def set_folder_preference(self, name, secret, **prefs):
        params = {
            'action': 'setfolderpref',
            'name': name,
            'secret': secret,
        }
        params.update(prefs)
        self._make_request(params=params)

    def update_secret(self, name, secret, new_secret):
        self._make_request(params={
            'action': 'updatesecret',
            'name': name,
            'secret': secret,
            'newsecret': new_secret,
        })

    def generate_invite(self, name, secret, readonly=False):
        invite_action = (
            'generateinvite' if not readonly else 'generateroinvite')
        response = self._make_request(params={
            'action': invite_action,
            'name': name,
            'secret': secret,
        })
        return json.loads(response.text)['invite']

    username = property(_make_action_method('getusername', key='username'))
