"""Utilities for extracting keyword information from search engine
referrers."""
import re
import logging

from itertools import groupby
from urlparse import urlparse, parse_qs, ParseResult
from iso3166 import countries

# import pkg_resources
# with fallback for environments that lack it
try:
    import pkg_resources
except ImportError:
    import os

    class pkg_resources(object):
        """Fake pkg_resources interface which falls back to getting resources
        inside `serpextract`'s directory. (thank you tldextract!)
        """
        @classmethod
        def resource_stream(cls, package, resource_name):
            moddir = os.path.dirname(__file__)
            f = os.path.join(moddir, resource_name)
            return open(f)

# import cPickle
# for performance with a fallback on Python pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle


__all__ = ('get_parser', 'is_serp', 'extract', 'get_all_query_params')

log = logging.getLogger('serpextract')

_country_codes = [country.alpha2.lower()
                  for country in countries]
# uk is not an official ISO-3166 country code, but it's used in top-level
# domains so we add it to our list see
# http://en.wikipedia.org/wiki/ISO_3166-1 for more information
_country_codes += ['uk']


def _to_unicode(s):
    """Safely decodes a string into unicode if it's not already unicode"""
    return s if isinstance(s, unicode) else s.decode("utf-8", "ignore")


def _serp_query_string(parse_result):
    """
    Some search engines contain the search keyword in the fragment so we
    build a version of a query string that contains the query string and
    the fragment.

    :param parse_result: a URL
    :type parse_result: :class:`urlparse.ParseResult`
    """
    query = parse_result.query
    if parse_result.fragment != '':
        query = '{}&{}'.format(query, parse_result.fragment)

    return query


def _is_url_without_path_query_or_fragment(url_parts):
    """
    Determines if a URL has a blank path, query string and fragment.

    :param url_parts: the URL
    :type url_parts: :class:`urlparse.ParseResult`
    """
    return url_parts.path.strip('/') == '' and url_parts.query == '' \
           and url_parts.fragment == ''

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
   get_engine_name = lambda x: x[1][0]
   definitions_by_engine = groupby(piwik_engines.iteritems(), get_engine_name)
   _engines = {}

   for engine_name, rule_group in definitions_by_engine:
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


def _not_regex(value):
   return not value.startswith('/') and not value.strip() == ''


_piwik_engines = None
def _get_piwik_engines():
   """Return the search engine parser definitions stored in this module"""
   global _piwik_engines
   if _piwik_engines is None:
       stream = pkg_resources.resource_stream
       with stream(__name__, 'search_engines.pickle') as picklestream:
           _piwik_engines = pickle.load(picklestream)

   return _piwik_engines


def _get_lossy_domain(domain):
   """A lossy version of a domain/host to use as lookup in the
   ``_engines`` dict."""
   domain = unicode(domain)
   codes = '|'.join(_country_codes)

   # First, strip off any www., www1., www2., search. domain prefix
   domain = re.sub(r'^(w+\d*|search)\.',
                   '',
                   domain)
   # Now remove domains that are thought of as mobile (m.something.com
   # becomes something.com)
   domain = re.sub(r'(^|\.)m\.',
                   r'\1',
                   domain)
   # Replace country code suffixes from domains (something.co.uk becomes
   # something.{})
   domain = re.sub(r'(\.(com|org|net|co|it|edu))?\.({})(\/|$)'.format(codes),
                   r'.{}\4',
                   domain)
   # Replace country code prefixes from domains (ca.something.com) becomes
   # {}.something.com
   domain = re.sub(r'(^|\.)({})\.'.format(codes),
                   r'\1{}.',
                   domain)
   return domain


class ExtractResult(object):
    __slots__ = ('engine_name', 'keyword', 'parser')

    def __init__(self, engine_name, keyword, parser):
        self.engine_name = engine_name
        self.keyword = keyword
        self.parser = parser

    def __repr__(self):
        repr_fmt = 'ExtractResult(engine_name={!r}, keyword={!r}, parser={!r})'
        return repr_fmt.format(self.engine_name, self.keyword, self.parser)


class SearchEngineParser(object):
    """Handles persing logic for a single line in Piwik's list of search
    engines.

    Piwik's list for reference:

    https://raw.github.com/piwik/piwik/master/core/DataFiles/SearchEngines.php

    This class is not used directly since it already assumes you know the
    exact search engine you want to use to parse a URL. The main interface
    for users of this module is the `get_keyword` method.
    """
    __slots__ = ('engine_name', 'keyword_extractor', 'link_macro', 'charsets')

    def __init__(self, engine_name, keyword_extractor, link_macro, charsets):
        """New instance of a `SearchEngineParser`.

        :param engine_name:         the friendly name of the engine (e.g.
                                    'Google')

        :param keyword_extractor:   a string or list of keyword extraction
                                    methods for this search engine.  If a
                                    single string, we assume we're extracting a
                                    query string param, if it's a string that
                                    starts with '/' then we extract from the
                                    path instead of query string

        :param link_macro:          a string indicating how to build a link to
                                    the search engine results page for a given
                                    keyword

        :param charsets:            a string or list of charsets to use to
                                    decode the keyword
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
        """Get a URL to a SERP for a given keyword.

        :param base_url: string of format ``'<scheme>://<netloc>'``
        :type base_url: str

        :param keyword: search engine keyword
        :type keyword: str

        :returns: a URL that links directly to a SERP for the given keyword.
        """
        if self.link_macro is None:
            return None

        link = u'{}/{}'.format(base_url, self.link_macro.format(k=keyword))
        #link = self.decode_string(link)
        return link

    def parse(self, serp_url):
        """Parse a SERP URL to extract the search keyword.

        :param serp_url: the SERP URL
        :type serp_url: either a string or a :class:`urlparse.ParseResult`
                        object

        :returns: An :class:`ExtractResult` instance.
        """
        if isinstance(serp_url, basestring):
            try:
                url_parts = urlparse(serp_url)
            except ValueError:
                msg = "Malformed URL '{}' could not parse".format(serp_url)
                log.debug(msg, exc_info=True)
                return None
        else:
            url_parts = serp_url
        original_query = _serp_query_string(url_parts)
        query = parse_qs(original_query, keep_blank_values=True)

        keyword = None
        engine_name = self.engine_name
        if engine_name == 'Google Images' or \
           (engine_name == 'Google' and '/imgres' in serp_url):
            # When using Google's image preview mode, it hides the keyword
            # within the prev query string param
            engine_name = 'Google Images'
            if 'prev' in query:
                keyword = parse_qs(urlparse(query['prev'][0]).query)\
                          .get('q')[0]
        elif engine_name == 'Google' and 'as_' in original_query:
            # Google has many different ways to filter results.  When some of
            # these filters are applied, we can no longer just look for the q
            # parameter so we look at additional query string arguments and
            # construct a keyword manually
            keys = []

            # Results should contain all of the words entered
            # Search Operator: None (same as normal search)
            key = query.get('as_q')
            if key:
              keys.append(key[0])
            # Results should contain any of these words
            # Search Operator: <keyword> [OR <keyword>]+
            key = query.get('as_oq')
            if key:
              key = key[0].replace('+', ' OR ')
              keys.append(key)
            # Results should match the exact phrase
            # Search Operator: "<keyword>"
            key = query.get('as_epq')
            if key:
              keys.append(u'"{}"'.format(key[0]))
            # Results should contain none of these words
            # Search Operator: -<keyword>
            key = query.get('as_eq')
            if key:
              keys.append(u'-{}'.format(key[0]))

            keyword = u' '.join(keys).strip()

        if engine_name == 'Google':
            # Check for usage of Google's top bar menu
            tbm = query.get('tbm', [None])[0]
            if tbm == 'isch':
                engine_name = 'Google Images'
            elif tbm == 'vid':
                engine_name = 'Google Video'
            elif tbm == 'shop':
                engine_name = 'Google Shopping'

        if keyword is not None:
            # Edge case found a keyword, exit quickly
            keyword = _to_unicode(keyword)
            return ExtractResult(engine_name, keyword, self)

        # Otherwise we keep looking through the defined extractors
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
                # Search for keywords in query string
                if extractor in query:
                    # Take the last param in the qs because it should be the
                    # most recent
                    keyword = query[extractor][-1]

                # Now we have to check for a tricky case where it is a SERP
                # but just with no keyword as can be the case with Google
                # Images or DuckDuckGo
                if keyword is None and extractor == 'q' and \
                   engine_name in ('Google Images', 'DuckDuckGo'):
                    keyword = ''
                elif keyword is None and extractor == 'q' and \
                     engine_name == 'Google' and \
                     _is_url_without_path_query_or_fragment(url_parts):
                    keyword = ''

        if keyword is not None:
            keyword = _to_unicode(keyword)
            return ExtractResult(engine_name, keyword, self)

    def __repr__(self):
        repr_fmt = ("SearchEngineParser(engine_name={!r}, "
                    "keyword_extractor={!r}, link_macro={!r}, charsets={!r})")
        return repr_fmt.format(
                        self.engine_name,
                        self.keyword_extractor,
                        self.link_macro,
                        self.charsets)


def get_all_query_params():
    """Return all the possible query string params for all search engines.

    :returns: a ``list`` of all the unique query string parameters that are
              used across the search engine definitions.
    """
    engines = _get_search_engines()
    all_params = set()
    for parser in engines.itervalues():
        # Find non-regex params
        params = set(filter(_not_regex, parser.keyword_extractor))
        all_params |= params

    return list(all_params)


def get_parser(referring_url):
    """Utility function to find a parser for a referring URL if it is a SERP.

    :param referring_url: suspected SERP URL
    :type referring_url: str or urlparse.ParseResult

    :returns: :class:`SearchEngineParser` object if one exists for URL,
              ``None`` otherwise
    """
    engines = _get_search_engines()
    try:
        if isinstance(referring_url, ParseResult):
            url_parts = referring_url
        else:
            url_parts = urlparse(referring_url)
    except ValueError:
        msg = "Malformed URL '{}' could not parse".format(referring_url)
        log.debug(msg, exc_info=True)
        # Malformed URLs
        return None

    query = _serp_query_string(url_parts)

    lossy_domain = _get_lossy_domain(url_parts.netloc)
    engine_key = url_parts.netloc

    # Try to find a parser in the engines list.  We go from most specific to
    # least specific order:
    # 1. <domain><path>
    # 2. <lossy_domain><path>
    # 3. <lossy_domain>
    # 4. <domain>
    # The final case has some special exceptions for things like Google custom
    # search engines, yahoo and yahoo images
    if '{}{}'.format(url_parts.netloc, url_parts.path) in engines:
        engine_key = '{}{}'.format(url_parts.netloc, url_parts.path)
    elif '{}{}'.format(lossy_domain, url_parts.path) in engines:
        engine_key = '{}{}'.format(lossy_domain, url_parts.path)
    elif lossy_domain in engines:
        engine_key = lossy_domain
    elif url_parts.netloc not in engines:
        if query[:14] == 'cx=partner-pub':
            # Google custom search engine
            engine_key = 'google.com/cse'
        elif url_parts.path[:28] == '/pemonitorhosted/ws/results/':
            # private-label search powered by InfoSpace Metasearch
            engine_key = 'wsdsold.infospace.com'
        elif '.images.search.yahoo.com' in url_parts.netloc:
            # Yahoo! Images
            engine_key = 'images.search.yahoo.com'
        elif '.search.yahoo.com' in url_parts.netloc:
            # Yahoo!
            engine_key = 'search.yahoo.com'
        else:
            return None

    return engines.get(engine_key)


def is_serp(referring_url):
    """Utility function to determine if a referring URL is a SERP.

    :param referring_url: suspected SERP URL
    :type referring_url: str or urlparse.ParseResult

    :returns: ``True`` if SERP, ``False`` otherwise.
    """
    parser = get_parser(referring_url)
    if parser is None:
        return False
    result = parser.parse(referring_url)

    return result is not None


def extract(serp_url, parser=None, lower_case=True, trimmed=True,
            collapse_whitespace=True):
    """Parse a SERP URL and return information regarding the engine name,
    keyword and :class:`SearchEngineParser`.

    This is a far more basic implementation than what Piwik has done in their
    source, but right now, we don't care about all the crazy edge cases.

    :param serp_url: the suspected SERP URL to extract a keyword from
    :type serp_url: str or urlparse.ParseResult
    :param parser: optionally pass in a parser if already looked up via
                   call to get_parser
    :type parser: :class:`SearchEngineParser`
    :param lower_case: lower case the keyword
    :type lower_case: bool
    :param trimmed: trim extra spaces before and after keyword
    :type trimmed: bool
    :param collapse_whitespace: collapse 2 or more ``\s`` characters into
                                one space ``' '``
    :type collapse_whitespace: bool

    :returns: an :class:`ExtractResult` instance if ``serp_url`` is valid,
              ``None`` otherwise
    """
    url_parts = urlparse(serp_url)
    if parser is None:
        parser = get_parser(url_parts)
    if not parser:
        return None  # Tried to get keyword from non SERP URL

    result = parser.parse(serp_url)

    if result is None:
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
    parser.add_argument('-l', '--list', default=False, action='store_true',
                        help='Print a list of all the SearchEngineParsers.')

    args = parser.parse_args()

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
