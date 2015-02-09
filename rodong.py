# Simple library to grab articles from rodong.rep.kp/en
# by Troy Deck
from requests import Session
from lxml import html
from UserDict import DictMixin
from itertools import count

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
            url = DOMAIN + SECTIONS[section_key] + '&page=' + str(page)
            body = self._session.get(url).content

            # Check first that we haven't gone beyond the last page
            # The website uses a javascript redirect embedded halfway
            # down the page to send you back to the first page (!)
            if 'location.href=' in body:
                break

            # Parse out all the article links
            root = html.fromstring(body)
            title_lines = root.find_class('ListNewsLineTitle')
            for title_line in title_lines:
                articles.append(Article(
                    self._session,
                    title_line.text_content().strip(),
                    DOMAIN + '/en/' + title_line.find('a').get('href')
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
                for p_tag in root.findall('*/table//p')
                if p_tag.get('style') == 'text-align: justify'
        ))
        self._photos = [
            DOMAIN + image.get('src')
                for image in root.findall('*/table//img')
        ]

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
