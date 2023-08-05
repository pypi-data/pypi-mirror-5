# -*- coding: utf-8 -*-

from libthumbor import CryptoURL
from django_thumbor import conf
from django.conf import settings


crypto = CryptoURL(key=conf.THUMBOR_SECURITY_KEY)


def _remove_prefix(url, prefix):
    if url.startswith(prefix):
        return url[len(prefix):]
    return url


def _remove_schema(url):
    return _remove_prefix(url, 'http://')


def _prepend_media_url(url):
    if url.startswith(settings.MEDIA_URL):
        url = _remove_prefix(url, settings.MEDIA_URL)
        url.lstrip('/')
        return '%s/%s' % (conf.THUMBOR_MEDIA_URL, url)
    return url


def generate_url(image_url, **kwargs):
    image_url = _prepend_media_url(image_url)
    image_url = _remove_schema(image_url)

    kwargs = dict(conf.THUMBOR_ARGUMENTS, **kwargs)
    encrypted_url = crypto.generate(image_url=image_url, **kwargs).strip('/')

    return '%s/%s' % (conf.THUMBOR_SERVER, encrypted_url)
