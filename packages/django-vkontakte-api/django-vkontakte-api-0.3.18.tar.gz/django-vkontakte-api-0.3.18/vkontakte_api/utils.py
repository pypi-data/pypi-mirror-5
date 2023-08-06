from django.conf import settings
from oauth_tokens.models import AccessToken, AccessTokenGettingError
from ssl import SSLError
import vkontakte
import time
import logging

__all__ = ['api_call']

log = logging.getLogger('vkontakte_api')

TIMEOUT = getattr(settings, 'VKONTAKTE_ADS_REQUEST_TIMEOUT', 1)
ACCESS_TOKEN = getattr(settings, 'VKONTAKTE_API_ACCESS_TOKEN', None)

VkontakteError = vkontakte.VKError

def get_tokens():
    '''
    Get all vkontakte tokens list
    '''
    return AccessToken.objects.filter(provider='vkontakte')

def update_token(count=1):
    '''
    Update token from provider and return it
    '''
    try:
        return AccessToken.objects.get_from_provider('vkontakte')
    except AccessTokenGettingError, e:
        if count <= 5:
            time.sleep(10)
            update_token(count+1)
        else:
            raise e

def get_api():
    '''
    Return API instance with latest token from database
    '''
    if ACCESS_TOKEN:
        token = ACCESS_TOKEN
    else:
        tokens = get_tokens()
        if not tokens:
            update_token()
            tokens = get_tokens()
        token = tokens[0].access_token
    return vkontakte.API(token=token)

def api_call(method, **kwargs):
    '''
    Call API using access_token
    '''
    vk = get_api()
    try:
        response = vk.get(method, timeout=TIMEOUT, **kwargs)
    except VkontakteError, e:
        if e.code == 5:
            log.debug("Updating vkontakte access token")
            update_token()
            ACCESS_TOKEN = None
            vk = get_api()
            response = vk.get(method, timeout=TIMEOUT, **kwargs)
        elif e.code == 6:
            log.warning("Vkontakte error: '%s'" % (e.description))
            time.sleep(10)
            response = api_call(method, **kwargs)
        elif e.code == 9:
            log.warning("Vkontakte flood control registered while executing method %s with params %s" % (method, kwargs))
            time.sleep(1)
            response = api_call(method, **kwargs)
        else:
            log.error("Unhandled vkontakte error raised: %s", e)
            raise e
    except SSLError, e:
        log.error("SSLError: '%s' registered while executing method %s with params %s" % (e, method, kwargs))
        time.sleep(1)
        response = api_call(method, **kwargs)
    except Exception, e:
        log.error("Unhandled error: %s registered while executing method %s with params %s" % (e, method, kwargs))
        raise e

    return response