import os
import sys
import transaction
import csv

from sqlalchemy import engine_from_config

CSV_HEADER =['urlname', 'parentname', 'baseref', 'result', 'warningstring',
    'infostring', 'valid', 'url', 'line', 'column', 'name', 'dltime',
    'dlsize', 'checktime', 'cached', 'level', 'modified']



from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    CheckedLink,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        DBSession.query(CheckedLink).delete()
