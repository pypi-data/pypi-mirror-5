"""Utilities for extracting keyword information from search engine
referrers."""
import os
import re
import logging
from collections import OrderedDict
from operator import itemgetter
import itertools
from urllib2 import urlopen
from subprocess import Popen, PIPE, STDOUT
from pprint import pprint
from urlparse import urlparse, parse_qs, ParseResult
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except ImportError:
    import json

from iso3166 import countries


__all__ = ('get_parser', 'is_serp', 'extract', 'get_all_query_params')

log = logging.getLogger('serpextract')

_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)), *paths)
# uk is not an official ISO-3166 country code, but it's used in top-level
# domains so we add it to our list see
# http://en.wikipedia.org/wiki/ISO_3166-1 for more information
_country_codes = [country.alpha2.lower() for country in countries] + ['uk']


def _to_unicode(s):
    """Safely convert s to a unicode"""
    return s if isinstance(s, unicode) else s.decode("utf-8", "ignore")


class ExtractResult(object):
    'ExtractResult(engine_name, keyword, parser)'
    __slots__ = ('engine_name', 'keyword', 'parser')

    def __init__(self, engine_name, keyword, parser):
        self.engine_name = engine_name
        self.keyword = keyword
        self.parser = parser

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'ExtractResult(engine_name={!r}, keyword={!r}, parser={!r})'\
               .format(self.engine_name, self.keyword, self.parser)


class SearchEngineParser(object):
    """A search engine parser which is mapped to a single line in Piwik's
    list of search engines
    https://raw.github.com/piwik/piwik/master/core/DataFiles/SearchEngines.php

    This class is not used directly since it already assumes you know the
    exact search engine you want to use to parse a URL.  The main interface
    for users of this module is the get_keyword method.
    """

    # Since we instantiate many of these objects, we try to save on memory
    __slots__ = ('engine_name', 'keyword_extractor', 'link_macro', 'charsets')

    def __init__(self, engine_name, keyword_extractor, link_macro, charsets):
        """New instance of a SearchEngineParser
        :param engine_name: the friendly name of the engine (e.g. 'google')
        :param keyword_extractor: a string or list of keyword extraction methods
                                  for this search engine.  If a single string,
                                  we assume we're extracting a query string
                                  param, if it's a string that starts with '/'
                                  then we extract from the path instead of
                                  query string
        :param link_macro: a string indicating how to build a link to the
                           search engine results page for a given keyword
        :param charsets: a string or list of charsets to use to decode the
                         keyword
        """
        self.engine_name = engine_name
        if isinstance(keyword_extractor, basestring):
            keyword_extractor = [keyword_extractor]
        self.keyword_extractor = keyword_extractor
        self.link_macro = link_macro
        if isinstance(charsets, basestring):
            charsets = [charsets]
        self.charsets = [c.lower() for c in charsets]

    def get_serp_url(self, base_url, keyword):
        """Get a URL to the search engine results page (SERP)
        for a given keyword.
        :param base_url: string of format '<scheme>://<netloc>'
        :param keyword: the search keyword
        """
        if self.link_macro is None:
            return None

        link = u'{}/{}'.format(base_url, self.link_macro.format(k=keyword))
        #link = self.decode_string(link)
        return link


    def parse(self, serp_url):
        """Parse a SERP URL to extract the search keyword.

        :param serp_url: either a string or a ParseResult
        :returns: a dict containing engine_name, keyword
        """
        if isinstance(serp_url, basestring):
            try:
                url_parts = urlparse(serp_url)
            except:
                return # Malformed URLs
        else:
            url_parts = serp_url
        query = parse_qs(url_parts.query, keep_blank_values=True)

        keyword = None
        for extractor in self.keyword_extractor:
            if extractor.startswith('/'):
                # Regular expression extractor
                extractor = extractor.strip('/')
                regex = re.compile(extractor)
                match = regex.search(url_parts.path)
                if match:
                    keyword = match.group(1)
                    break
            else:
                if extractor in query:
                    keyword = query[extractor][0]
                    break

        if keyword is None:
            return

        keyword = _to_unicode(keyword)

        return ExtractResult(self.engine_name, keyword, self)

    def __repr__(self):
        return """SearchEngineParser(engine_name={!r},\
 keyword_extractor={!r}, link_macro={!r}, charsets={!r})"""\
        .format(self.engine_name, self.keyword_extractor, self.link_macro,
                self.charsets)


_piwik_engines = None
def _get_piwik_engines(fresh=False):
    """Return the search engine dict specified by the Piwik team:
    https://raw.github.com/piwik/piwik/master/core/DataFiles/SearchEngines.php

    :param fresh: force a cache refresh of engines
    """
    global _piwik_engines
    # TODO: Regex this instead of pipeing it through php which is a horrible
    # dependency for a Python module
    filename = _here('search_engines.pickle')

    if not os.path.exists(filename) or fresh:
        log.info('Grabbing fresh Piwik search engine list (requires PHP).')
        url = urlopen('https://raw.github.com/piwik/piwik/master/core/DataFiles/SearchEngines.php')
        php_script = url.readlines()
        php_script.append('echo(json_encode($GLOBALS["Piwik_SearchEngines"]));\n')
        php_script = ''.join(php_script)
        process = Popen(['php'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        json_string = process.communicate(input=php_script)[0]
        # Ordering of the dictionary from PHP matters so we keep it
        # in an OrderedDict
        _piwik_engines = json.loads(json_string, object_pairs_hook=OrderedDict)
        log.info('Loaded %s Piwik search engines, updating local cache (%s).',
                 len(_piwik_engines), filename)
        with open(filename, 'w') as file_:
            pickle.dump(_piwik_engines, file_)
    else:
        with open(filename, 'r') as file_:
            _piwik_engines = pickle.load(file_)

    return _piwik_engines


def _get_lossy_domain(domain):
    """A lossy version of a domain/host to use as lookup in the _engines dict."""
    domain = unicode(domain)
    codes = '|'.join(_country_codes)
    domain = re.sub(r'^(\w+[0-9]*|search)\.', '', domain)
    domain = re.sub(r'(^|\.)m\.', r'\1', domain)
    domain = re.sub(r'(\.(com|org|net|co|it|edu))?\.({})(\/|$)'.format(codes), r'.{}\4', domain)
    domain = re.sub(r'(^|\.)({})\.'.format(codes), r'\1{}.', domain)

    return domain


_engines = None
def _get_search_engines():
    """Convert the OrderedDict of search engine parsers that we get from Piwik
    to a dictionary of SearchEngineParser objects.
    Cache this thing by storing in the global ``_engines``.
    """
    global _engines
    if _engines:
        return _engines

    piwik_engines = _get_piwik_engines()
    # Engine names are the first param of each of the search engine arrays
    # so we group by those guys, and create our new dictionary with that
    # order
    key_func = lambda x: x[1][0]
    grouped = itertools.groupby(piwik_engines.iteritems(), key_func)
    _params = []
    _engines = {}

    for engine_name, rule_group in grouped:
        defaults = {
            'extractor': None,
            'link_macro': None,
            'charsets': ['utf-8']
        }

        for i, rule in enumerate(rule_group):
            domain = rule[0]
            rule = rule[1][1:]
            if i == 0:
                defaults['extractor'] = rule[0]
                if len(rule) >= 2:
                    defaults['link_macro'] = rule[1]
                if len(rule) >= 3:
                    defaults['charsets'] = rule[2]

                _engines[domain] = SearchEngineParser(engine_name,
                                                      defaults['extractor'],
                                                      defaults['link_macro'],
                                                      defaults['charsets'])
                continue

            # Default args for SearchEngineParser
            args = [engine_name, defaults['extractor'],
                    defaults['link_macro'], defaults['charsets']]
            if len(rule) >= 1:
                args[1] = rule[0]

            if len(rule) >= 2:
                args[2] = rule[1]

            if len(rule) == 3:
                args[3] = rule[2]

            _engines[domain] = SearchEngineParser(*args)

    return _engines


def get_all_query_params():
    """Return all the possible query string params for all search engines."""
    engines = _get_search_engines()
    all_params = set()
    for _, parser in engines.iteritems():
        # Find non-regex params
        params = set(filter(lambda x: not x.startswith('/') and \
                                      not x.strip() == '',
                            parser.keyword_extractor))
        all_params |= params

    return list(all_params)


def get_parser(referring_url):
    """Utility function to find a parser for a referring URL
    if it is a SERP.

    :param referring_url: either the referring URL as a string or ParseResult
    :returns: SearchEngineParser object if one exists for URL, None otherwise
    """
    engines = _get_search_engines()
    try:
        if isinstance(referring_url, ParseResult):
            url_parts = referring_url
        else:
            url_parts = urlparse(referring_url)
    except:
        return # Malformed URLs

    # First try to look up a search engine by the host name incase we have
    # a direct entry for it
    parser = engines.get(url_parts.netloc, 'nothing')
    if parser == 'nothing':
        # Now we'll try searching by lossy domain which converts
        # things like country codes for us
        parser = engines.get(_get_lossy_domain(url_parts.netloc),
                             'nothing')

    if parser == 'nothing':
        return None # no parser to be found

    return parser


def is_serp(referring_url):
    """Utility function to determine if a referring URL is a SERP URL.

    :returns: True if SERP, False otherwise.
    """
    parser = get_parser(referring_url)
    if parser is None:
        return False
    result = parser.parse(referring_url)

    return result is not None


def extract(serp_url, parser=None, lower_case=True, trimmed=True,
            collapse_whitespace=True):
    """Parse a SERP URL and return information regarding the engine, keyword
    and serp_link.

    This is a far more basic implementation than what Piwik has done in their
    source, but right now, we don't care about all the crazy edge cases.

    :param serp_url: the suspected SERP URL to extract a keyword from
    :param parser: optionally pass in a parser if already looked up via
                   call to get_parser
    :param lower_case: lower case the keyword
    :param trimmed: trim extra spaces before and after keyword
    :param collapse_whitespace: collapse 2 or more \s characters into
                                one space ' '
    :returns: a dict containing engine_name, keyword
    """
    if parser is None:
        parser = get_parser(serp_url)
    if not parser:
        return None # Tried to get keyword from non SERP URL

    result = parser.parse(serp_url)
    if result is None:
        log.debug(('Found search engine parser for {} but was unable to'
                    ' extract keyword.').format(serp_url))
        return None

    if lower_case:
        result.keyword = result.keyword.lower()
    if trimmed:
        result.keyword = result.keyword.strip()
    if collapse_whitespace:
        result.keyword = re.sub(r'\s+', ' ', result.keyword, re.UNICODE)

    return result


def main():
    import argparse
    import sys
    import re

    parser = argparse.ArgumentParser(
        description='Parse a SERP URL to extract engine name and keyword.')

    parser.add_argument('input', metavar='url', type=unicode, nargs='*',
                        help='A potential SERP URL')
    parser.add_argument('-u', '--update', default=False, action='store_true',
                        help=('Force fetch a new list of search engines from '
                              'Piwik (requires PHP locally installed).'))
    parser.add_argument('-l', '--list', default=False, action='store_true',
                        help='Print a list of all the SearchEngineParsers.')

    args = parser.parse_args()

    if args.update:
        _get_piwik_engines(fresh=True)
        sys.exit(0)

    if args.list:
        engines = _get_search_engines()
        engines = sorted(engines.iteritems(), key=lambda x: x[1].engine_name)
        print '{:<30}{}'.format('Fuzzy Domain', 'Parser')
        for fuzzy_domain, parser in engines:
            print '{:<30}{}'.format(fuzzy_domain, parser)
        print '{} parsers.'.format(len(engines))
        sys.exit(0)

    if len(args.input) == 0:
        parser.print_usage()
        sys.exit(1)

    escape_quotes = lambda s: re.sub(r'"', '\\"', s)

    for url in args.input:
        res = extract(url)
        if res is None:
            res = ['""', '""']
        else:
            res = [escape_quotes(res.engine_name), escape_quotes(res.keyword)]
            res = [u'"{}"'.format(r) for r in res]
        print u','.join(res)

if __name__ == '__main__':
    main()
