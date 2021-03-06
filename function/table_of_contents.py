"""Generate a table of contents for an HTML page.

Headings are indexed and placed into nested ordered lists.

For a table of contents to be generated, there must be at least two top-level
headings and one subheading belonging to either top-level heading.

If a heading has an ID, that ID will be used to generate a link in the
table of contents.

"""

from sakura.common import ini
from lxml import etree
from cStringIO import StringIO


SAKURA_ARGS = ['document_path', 'document']
REPLACE_ALL = False


def table_of_contents(document_path, document):
    """Maybe instead of StringIO I should build with lxml?"""

    table_settings = ini('table-of-contents')
    root = etree.HTML(document)  # can define base_url!
    headings = ('h3', 'h4', 'h5', 'h6')
    current_level = -1
    current_level_text = None
    html = StringIO()

    # heading
    open_tag = table_settings['heading']['open_tag']
    close_tag = table_settings['heading']['close_tag']
    text = table_settings['heading']['text']
    html.write(open_tag + text + close_tag)

    # start table of contents... table
    html.write(table_settings['container']['open_tag'])

    try:
        # use os.path instead.
        __, document_path = document_path.split('/', 1)
    except ValueError:
        raise Exception(document_path)

    number_of_entries = 0
    has_nested = False

    for element in root.iter():
        tag = element.tag

        if tag not in headings:
            continue

        number_of_entries += 1
        nest_level = headings.index(tag)
        level_id =  element.get('id')
        level_text = element.text

        if level_id:
            subs = (document_path, level_id, level_text)
            entry = '<a href="%s#%s">%s</a>' % subs

        else:
            entry = level_text

        if nest_level == current_level:
            html.write('<li>%s' % entry)
        elif nest_level > current_level:
            html.write('\n<ol>\n <li>%s' % entry)
        elif nest_level < current_level:
            has_nested = True
            html.write('</ol>\n <li>%s' % entry)

        current_level = nest_level

    if number_of_entries < 2 or not has_nested:
        return ''

    html.write('\n</ol>')
    html.write(table_settings['container']['close_tag'])
    return html.getvalue()

