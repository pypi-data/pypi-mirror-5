import re
from lxml.etree import tounicode
from lxml.etree import tostring
from lxml.html.clean import Cleaner
from lxml.html import fragment_fromstring
from lxml.html import fromstring
from operator import attrgetter
from pprint import PrettyPrinter

from breadability.document import OriginalDocument
from breadability.logconfig import LOG
from breadability.logconfig import LNODE
from breadability.scoring import score_candidates
from breadability.scoring import get_link_density
from breadability.scoring import get_class_weight
from breadability.scoring import is_unlikely_node
from breadability.utils import cached_property


html_cleaner = Cleaner(scripts=True, javascript=True, comments=True,
                  style=True, links=True, meta=False, add_nofollow=False,
                  page_structure=False, processing_instructions=True,
                  embedded=False, frames=False, forms=False,
                  annoying_tags=False, remove_tags=None,
                  remove_unknown_tags=False, safe_attrs_only=False)


BASE_DOC = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    </head>
    <body>
    </body>
</html>
"""
SCORABLE_TAGS = ['div', 'p', 'td', 'pre', 'article']


def drop_tag(doc, *tags):
    """Helper to just remove any nodes that match this html tag passed in

    :param *tags: one or more html tag strings to remove e.g. style, script

    """
    for tag in tags:
        found = doc.iterfind(".//" + tag)
        for n in found:
            LNODE.log(n, 1, "Dropping tag")
            n.drop_tree()
    return doc


def is_bad_link(a_node):
    """Helper to determine if the link is something to clean out

    We've hit articles with many multiple links that should be cleaned out
    because they're just there to pollute the space. See tests for examples.

    """
    if a_node.tag == 'a':
        name = a_node.get('name')
        href = a_node.get('href')
        if name and not href:
            return True

        if href:
            url_bits = href.split('#')
            if len(url_bits) == 2:
                if len(url_bits[1]) > 25:
                    return True
    return False


def ok_embedded_video(node):
    """Check if this embed/video is an ok one to count."""
    keep_keywords = ['youtube', 'blip.tv', 'vimeo']
    node_str = tounicode(node)
    for key in keep_keywords:
        if key in node_str:
            return True
    return False


def build_base_document(html, fragment=True):
    """Return a base document with the body as root.

    :param html: Parsed Element object
    :param fragment: Should we return a <div> doc fragment or a full <html>
    doc.

    """
    if html.tag == 'body':
        html.tag = 'div'
        found_body = html
    else:
        found_body = html.find('.//body')

    if found_body is None:
        frag = fragment_fromstring('<div/>')
        frag.set('id', 'readabilityBody')
        frag.append(html)

        if not fragment:
            output = fromstring(BASE_DOC)
            insert_point = output.find('.//body')
            insert_point.append(frag)
        else:
            output = frag
    else:

        found_body.tag = 'div'
        found_body.set('id', 'readabilityBody')

        if not fragment:
            output = fromstring(BASE_DOC)
            insert_point = output.find('.//body')
            insert_point.append(found_body)
        else:
            output = found_body

    output.doctype = "<!DOCTYPE html>"
    return output


def build_error_document(html, fragment=True):
    """Return an empty erorr document with the body as root.

    :param fragment: Should we return a <div> doc fragment or a full <html>
    doc.

    """
    frag = fragment_fromstring('<div/>')
    frag.set('id', 'readabilityBody')
    frag.set('class', 'parsing-error')

    if not fragment:
        output = fromstring(BASE_DOC)
        insert_point = output.find('.//body')
        insert_point.append(frag)
    else:
        output = frag

    output.doctype = "<!DOCTYPE html>"
    return output


def transform_misused_divs_into_paragraphs(doc):
    """Turn all divs that don't have children block level elements into p's

    Since we can't change the tree as we iterate over it, we must do this
    before we process our document.

    The idea is that we process all divs and if the div does not contain
    another list of divs, then we replace it with a p tag instead appending
    it's contents/children to it.

    """
    for elem in doc.iter(tag='div'):
        child_tags = [n.tag for n in elem.getchildren()]
        if 'div' not in child_tags:
            # if there is no div inside of this div...then it's a leaf
            # node in a sense.
            # We need to create a <p> and put all it's contents in there
            # We'll just stringify it, then regex replace the first/last
            # div bits to turn them into <p> vs <div>.
            LNODE.log(elem, 1, 'Turning leaf <div> into <p>')
            orig = tounicode(elem).strip()
            started = re.sub(r'^<\s*div', '<p', orig)
            ended = re.sub(r'div>$', 'p>', started)
            elem.getparent().replace(elem, fromstring(ended))
    return doc


def check_siblings(candidate_node, candidate_list):
    """Look through siblings for content that might also be related.

    Things like preambles, content split by ads that we removed, etc.

    """
    candidate_css = candidate_node.node.get('class')
    potential_target = candidate_node.content_score * 0.2
    sibling_target_score = potential_target if potential_target > 10 else 10
    parent = candidate_node.node.getparent()
    siblings = parent.getchildren() if parent is not None else []

    for sibling in siblings:
        append = False
        content_bonus = 0

        if sibling is candidate_node.node:
            LNODE.log(sibling, 1, 'Sibling is the node so append')
            append = True

        # Give a bonus if sibling nodes and top candidates have the example
        # same class name
        if candidate_css and sibling.get('class') == candidate_css:
            content_bonus += candidate_node.content_score * 0.2

        if sibling in candidate_list:
            adjusted_score = candidate_list[sibling].content_score + \
                content_bonus

            if adjusted_score >= sibling_target_score:
                append = True

        if sibling.tag == 'p':
            link_density = get_link_density(sibling)
            content = sibling.text_content()
            content_length = len(content)

            if content_length > 80 and link_density < 0.25:
                append = True
            elif content_length < 80 and link_density == 0:
                if ". " in content:
                    append = True

        if append:
            LNODE.log(sibling, 1, 'Sibling being appended')
            if sibling.tag not in ['div', 'p']:
                # We have a node that isn't a common block level element, like
                # a form or td tag. Turn it into a div so it doesn't get
                # filtered out later by accident.
                sibling.tag = 'div'

            if candidate_node.node != sibling:
                candidate_node.node.append(sibling)

    return candidate_node


def clean_document(node):
    """Clean up the final document we return as the readable article"""
    if node is None or len(node) == 0:
        return

    LNODE.log(node, 2, "Processing doc")
    clean_list = ['object', 'h1']
    to_drop = []

    # If there is only one h2, they are probably using it as a header and
    # not a subheader, so remove it since we already have a header.
    if len(node.findall('.//h2')) == 1:
        LOG.debug('Adding H2 to list of nodes to clean.')
        clean_list.append('h2')

    for n in node.iter():
        LNODE.log(n, 2, "Cleaning iter node")
        # clean out any in-line style properties
        if 'style' in n.attrib:
            n.set('style', '')

        # remove all of the following tags
        # Clean a node of all elements of type "tag".
        # (Unless it's a youtube/vimeo video. People love movies.)
        is_embed = True if n.tag in ['object', 'embed'] else False
        if n.tag in clean_list:
            allow = False

            # Allow youtube and vimeo videos through as people usually
            # want to see those.
            if is_embed:
                if ok_embedded_video(n):
                    allow = True

            if not allow:
                LNODE.log(n, 2, "Dropping Node")
                to_drop.append(n)

        if n.tag in ['h1', 'h2', 'h3', 'h4']:
            # clean headings
            # if the heading has no css weight or a high link density,
            # remove it
            if get_class_weight(n) < 0 or get_link_density(n) > .33:
                LNODE.log(n, 2, "Dropping <hX>, it's insignificant")
                to_drop.append(n)

        # clean out extra <p>
        if n.tag == 'p':
            # if the p has no children and has no content...well then down
            # with it.
            if not n.getchildren() and len(n.text_content()) < 5:
                LNODE.log(n, 2, 'Dropping extra <p>')
                to_drop.append(n)

        # finally try out the conditional cleaning of the target node
        if clean_conditionally(n):
            to_drop.append(n)

    [n.drop_tree() for n in to_drop if n.getparent() is not None]
    return node


def clean_conditionally(node):
    """Remove the clean_el if it looks like bad content based on rules."""
    target_tags = ['form', 'table', 'ul', 'div', 'p']

    LNODE.log(node, 2, 'Cleaning conditionally node.')

    if node.tag not in target_tags:
        # this is not the tag you're looking for
        LNODE.log(node, 2, 'Node cleared.')
        return

    weight = get_class_weight(node)
    # content_score = LOOK up the content score for this node we found
    # before else default to 0
    content_score = 0

    if (weight + content_score < 0):
        LNODE.log(node, 2, 'Dropping conditional node')
        LNODE.log(node, 2, 'Weight + score < 0')
        return True

    if node.text_content().count(',') < 10:
        LOG.debug("There aren't 10 ,s so we're processing more")

        # If there are not very many commas, and the number of
        # non-paragraph elements is more than paragraphs or other ominous
        # signs, remove the element.
        p = len(node.findall('.//p'))
        img = len(node.findall('.//img'))
        li = len(node.findall('.//li')) - 100
        inputs = len(node.findall('.//input'))

        embed = 0
        embeds = node.findall('.//embed')
        for e in embeds:
            if ok_embedded_video(e):
                embed += 1
        link_density = get_link_density(node)
        content_length = len(node.text_content())

        remove_node = False

        if li > p and node.tag != 'ul' and node.tag != 'ol':
            LNODE.log(node, 2, 'Conditional drop: li > p and not ul/ol')
            remove_node = True
        elif inputs > p / 3.0:
            LNODE.log(node, 2, 'Conditional drop: inputs > p/3.0')
            remove_node = True
        elif content_length < 25 and (img == 0 or img > 2):
            LNODE.log(node, 2,
                'Conditional drop: len < 25 and 0/>2 images')
            remove_node = True
        elif weight < 25 and link_density > 0.2:
            LNODE.log(node, 2,
                'Conditional drop: weight small and link is dense')
            remove_node = True
        elif weight >= 25 and link_density > 0.5:
            LNODE.log(node, 2,
                'Conditional drop: weight big but link heavy')
            remove_node = True
        elif (embed == 1 and content_length < 75) or embed > 1:
            LNODE.log(node, 2,
                'Conditional drop: embed w/o much content or many embed')
            remove_node = True

        if remove_node:
            LNODE.log(node, 2, 'Node will be removed')
        else:
            LNODE.log(node, 2, 'Node cleared')
        return remove_node

    # nope, don't remove anything
    LNODE.log(node, 2, 'Node Cleared final.')
    return False


def prep_article(doc):
    """Once we've found our target article we want to clean it up.

    Clean out:
    - inline styles
    - forms
    - strip empty <p>
    - extra tags

    """
    doc = clean_document(doc)
    return doc


def find_candidates(doc):
    """Find cadidate nodes for the readable version of the article.

    Here's we're going to remove unlikely nodes, find scores on the rest, and
    clean up and return the final best match.

    """
    scorable_node_tags = SCORABLE_TAGS
    nodes_to_score = []
    should_remove = []

    for node in doc.iter():
        if is_unlikely_node(node):
            LOG.debug('We should drop unlikely: ' + str(node))
            should_remove.append(node)
            continue
        if node.tag == 'a' and is_bad_link(node):
            LOG.debug('We should drop bad link: ' + str(node))
            should_remove.append(node)
            continue
        if node.tag in scorable_node_tags and node not in nodes_to_score:
            nodes_to_score.append(node)
    return score_candidates(nodes_to_score), should_remove


class Article(object):
    """Parsed readable object"""
    _should_drop = []

    def __init__(self, html, url=None, fragment=True):
        """Create the Article we're going to use.

        :param html: The string of html we're going to parse.
        :param url: The url so we can adjust the links to still work.
        :param fragment: Should we return a <div> fragment or a full <html>
        doc.

        """
        LOG.debug('Url: ' + str(url))
        self.orig = OriginalDocument(html, url=url)
        self.fragment = fragment

    def __str__(self):
        return tostring(self._readable)

    def __unicode__(self):
        return tounicode(self._readable)

    @cached_property(ttl=600)
    def doc(self):
        """The doc is the parsed xml tree of the given html."""
        try:
            doc = self.orig.html
            # cleaning doesn't return, just wipes in place
            html_cleaner(doc)
            doc = drop_tag(doc, 'noscript', 'iframe')
            doc = transform_misused_divs_into_paragraphs(doc)
            return doc
        except ValueError:
            return None

    @cached_property(ttl=600)
    def candidates(self):
        """Generate the list of candidates from the doc."""
        doc = self.doc
        if doc is not None and len(doc):
            candidates, should_drop = find_candidates(doc)
            self._should_drop = should_drop
            return candidates
        else:
            return None

    @cached_property(ttl=600)
    def readable(self):
        return tounicode(self._readable)

    @cached_property(ttl=600)
    def _readable(self):
        """The readable parsed article"""
        if self.candidates:
            LOG.debug('Candidates found:')
            pp = PrettyPrinter(indent=2)

            # cleanup by removing the should_drop we spotted.
            [n.drop_tree() for n in self._should_drop
                if n.getparent() is not None]

            # right now we return the highest scoring candidate content
            by_score = sorted([c for c in self.candidates.values()],
                key=attrgetter('content_score'), reverse=True)
            LOG.debug(pp.pformat(by_score))

            # since we have several candidates, check the winner's siblings
            # for extra content
            winner = by_score[0]
            LOG.debug('Selected winning node: ' + str(winner))
            updated_winner = check_siblings(winner, self.candidates)
            LOG.debug('Begin final prep of article')
            updated_winner.node = prep_article(updated_winner.node)
            if updated_winner.node is not None:
                doc = build_base_document(updated_winner.node, self.fragment)
            else:
                LOG.warning('Had candidates but failed to find a cleaned winning doc.')
                doc = self._handle_no_candidates()
        else:
            LOG.warning('No candidates found: using document.')
            LOG.debug('Begin final prep of article')
            doc = self._handle_no_candidates()

        return doc

    def _handle_no_candidates(self):
        """If we fail to find a good candidate we need to find something else."""
        # since we've not found a good candidate we're should help this
        if self.doc is not None and len(self.doc):
            # cleanup by removing the should_drop we spotted.
            [n.drop_tree() for n in self._should_drop
                if n.getparent() is not None]
            doc = prep_article(self.doc)
            doc = build_base_document(doc, self.fragment)
        else:
            LOG.warning('No document to use.')
            doc = build_error_document(self.fragment)

        return doc
