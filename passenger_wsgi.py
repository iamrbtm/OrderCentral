import sys
project_home = u'/home/onlymyli/public_html/bazaar'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
from bazaar import create_app
application = create_app()