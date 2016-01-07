# coding=UTF-8
# Simple library to grab articles from rodong.rep.kp/en
# by Troy Deck
from requests import Session
from lxml import html
from UserDict import DictMixin
from itertools import count
import re

DOMAIN = 'http://rodong.rep.kp'
SECTIONS = {
    'supreme_leader': '/en/index.php?strPageID=SF01_01_02',
    'in_dprk': '/en/index.php?strPageID=SF01_01_03&iThemeID=2',
    'inter_korean': '/en/index.php?strPageID=SF01_01_03&iThemeID=3',
    'international': '/en/index.php?strPageID=SF01_01_03&iThemeID=4',
    'editorial': '/en/index.php?strPageID=SF01_01_04&iClassID=4',
    'article': '/en/index.php?strPageID=SF01_01_04&iClassID=5',
    'commentary': '/en/index.php?strPageID=SF01_01_04&iClassID=6',
    'document': '/en/index.php?strPageID=SF01_01_05&iClassID=7',
}

class RodongSinmun(DictMixin):
    """
    This class provides a lazy-loaded dictionary interface to the articles on
    the English version of the North Korean news and propaganda website
    Rodong Sinmun ("Workers' Newspaper"). The website is divided into
    a number of sections, and each section is a key in the dictionary.
    Each dictionary entry is a list of Articles in that section.
    """
    def __init__(self, user_agent='JucheBot/1.0'):
        """ Creates a new scraper. """
        self._session = Session()
        self._session.headers.update({'User-Agent': user_agent})
        self._sections = {section: None for section in SECTIONS.keys()}

    def __load_section(self, section_key):
        """
        Reads the set of article links for a section if they are not cached.
        """
        if self._sections[section_key] is not None: return

        articles = []
        for page in count(1):
            if page > 50:
                raise Exception('Last page detection is probably broken')

            url = '{domain}{section}&iMenuID=1&iSubMenuID={page}'.format(
                domain = DOMAIN,
                section = SECTIONS[section_key],
                page = page
            )

            body = self._session.get(url).content

            # This is a very hacky way of detecting the last page
            # that will probably break again in the future
            if "알수 없는 주소" in body: # "Unknown Address"
                break

            # Parse out all the article links
            root = html.fromstring(body)
            title_lines = root.find_class('ListNewsLineTitle')
            for title_line in title_lines:
                title_link = title_line.find('a')

                # The links do a JS open in a new window, so we need to parse
                # it out using this ugly, brittle junk
                href = title_link.get('href')
                match = re.match("javascript:article_open\('(.+)'\)", href)
                if not match:
                    raise Exception("The site's link format has changed and is not compatible")
                path = match.group(1).decode('string_escape')

                articles.append(Article(
                    self._session,
                    title_link.text_content().strip(),
                    DOMAIN + '/en/' + path
                ))

        self._sections[section_key] = articles

    def __getitem__(self, key):
        if key not in self._sections:raise KeyError()
        self.__load_section(key)
        return self._sections[key]

    def keys(self):
        return self._sections.keys()

class Article(object):
    """ A lazy-loaded representation of a Rodong Sinmun article """
    def __init__(self, session, title, url):
        """ Creates a new Article """
        self._session = session
        self.url = url
        self.title = title
        self._text = None
        self._photos = None

    def __load(self):
        """ Loads text and photos if they are not cached. """
        if self._text is not None: return

        body = self._session.get(self.url).content
        root = html.fromstring(body)
        self._text = "\n".join((
            p_tag.text_content()
                for p_tag in root.findall('.//p[@class="ArticleContent"]')
                if 'justify' in p_tag.get('style', '')
        ))

        # TODO fix this
        self._photos = []

    @property
    def text(self):
        """ The article's text """
        self.__load()
        return self._text

    @property
    def photos(self):
        """ A list of absolute URLs to the article's photos """
        self.__load()
        return self._photos
