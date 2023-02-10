import sys

project_home = u'/home/onlymyli/public_html/ordercentral'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path
from ordercentral import create_app

application = create_app()
