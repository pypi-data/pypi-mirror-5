# -*- coding: utf-8 -*-
import json
import base64
import logging

import requests
from zope.interface import implementer
from zope.interface import Attribute, Interface

log = logging.getLogger(__name__)


def includeme(config):
    log.debug('Including pyramid_mixpanel')
    config.registry.registerUtility(MixpanelUtility(config.registry.settings))
    config.commit()


def get_mixpanel_utility(request):
    """Retrieve mixpanel utility from the registry."""
    return request.registry.getUtility(IMixpanelUtility)


class IMixpanelUtility(Interface):
    """Utility to track events & people on Mixpanel service."""

    token = Attribute("""Mixpanel token""")

    def track(event, properties):
        """Track an event and its properties."""

    def people_track(distinct_id, properties):
        """Track a user with properties."""


@implementer(IMixpanelUtility)
class MixpanelUtility(object):

    def __init__(self, settings):
        self.token = settings['mixpanel.token']

    def track(self, event, properties):
        """Logging to the mixpanel.com API.

        @param event: event/category to log this data under
        @param properties: dictionary of key-value pairs that describe event
        See http://mixpanel.com/api/

        Only accepts datatypes that a default JSON encoder can encode, i.e.,
        datetime and Decimal objects needs to be converted to string format
        by the client.
        """
        url = "https://api.mixpanel.com/track"
        if u'token' not in properties:
            properties[u'token'] = self.token

        try:
            params = {'event': event, 'properties': properties}
            data = base64.b64encode(json.dumps(params))
            # TODO POST is also accepted and better HTTP, use it
            response = requests.get(url, params={'data': data})
            response.raise_for_status()
        except Exception:
            log.exception('mixpanel track event exception: event %s; properties: %s',
                          event, properties)

    def people_track(self, distinct_id, properties):
        """Create or update user in Mixpanel People.

        *distinct_id* must be a string and *properties* a dictionary.
        See Mixpanel People documentation for info about special keys.

        The same function is used to create the user, update the last
        login and update the transaction information, because we can't
        know for sure when an update can be done instead of a create,
        so we always send all the information.  This has the side
        effect of possibly updating info that have been refreshed with
        real-time update.
        """
        try:
            data = base64.b64encode(json.dumps({
                u'$token': self.token,
                u'$distinct_id': distinct_id,
                u'$set': properties,
            }))

            response = requests.post('https://api.mixpanel.com/engage/',
                                     {'data': data})
            response.raise_for_status()
        except Exception:
            log.exception('mixpanel people tracking error')
            return

        result = response.content  # '1' means OK
        if result == '0':
            log.error('mixpanel people tracking returned error status')
        elif result != '1':
            log.warning('unknown status returned by mixpanel people '
                        'tracking: %r', result)
