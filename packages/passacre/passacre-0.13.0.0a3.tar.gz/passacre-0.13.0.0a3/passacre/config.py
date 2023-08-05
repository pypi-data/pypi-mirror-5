# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

from __future__ import unicode_literals

from passacre.multibase import MultiBase

import string
import yaml

default_digits = {
    'printable': string.digits + string.ascii_letters + string.punctuation,
    'alphanumeric': string.digits + string.ascii_letters,
    'digit': string.digits,
    'letter': string.ascii_letters,
    'lowercase': string.ascii_lowercase,
    'uppercase': string.ascii_uppercase,
}

def multibase_of_schema(schema):
    "Convert a password schema from decoded YAML to a ``MultiBase``."
    ret = []
    for item in schema:
        count = 1
        if isinstance(item, list) and isinstance(item[0], int):
            count, item = item
        if not isinstance(item, list):
            item = [item]
        item = ''.join(default_digits.get(i, i) for i in item)
        ret.extend([item] * count)
    return MultiBase(ret)

def load(infile):
    "Load site configuration from a YAML file object."
    parsed = yaml.load(infile)
    defaults = parsed['sites'].get('default', {})
    defaults.setdefault('method', 'keccak')
    defaults.setdefault('iterations', 1000)

    sites = {}
    for site, additional_config in parsed['sites'].items():
        site_config = sites[site] = defaults.copy()
        site_config.update(additional_config)
        site_config['multibase'] = multibase_of_schema(site_config['schema'])
        site_config['iterations'] = (
            site_config.get('iterations', 1000) + site_config.get('increment', 0))

    site_hashing = sites['--site-hashing'] = defaults.copy()
    site_hashing.update(parsed.get('site-hashing', {}))
    site_hashing.setdefault('enabled', True)

    return sites
