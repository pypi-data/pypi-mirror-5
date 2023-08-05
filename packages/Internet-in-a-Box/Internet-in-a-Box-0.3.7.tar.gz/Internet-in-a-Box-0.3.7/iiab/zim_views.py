# ZIM file URL views (for Wikipedia)
from flask import Blueprint, Response, render_template

from zim import Library, replace_paths
from config import config

blueprint = Blueprint('zim_views', __name__,
                      template_folder='templates', static_folder='static')


@blueprint.route('/<humanReadableId>')
def zim_main_page_view(humanReadableId):
    """Returns the main page of the zim file"""
    library_xml = config().get_path('KIWIX', 'library')
    lib = Library(library_xml)
    zimfile = lib.get_zimfile(humanReadableId)
    try:
        article, mimetype, ns = zimfile.get_main_page()
        html = mangle_article(article, mimetype, humanReadableId)
        return Response(html, mimetype=mimetype)
    except OSError as e:
        html = "<html><body>"
        html += "<p>Error accessing article.  Possible failure to run zimdump command</p>"
        html += "<p>zimdump = " + config().get_path('KIWIX', 'zimdump') + "</p>\n"
        html += "<p>Exception: " + str(e) + "</p>\n"
        html += "</body></html>"
        return Response(html)


def mangle_article(html, mimetype, humanReadableId):
    if mimetype in ['text/html; charset=utf-8', 'stylesheet/css', 'text/html']:
        try:
            html = html.decode('utf-8')
        except UnicodeDecodeError:
            try:
                print "utf-8 decoding failed, falling back to latin1"
                html = html.decode('latin1')
            except:
                print "utf-8 and latin1 decoding failed"
                return html
        html = replace_paths("iiab/zim/" + humanReadableId, html)
    return html


@blueprint.route('/<humanReadableId>/<namespace>/<path:url>')
def zim_view(humanReadableId, namespace, url):
    library_xml = config().get_path('KIWIX', 'library')
    lib = Library(library_xml)
    article, mimetype, ns = lib.get_article_by_url(humanReadableId, namespace, url)
    html = mangle_article(article, mimetype, humanReadableId)
    return Response(html, mimetype=mimetype)


@blueprint.route('/iframe/<humanReadableId>')
def iframe_main_page_view(humanReadableId):
    url = '/iiab/zim/' + humanReadableId + '/'
    return render_template('zim_iframe.html', url=url)


@blueprint.route('/iframe/<humanReadableId>/<namespace>/<path:url>')
def iframe_view(humanReadableId, namespace, url):
    url = '/iiab/zim/' + humanReadableId + '/' + namespace + '/' + url
    return render_template('zim_iframe.html', url=url)
