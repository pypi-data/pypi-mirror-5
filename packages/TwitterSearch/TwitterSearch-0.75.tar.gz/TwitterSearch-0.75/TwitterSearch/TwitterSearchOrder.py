import datetime
from .TwitterSearchException import TwitterSearchException
from .utils import py3k

try: from urllib.parse import parse_qs as parse # python3
except ImportError: from urlparse import parse_qs as parse #python2

try: from urllib.parse import quote_plus # python3
except ImportError: from urllib import quote_plus # python2

class TwitterSearchOrder(object):

    # default value for count should be the maximum value to minimize traffic
    # see https://dev.twitter.com/docs/api/1.1/get/search/tweets
    _max_count = 100

    # taken from http://www.loc.gov/standards/iso639-2/php/English_list.php
    iso_6391 = ['aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az', 'ba', 'be', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'br', 'bs', 'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy', 'da', 'de', 'dv', 'dz', 'ee', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gu', 'gv', 'ha', 'he', 'hi', 'ho', 'hr', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'ka', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'kv', 'kw', 'ky', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'na', 'nb', 'nd', 'ne', 'ng', 'nl', 'nn', 'no', 'nr', 'nv', 'ny', 'oc', 'oj', 'om', 'or', 'os', 'pa', 'pi', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'rw', 'sa', 'sc', 'sd', 'se', 'sg', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'wo', 'xh', 'yi', 'yo', 'za', 'zh', 'zu']

    def __init__(self):
        self.arguments = { 'count' : '%s' % self._max_count }
        self.searchterms = []
        self.url = ''
        self.manual_url = False

    def addKeyword(self, word):
        if py3k:
            if isinstance(word, str) and len(word) >= 2:
              self.searchterms.append(word)
            elif isinstance(word, list):
                self.searchterms += word
            else:
                raise TwitterSearchException(1000)
        else:
            if isinstance(word, basestring) and len(word) >= 2:
                self.searchterms.append(word)
            elif isinstance(word, list):
                self.searchterms += word
            else:
                raise TwitterSearchException(1000)

    def setKeywords(self, word):
        if not isinstance(word, list):
            raise TwitterSearchException(1001)
        self.searchterms = word

    def setSearchURL(self, url):
        if url[0] == '?':
            url = url[1:]

        args = parse(url)
        self.searchterms = args['q']
        del args['q']

        self.arguments = {}
        for key, value in args.items():
            self.arguments.update({key : value[0]}) 

    def createSearchURL(self):
        if len(self.searchterms) == 0:
            raise TwitterSearchException(1015)

        url = '?'
        url += 'q='
        for term in self.searchterms:
            url += '%s+' % quote_plus(term)
        url = url[0:len(url)-1]

        for key, value in self.arguments.items():
            url += '&' +'%s=%s' % (quote_plus(key), quote_plus(value))

        self.url = url
        return self.url

    def setLanguage(self, lang):
        if len(lang) == 2 and lang in self.iso_6391:
            self.arguments.update( { 'lang' : '%s' % lang } )
        else:
            raise TwitterSearchException(1002)

    def setLocale(self, lang):
        if len(lang) == 2 and lang in self.iso_6391:
            self.arguments.update( { 'locale' : '%s' % lang } )
        else:
            raise TwitterSearchException(1002)

    def setResultType(self, tor):
        if tor == 'mixed' or tor == 'recent' or tor == 'popular':
            self.arguments.update( { 'result_type' : '%s' % tor } )
        else:
            raise TwitterSearchException(1003)

    def setSinceID(self, twid):
        if py3k:
            if not isinstance(twid, int):
                raise TwitterSearchException(1004)
        else:
           if not isinstance(twid, (int, long)):
                raise TwitterSearchException(1004)

        if twid > 0:
            self.arguments.update( { 'since_id' : '%s' % twid } )
        else:
            raise TwitterSearchException(1004)

    def setMaxID(self, twid):
        if py3k:
            if not isinstance(twid, int):
                raise TwitterSearchException(1004)
        else:
           if not isinstance(twid, (int, long)):
                raise TwitterSearchException(1004)

        if twid > 0:
            self.arguments.update( { 'max_id' : '%s' % twid } )
        else:
            raise TwitterSearchException(1004)

    def setCount(self, cnt):
        if isinstance(cnt, int) and cnt > 0 and cnt <= 100:
            self.arguments.update( { 'count' : '%s' % cnt } )
        else:
            raise TwitterSearchException(1004)

    def setGeocode(self, latitude, longitude, radius, unit):
        if py3k:
            if not isinstance(radius, int):
                raise TwitterSearchException(1004)
        else:
           if not isinstance(radius, (int, long)):
                raise TwitterSearchException(1004)

        if isinstance(latitude, float) and isinstance(longitude, float):
            if unit == 'mi' or unit == 'km':
                self.arguments.update( { 'geocode' : '%s,%s,%s%s' % (latitude, longitude, radius, unit) } )
            else:
                raise TwitterSearchException(1005)
        else:
            raise TwitterSearchException(1004)

    def setCallback(self, func):
        if py3k:
            if isinstance(func, str) and func:
                self.arguments.update( { 'callback' : '%s' % func } )
            else:
                raise TwitterSearchException(1006)
        else:
            if isinstance(func, basestring) and func:
                self.arguments.update( { 'callback' : '%s' % func } )
            else:
                raise TwitterSearchException(1006)


    def setUntil(self, date):
        if isinstance(date, datetime.date):
            self.arguments.update( { 'unitl' : '%s' % date.strftime('%Y-%m-%d') } )
        else:
            raise TwitterSearchException(1007)

    def setIncludeEntities(self, include):
        if not isinstance(include, (bool, int)) and ( include == 1 or include == 0):
            raise TwitterSearchException(1008)

        if include:
            self.arguments.update( { 'include_entities' : 'True' } )
        else:
            self.arguments.update( { 'include_entities' : 'False' } )
