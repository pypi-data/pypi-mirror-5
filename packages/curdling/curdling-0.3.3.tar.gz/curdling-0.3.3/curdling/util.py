from __future__ import absolute_import, print_function, unicode_literals
from distlib import compat, util

import io
import os
import re
import hashlib
import logging
import subprocess
import urllib3


INCLUDE_PATTERN = re.compile(r'-r\s*\b([^\b]+)')

LINK_PATTERN = re.compile(r'^([^\:]+):\/\/.+')

ROOT_LOGGER = logging.getLogger('curdling')


class Requirement(object):
    name = None


def is_url(requirement):
    return ':' in requirement


def safe_name(requirement):
    if is_url(requirement):
        return requirement
    safe = requirement.lower().replace('_', '-')
    return safe_requirement(safe)


def safe_requirement(requirement):
    return (util.parse_requirement(requirement).requirement
            .replace('== ', '')
            .replace('==', ''))


def parse_requirement(spec):
    if not is_url(spec):
        requirement = util.parse_requirement(spec)
        requirement.name = safe_name(requirement.name)
        requirement.requirement = safe_requirement(spec)
        requirement.is_link = False
    else:
        requirement = Requirement()
        requirement.name = spec
        requirement.requirement = spec
        requirement.constraints = ()
        requirement.is_link = True
    return requirement


def split_name(fname):
    name, ext = os.path.splitext(fname)

    try:
        ext, frag = ext.split('#')
    except ValueError:
        frag = ''
    return name, ext[1:], frag


def expand_requirements(file_name):
    requirements = []

    for req in io.open(file_name).read().splitlines():
        req = req.split('#', 1)[0].strip()
        if not req:
            continue

        # Handling special lines that start with `-r`, so we can have files
        # including other files.
        include = INCLUDE_PATTERN.findall(req)
        if include:
            requirements.extend(expand_requirements(include[0]))
            continue

        # Finally, we're sure that it's just a package description
        requirements.append(safe_name(req))
    return requirements


def filehash(f, algo, block_size=2**20):
    algo = getattr(hashlib, algo)()
    while True:
        data = f.read(block_size)
        if not data:
            break
        algo.update(data)
    return algo.hexdigest()


def spaces(count, text):
    return '\n'.join('{0}{1}'.format(' ' * count, line)
        for line in text.splitlines())


def get_auth_info_from_url(url):
    parsed = compat.urlparse(url)
    if parsed.username:
        auth = '{0}:{1}'.format(parsed.username, parsed.password)
        return urllib3.util.make_headers(basic_auth=auth)
    return {}


def execute_command(name, *args, **kwargs):
    command = subprocess.Popen((name,) + args,
        stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        **kwargs)
    _, errors = command.communicate()
    if command.returncode != 0:
        raise Exception(errors)


def logger(name):
    logger_instance = logging.getLogger(name)
    logger_instance.parent = ROOT_LOGGER
    return logger_instance
