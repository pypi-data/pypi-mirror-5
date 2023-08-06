import os
from datetime import datetime
from contextlib import contextmanager
import logging
import re
import urllib2
from urlparse import urlsplit

from BeautifulSoup import BeautifulSoup
import formencode as fe
from formencode import validators as fev
import html2text
from ming.utils import LazyProperty
from pylons import tmpl_context as c
from pylons import app_globals as g
from tg import (
        expose,
        redirect,
        validate,
        )
from tg.decorators import (
        with_trailing_slash,
        without_trailing_slash,
        )

from allura.controllers import BaseController
from allura.lib import helpers as h
from allura.lib.decorators import require_post
from allura import model as M

from forgewiki.wiki_main import ForgeWikiApp
from forgewiki import model as WM

from forgeimporters.base import ToolImporter
from forgeimporters.google import GoogleCodeProjectExtractor

TARGET_APP_ENTRY_POINT_NAME = 'Wiki'
DATE_FORMAT = '%a %b %d %H:%M:%S %Y'

log = logging.getLogger(__name__)


@contextmanager
def no_notifications(project):
    try:
        project.notifications_disabled = True
        yield
    finally:
        project.notifications_disabled = False


class GoogleCodeWikiImportSchema(fe.Schema):
    gc_project_name = fev.UnicodeString(not_empty=True)
    mount_point = fev.UnicodeString()
    mount_label = fev.UnicodeString()


class GoogleCodeWikiImportController(BaseController):
    @with_trailing_slash
    @expose('jinja:googlecodewikiimporter:templates/index.html')
    def index(self, **kw):
        return {}

    @without_trailing_slash
    @expose()
    @require_post()
    @validate(GoogleCodeWikiImportSchema(), error_handler=index)
    def create(self, gc_project_name, mount_point, mount_label, **kw):
        c.project.set_tool_data('google-code', project_name=gc_project_name)
        app = GoogleCodeWikiImporter().import_tool(c.project, c.user,
                mount_point=mount_point,
                mount_label=mount_label)
        redirect(app.url())


class GoogleCodeWikiComment(object):
    def __init__(self, soup):
        self.soup = soup

    @LazyProperty
    def _author(self):
        # class="userlink" could be on an `a` or `span` tag
        return self.soup.find('span', 'author').find(attrs={'class': 'userlink'})

    @LazyProperty
    def author_name(self):
        return self._author.text

    @LazyProperty
    def author_link(self):
        if not self._author.get('href'):
            return None
        return GoogleCodeProjectExtractor.BASE_URL + self._author['href']

    @LazyProperty
    def text(self):
        element = self.soup.find('div', 'commentcontent')
        return html2text.HTML2Text().handle(unicode(element))

    @LazyProperty
    def annotated_text(self):
        author = self.author_name
        if self.author_link:
            author = '[{0}]({1})'.format(self.author_name, self.author_link)
        author_snippet = u'Originally posted by: {0}'.format(author)
        return u'{0}\n\n{1}'.format(author_snippet, self.text)

    @LazyProperty
    def timestamp(self):
        return datetime.strptime(self.soup.find('span', 'date')['title'],
                DATE_FORMAT)


class GoogleCodeWikiPage(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.page = BeautifulSoup(urllib2.urlopen(self.url))

    def rewrite_wiki_links(self, text):
        wiki_path = os.path.dirname(urlsplit(self.url).path)
        pat = r'\[([^\]]+)\]\({0}/([^\)]+)\)'.format(wiki_path)
        def repl(match):
            return u'[{0}]({1})'.format(match.group(1), match.group(2))
        return re.sub(pat, repl, text)

    @LazyProperty
    def text(self):
        wiki_content = self.page.find(id='wikimaincol')
        orig = html2text.HTML2Text().handle(unicode(wiki_content))
        return self.rewrite_wiki_links(orig)

    @LazyProperty
    def timestamp(self):
        return datetime.strptime(self.page.find(id='wikiauthor').span['title'],
                DATE_FORMAT)

    @LazyProperty
    def labels(self):
        return [a.text for a in self.page.find(id='wikiheader').findAll(
            'a', 'label')]

    @LazyProperty
    def author(self):
        return self.page.find(id='wikiauthor').a.text

    @LazyProperty
    def comments(self):
        container = self.page.find(id='commentlist')
        if not container:
            return []
        return [GoogleCodeWikiComment(comment) for comment in
                container.findAll('div', 'artifactcomment')]


class GoogleCodeWikiExtractor(GoogleCodeProjectExtractor):
    PAGE_MAP = GoogleCodeProjectExtractor.PAGE_MAP
    PAGE_MAP.update({
        'wiki_index': GoogleCodeProjectExtractor.BASE_URL + '/p/%s/w/list',
        })

    def get_wiki_pages(self):
        page = self.get_page('wiki_index')
        RE_WIKI_PAGE_URL = r'^/p/{0}/wiki/.*$'.format(self.gc_project_name)
        seen = set()
        for a in page.find(id="resultstable").findAll("a"):
            if re.match(RE_WIKI_PAGE_URL, a['href']) and a['href'] not in seen:
                yield (a.text, self.BASE_URL + a['href'])
                seen.add(a['href'])

    def get_default_wiki_page_name(self):
        page = self.get_page('wiki_index')
        a = page.find(id='mt').find('a', 'active')
        if not a:
            return None
        return urlsplit(a['href']).path.split('/')[-1].split('#')[0]


class GoogleCodeWikiImporter(ToolImporter):
    target_app = ForgeWikiApp
    source = 'Google Code'
    controller = GoogleCodeWikiImportController
    tool_label = 'Wiki'
    tool_description = 'Import your wiki pages from Google Code'

    def import_tool(self, project, user, project_name=None, mount_point=None,
            mount_label=None, **kw):
        """ Import a Google Code wiki into a new ForgeWiki app.

        """
        extractor = GoogleCodeWikiExtractor(project, project_name)
        default_wiki_page_name = extractor.get_default_wiki_page_name()
        with no_notifications(project):
            app = project.install_app(
                    TARGET_APP_ENTRY_POINT_NAME,
                    mount_point=mount_point or 'wiki',
                    mount_label=mount_label or 'Wiki',
                    )
            with h.push_context(project._id,
                    mount_point=app.config.options.mount_point):
                for page in self.get_pages(extractor):
                    self.create_page(page)
                    if page.name == default_wiki_page_name:
                        app.root_page_name = page.name
        g.post_event('project_updated')
        return app

    def get_pages(self, extractor):
        for name, url in extractor.get_wiki_pages():
            yield GoogleCodeWikiPage(name, url)

    def create_page(self, page):
        global c
        p = WM.Page.upsert(page.name)
        p.viewable_by = ['all']
        p.text = page.text
        p.mod_date = page.timestamp
        p.labels = page.labels
        with h.push_config(c, user=M.User.anonymous()):
            ss = p.commit()
            ss.mod_date = ss.timestamp = page.timestamp
            for comment in page.comments:
                p.discussion_thread.add_post(text=comment.annotated_text,
                        timestamp=comment.timestamp,
                        ignore_security=True,
                        )
