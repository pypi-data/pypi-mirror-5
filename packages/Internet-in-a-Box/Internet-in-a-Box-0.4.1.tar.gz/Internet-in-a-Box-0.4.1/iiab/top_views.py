# Top level URL views
from flask import (Blueprint, make_response, render_template,
                   send_file, redirect, abort)

from config import config
from utils import mdns_resolve

blueprint = Blueprint('top_views', __name__,
                      template_folder='templates', static_folder='static')


@blueprint.route('/')
def index():
    error = None
    if config().get_knowledge_dir() is None:
        error = "Could not find knowledge directory containing Internet-in-a-Box dataset.  "
        error += "The configured knowledge_dir path is " + config().get('DEFAULT', 'knowledge_dir')
        error += " and search_for_knowledge_dir is "
        if config().get('DEFAULT', 'search_for_knowledge_dir'):
            error += "ON, so all mounted filesystems were checked."
        else:
            error += "OFF, so other mounted filesystems were NOT checked."
    return render_template("home.html", error=error)


@blueprint.route('detect')
def detect_view():
    """Detect if a valid IIAB installation exists on the localhost
    or the local network (using mDNS).  Returns a 404 if no
    IIAB installation found."""
    localhost_iiab = config().get_knowledge_dir()
    if localhost_iiab is not None:
        return "true"
    try:
        address = mdns_resolve("know.local")
        if address is not None:
            return "true"
    except:
        pass
    abort(404)


@blueprint.route('redirect')
def redirect_view():
    """Redirect the browser to our index or, if the
    local machine is not configured, attempt to
    resolve the mdns name know.local"""
    localhost_iiab = config().get_knowledge_dir()
    if localhost_iiab is not None:
        return index()
    try:
        address = mdns_resolve("know.local")
        if address is not None:
            return redirect("http://" + address)
    except:
        pass
    return index()  # This will display an error, but that is better than nothing


# This is a hack because of the double //static path issue
#@blueprint.route('static/<path:filename>')
#def static(filename):
#    return blueprint.send_static_file(filename)


@blueprint.route('test')
def test():
    print "TEST"
    return make_response((send_file('/var/www/foo.webm', mimetype="video/webm"), 200, {'Accept-Ranges': 'bytes'}))
