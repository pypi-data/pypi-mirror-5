import os
import sys
import time
import json
import requests
from struct import pack
from base64 import b64encode

import gw2api


__all__ = ("encode_item_link", "encode_coin_link", "encode_chat_link")


def mtime(path):
    """Get the modification time of a file, or -1 if the file does not exist.
    """
    if not os.path.exists(path):
        return -1
    stat = os.stat(path)
    return stat.st_mtime


def get_cached(path, cache_name=None, **kwargs):
    """Request a resource form the API, first checking if there is a cached
    response available. Returns the parsed JSON data.
    """
    if gw2api.cache_dir and gw2api.cache_time and cache_name is not False:
        if cache_name is None:
            cache_name = path
        cache_file = os.path.join(gw2api.cache_dir, cache_name)
        if mtime(cache_file) >= time.time() - gw2api.cache_time:
            with open(cache_file, "r") as fp:
                return json.load(fp)
    else:
        cache_file = None

    r = gw2api.session.get(gw2api.BASE_URL + path, **kwargs)
    r.raise_for_status()
    data = r.json()

    if cache_file:
        with open(cache_file, "w") as fp:
            json.dump(data, fp, indent=2)

    return data


def encode_item_link(item_id, number=1):
    """Encode a chat link for an item (or a stack of items).

    :param item_id: the Id of the item
    :param number: the number of items in the stack
    """
    return encode_chat_link(gw2api.TYPE_ITEM, id=item_id, number=number)


def encode_coin_link(copper, silver=0, gold=0):
    """Encode a chat link for an amount of coins.
    """
    amount = copper + silver * 100 + gold * 100 * 100
    return encode_chat_link(gw2api.TYPE_COIN, amount=amount)


def encode_chat_link(link_type, **kwargs):
    if isinstance(link_type, basestring):
        link_type = gw2api.LINK_TYPES[link_type]

    if link_type == gw2api.TYPE_COIN:
        if "copper" in kwargs or "silver" in kwargs or "gold" in kwargs:
            amount = (kwargs.get("gold", 0) * 100 * 100 +
                      kwargs.get("silver", 0) * 100 +
                      kwargs.get("copper", 0))
        else:
            amount = kwargs["amount"]
        data = pack("<BI", link_type, amount)
    elif link_type == gw2api.TYPE_ITEM:
        data = pack("<BBI", link_type, kwargs.get("number", 1), kwargs["id"])
    elif link_type in (gw2api.TYPE_TEXT, gw2api.TYPE_MAP, gw2api.TYPE_SKILL,
                       gw2api.TYPE_TRAIT, gw2api.TYPE_RECIPE):
        data = pack("<BI", link_type, kwargs["id"])
    else:
        raise Exception("Unknown link type 0x%02x" % link_type)

    return "[&%s]" % b64encode(data)
