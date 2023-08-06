import argparse
from datetime import (
        datetime,
        timedelta,
        )
import tempfile

import formencode as fe
from formencode import validators as fev

from ming.orm import session
from pylons import tmpl_context as c
from pylons import app_globals as g
from tg import (
        config,
        expose,
        redirect,
        validate,
        )
from tg.decorators import (
        with_trailing_slash,
        without_trailing_slash,
        )

from allura.controllers import BaseController
from allura.lib.decorators import require_post
from allura.model import ApiTicket

from forgeimporters.base import ToolImporter

from forgewiki.scripts.wiki_from_trac.extractors import WikiExporter
from forgewiki.scripts.wiki_from_trac.loaders import load_data
from forgewiki.scripts.wiki_from_trac.wiki_from_trac import WikiFromTrac
from forgewiki.wiki_main import ForgeWikiApp


class TracWikiImportSchema(fe.Schema):
    trac_url = fev.URL(not_empty=True)
    mount_point = fev.UnicodeString()
    mount_label = fev.UnicodeString()


class TracWikiImportController(BaseController):
    @with_trailing_slash
    @expose('jinja:tracwikiimporter:templates/index.html')
    def index(self, **kw):
        return {}

    @without_trailing_slash
    @expose()
    @require_post()
    @validate(TracWikiImportSchema(), error_handler=index)
    def create(self, trac_url, mount_point, mount_label, **kw):
        app = TracWikiImporter().import_tool(c.project, c.user,
                mount_point=mount_point,
                mount_label=mount_label,
                trac_url=trac_url)
        redirect(app.url())


class TracWikiImporter(ToolImporter):
    target_app = ForgeWikiApp
    source = 'Trac'
    controller = TracWikiImportController
    tool_label = 'Wiki'
    tool_description = 'Import your wiki from Trac.  Note: wiki content is imported, but not revision history or attachments.'

    def import_tool(self, project, user, project_name=None, mount_point=None,
            mount_label=None, trac_url=None, **kw):
        """ Import Trac wiki into a new Allura Wiki tool.

        """
        trac_url = trac_url.rstrip('/') + '/'
        mount_point = mount_point or 'wiki'
        app = project.install_app(
                'Wiki',
                mount_point=mount_point,
                mount_label=mount_label or 'Wiki',
                )
        session(app.config).flush(app.config)
        api_ticket = ApiTicket(user_id=user._id,
                capabilities={"import": ["Projects", project.shortname]},
                expires=datetime.utcnow() + timedelta(minutes=60))
        session(api_ticket).flush(api_ticket)
        options = argparse.Namespace()
        options.api_key = api_ticket.api_key
        options.secret_key = api_ticket.secret_key
        options.project = project.shortname
        options.wiki = mount_point
        options.base_url = config['base_url']
        options.verbose = False
        options.converter = 'html2text'
        options.import_opts = []
        options.user_map_file = None
        with tempfile.NamedTemporaryFile() as f:
            WikiExporter(trac_url, options).export(f)
            f.flush()
            load_data(f.name, WikiFromTrac.parser(), options)
        g.post_event('project_updated')
        return app
