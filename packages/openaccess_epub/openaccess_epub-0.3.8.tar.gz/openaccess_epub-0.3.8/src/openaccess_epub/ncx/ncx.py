# -*- coding: utf-8 -*-
"""
This module provides the basic tools necessary to create the NCX (Navigation
Center eXtended) file for ePub. The specification for this file is a subsection
of the OPF specification. See:

http://www.idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.4.1
http://www.niso.org/workrooms/daisy/Z39-86-2005.html#NCX

The NCX file is REQUIRED for valid ePub, but readers support it OPTIONALLY. Its
job is to provide a more advanced Table of Contents-style navigation system for
the ePub beyond what is done in the OPF file.
"""

import openaccess_epub.utils as utils
from openaccess_epub.utils import OrderedSet
from .publisher_metadata import *
from collections import namedtuple
import os
import xml.dom.minidom
import logging

log = logging.getLogger('NCX')

navpoint = namedtuple('navPoint', 'id, label, playOrder, source, children')
navtarget = namedtuple('navTarget', 'id, label, source')

class NCX(object):
    """
    This class represents the NCX file, its generation with input, and its
    output rendering.

    The NCX serves to provide additional Table of Contents-style navigation
    through the ePub file.

    When the NCX class initiates, it contains no content, creating only the
    basic file framework and static data. To pass input articles to the NCX
    class, whether for Single Input Mode or for Collection Mode, use the
    OPF.take_article method.

    Similar to the opf.OPF class, the NCX class maintains a notion of internal
    state. This gives it focus on a single input article at a time,
    incorporating what it needs from the content data to generate internal data
    structures. This model serves as a framework that makes Collection Mode
    much easier and makes cross-journal support possible; it makes little
    difference to Single Input unless one is using an unusual workflow (such as
    using the same NCX instance to generate .ncx files for different ePubs).
    """
    def __init__(self, oae_version, location=os.getcwd(),
                  collection_mode=False):
        """
        Initialization arguments:
            oae_version - Version of OpenAccess_Epub; needed to specify in the
              header what version of OAE generated the toc.ncx file
            location - Where this ePub is based
            collection_mode - To use Collection Mode, set to True

        Collection Mode can be turned on or off after initialization using the
        use_collection_mode() and use_single_mode methods() respectively.
e
        before writing will give it a title.
        """
        #Set internal variables to defaults
        self.reset_state()
        #Pull in argument values
        self.version = oae_version
        self.location = location
        self.collection_mode = collection_mode
        #Create the basic document
        self.init_ncx_document()

    def init_ncx_document(self):
        """
        This method creates the initial DOM document for the toc.ncx file
        """
        publicId = '-//NISO//DTD ncx 2005-1//EN'
        systemId = 'http://www.daisy.org/z3986/2005/ncx-2005-1.dtd'
        impl = xml.dom.minidom.getDOMImplementation()
        doctype = impl.createDocumentType('ncx', publicId, systemId)
        self.document = impl.createDocument(None, 'ncx', doctype)
        #Grab the root <ncx> node
        self.ncx = self.document.lastChild
        self.ncx.setAttribute('version', '2005-1')
        self.ncx.setAttribute('xml:lang', 'en-US')
        self.ncx.setAttribute('xmlns', 'http://www.daisy.org/z3986/2005/ncx/')
        #Create the sub elements to <ncx>
        ncx_subelements = ['head', 'docTitle', 'docAuthor', 'navMap']
        #for element in ncx_subelements:
        #    self.ncx.appendChild(self.document.createElement(element))
        #self.head, self.doctitle, self.docauthor, self.navmap = self.ncx.childNodes
        #Add a label with text 'Table of Contents' to navMap
        #lbl = self.appendNewElement('navLabel', self.navmap)
        #lbl.appendChild(self.make_text('Table of Contents'))
        #Create some optional subelements
        #These are not added to the document yet, as they may not be needed
        #self.list_of_figures = self.document.createElement('navList')
        #self.list_of_figures.setAttribute('class', 'lof')
        #self.list_of_figures.setAttribute('id', 'lof')
        #self.list_of_tables = self.document.createElement('navList')
        #self.list_of_tables.setAttribute('class', 'lot')
        #self.list_of_tables.setAttribute('id', 'lot')
        

    def take_article(self, article):
        """
        Receives an instance of the Article class. This modifies the internal
        state of the NCX class to focus on the new article for the purposes of
        extracting structural information, and the article authors as metadata.
        
        In Collection Mode, the addition of new articles to the NCX class
        results in cumulative (in order of receipt) content. In Single Input
        Mode, the addition of a new article will erase any information from the
        previous article.
        """
        #Reset some things if taking a new article, this prevents accumulation
        #in Single Input Mode.
        if not self.collection_mode:
            self.reset_state()
        #Set state
        self.article = article
        self.all_articles.append(self.article)
        self.doi = article.get_DOI()
        self.all_dois.append(self.doi)
        self.journal_doi, self.article_doi = self.doi.split('/')
        #Pull author metadata from the article metadata for docAuthor elements
        self.extract_article_metadata()
        #Execute addition of elements to self.nav_map
        self.add_article_to_navmap()

    def add_article_to_navmap(self):
        """
        
        """
        #Add a navpoint for the title page
        id = 'titlepage-{0}'.format(self.article_doi)
        label = self.article_title
        source = 'main.{0}.xml#title'.format(self.article_doi)
        title = navpoint(id, label, self.pull_play_order(), source, [])
        self.nav_map.append(title)
        #Check if the article has a body element
        body = self.article.body
        if body:
            self.id_int = 0
            #This step is executed as pre-processing, <sec> elements will receive
            #an id attribute if they lack one
            #This has a, helpful, side-effect when the Article is given to OPS
            for sec in body.getElementsByTagName('sec'):
                if not sec.getAttribute('id'):
                    sec.setAttribute('id', 'OA-EPUB-{0}'.format(self.id_int))
                    self.id_int += 1
        #Recursively parse the structure of the input article and add to navmap
        if body:  # If an article has no body
            for nav_point in self.recursive_article_navmap(body):
                self.nav_map.append(nav_point)
        #Add a navpoint for the references, if there are references
        try:
            back = self.article.root_tag.getElementsByTagName('back')[0]
        except IndexError:
            pass
        else:
            if back.getElementsByTagName('ref'):
                id = 'references-{0}'.format(self.article_doi)
                label = 'References'
                source = 'biblio.{0}.xml#references'.format(self.article_doi)
                references = navpoint(id, label, self.pull_play_order(), source, [])
                self.nav_map.append(references)

    def recursive_article_navmap(self, src_node, depth=0, first=True):
        """
        This function recursively traverses the content of an input article to
        add the correct elements to the NCX file's navMap and Lists.
        """
        if depth > self.maxdepth:
            self.maxdepth = depth
        navpoints = []
        tagnames = ['sec', 'fig', 'table-wrap']
        for child in src_node.childNodes:
            try:
                tagname = child.tagName
            except AttributeError:  # Text nodes have no attribute tagName
                continue
            else:
                if tagname not in tagnames:
                    continue
            source_id = child.getAttribute('id')
            if not self.collection_mode:
                child_id = source_id
            else: #If in collection_mode, prepend the article_doi to avoid collisions
                child_id = '{0}-{1}'.format(self.article_doi, child.getAttribute('id'))
            #Attempt to pull the title text as a label for the navpoint
            try:
                child_title = child.getChildrenByTagName('title')[0]
            except IndexError:
                #label = 'Title Not Found!'
                continue
            else:
                label = utils.serialize_text(child_title)
                if not label:
                    #label = 'Blank Title Found!'
                    continue
            source = 'main.{0}.xml#{1}'.format(self.article_doi, source_id)
            if tagname == 'sec':
                play_order = self.pull_play_order()
                children = self.recursive_article_navmap(child, depth=depth+1)
                new_nav = navpoint(child_id, label, play_order, source, children)
                navpoints.append(new_nav)
            #figs and table-wraps do not have children
            elif tagname == 'fig':  # Add navpoints to list_of_figures
                new_nav = navtarget(child_id, label, source)
                self.list_of_figures.append(new_nav)
            elif tagname == 'table-wrap':  # Add navpoints to list_of_tables
                new_nav = navtarget(child_id, label, source)
                self.list_of_tables.append(new_nav)
        return navpoints

    def extract_article_metadata(self):
        """
        This method calls set_publisher_metadata_methods to ensure that
        publisher-specific methods are being correctly employed. It then
        directs the acquisition of article metadata using these methods, while
        adjusting for collection_mode.
        """
        #Recall that metadata were reset in single mode during take_article
        self.set_publisher_metadata_methods()
        if self.collection_mode:
            pass  # Nothing specific to Collection Mode only at this time
        else:  # Single Mode specific actions
            pass  # Nothing specific to Single Mode only at this time

        #Generally speaking, for the NCX, little differs between Collection and
        #Single modes except for the reset between each article for Single
        #creator is OrderedSet([Creator(name, role, file_as)])
        for creator in self.get_article_creator(self.article):
            self.doc_author.add(creator)
        self.article_title = self.get_article_title(self.article)

    def set_publisher_metadata_methods(self):
        """
        Sets internal methods to be publisher specific for the article at hand.
        """
        if self.journal_doi == '10.1371':
            self.get_article_creator = plos_creator
            self.get_article_title= plos_title
        else:
            raise ValueError('This publisher, {0}, is not supported'.format(self.journal_doi))

    def reset_state(self):
        """
        Resets the internal state variables to defaults, also used in __init__
        to set them at the beginning.
        """
        self.article = None
        self.all_articles = []
        self.doi = ''
        self.all_dois = []
        self.article_doi = ''
        self.journal_doi = ''
        self.play_order = 1
        self.id_int = 0
        self.maxdepth = 0
        self.nav_map = []

        #Reset the other metadata and other structures
        self.reset_metadata()
        self.reset_lists()

    def reset_metadata(self):
        """
        THe NCX file does not truly exist for metadata, but it has a few
        elements held over from the Daisy Talking Book specification. The 
        """
        self.doc_author = OrderedSet()
        self.article_title = ''
        #The docTitle can be auto-generated from self.all_articles, so there is
        #no need to collect anything else

    def reset_lists(self):
        """
        Resets the internal states of the lists of items: List of Figures, List
        of Tables, and List of Equations. This is distinct from the navMap.
        """
        self.list_of_figures = []
        self.list_of_tables = []
        self.list_of_equations = []

    def make_head(self):
        """
        Creates the meta elements for the <head> section of the NCX file.
        """
        #A simple convenience function for making the meta elements
        def make_meta(content, name):
            meta = self.document.createElement('meta')
            meta.setAttribute('content', content)
            meta.setAttribute('name', name)
            return meta

        head = self.document.createElement('head')
        #Add comment about required elements
        head.appendChild(self.document.createComment('''The following metadata\
items, except for dtb:generator, are required for all NCX documents, including\
those conforming to the relaxed constraints of OPS 2.0'''))
        #Add the meta elements
        #dtb:uid - string of joined dois
        head.appendChild(make_meta(','.join(self.all_dois), 'dtb:uid'))
        #dtb:depth - maxdepth of navMap
        head.appendChild(make_meta(str(self.maxdepth), 'dtb:depth'))
        #dtb:totalPageCount
        head.appendChild(make_meta('0', 'dtb:totalPageCount'))
        #dtb:maxPageNumber
        head.appendChild(make_meta('0', 'dtb:maxPageNumber'))
        #dtb:generator
        head.appendChild(make_meta('OpenAccess_EPUB {0}'.format(self.version),
                                   'dtb:generator'))
        self.ncx.appendChild(head)

    def make_docTitle(self):
        """
        Creates the <docTitle> element for the NCX file.
        """
        doc_title_node = self.document.createElement('docTitle')
        text_node = self.document.createElement('text')
        if not self.collection_mode:  # Single Mode
            #Use title of article
            text = 'NCX For: {0}'.format(self.article_title)
        else:  # Collection Mode
            #Use DOIs of all articles
            text = 'NCX For Collection: {0}'.format(','.join(self.all_dois))
        text_node.appendChild(self.document.createTextNode(text))
        doc_title_node.appendChild(text_node)
        self.ncx.appendChild(doc_title_node)

    def make_docAuthor(self):
        """
        Creates the <docAuthor> elements for the NCX file.
        """
        for author in self.doc_author:
            doc_author_node = self.document.createElement('docAuthor')
            text_node = self.document.createElement('text')
            text_node.appendChild(self.document.createTextNode(author.name))
            doc_author_node.appendChild(text_node)
            self.ncx.appendChild(doc_author_node)

    def make_navMap(self, nav=None):
        """
        Creates the <navMap> element for the NCX file. This uses an internal
        recursive core fuinction to translate the self.nav_map data structure
        (which was generated by recursive parsing of input files) into XML.
        """
        #The recursive inner translation function
        #def recursive_nav_parse(nav):
        if nav is None:
            nav_node = self.document.createElement('navMap')
            for nav_point in self.nav_map:
                nav_node.appendChild(self.make_navMap(nav=nav_point))
        else:
            nav_node = self.document.createElement('navPoint')
            nav_node.setAttribute('id', nav.id)
            nav_node.setAttribute('playOrder', nav.playOrder)
            label_node = self.document.createElement('navLabel')
            label_text = self.document.createElement('text')
            label_text.appendChild(self.document.createTextNode(nav.label))
            label_node.appendChild(label_text)
            nav_node.appendChild(label_node)
            content_node = self.document.createElement('content')
            content_node.setAttribute('src', nav.source)
            nav_node.appendChild(content_node)
            for child in nav.children:
                nav_node.appendChild(self.make_navMap(nav=child))
        return nav_node

    def make_list_of_figures(self):
        """
        Makes a navList for the NCX file representing the List of Figures.
        """
        if not self.list_of_figures:
            return
        else:
            navlist_node = self.document.createElement('navList')
            navlist_node.appendChild(self.make_navLabel('List of Figures'))
        for nav in self.list_of_figures:
            nav_target = self.document.createElement('navTarget')
            nav_target.setAttribute('id', nav.id)
            nav_target.appendChild(self.make_navLabel(nav.label))
            content_node = self.document.createElement('content')
            content_node.setAttribute('src', nav.source)
            nav_target.appendChild(content_node)

    def make_list_of_tables(self):
        """
        Makes a navList for the NCX file representing the List of Tables.
        """
        if not self.list_of_tables:
            return
        else:
            navlist_node = self.document.createElement('navList')
            navlist_node.appendChild(self.make_navLabel('List of Tables'))
        for nav in self.list_of_tables:
            nav_target = self.document.createElement('navTarget')
            nav_target.setAttribute('id', nav.id)
            nav_target.appendChild(self.make_navLabel(nav.label))
            content_node = self.document.createElement('content')
            content_node.setAttribute('src', nav.source)
            nav_target.appendChild(content_node)

    def write(self):
        """
        Writing the NCX file is immediately preceded by jobs that finalize
        the NCX document. This includes the creation of the navMap, the
        generation and creation of meta elements in the head, and the navList
        elements.

        Writing the NCX file should be done after all intended input articles
        have been passed in. This will be one of the final steps of the ePub
        creation process.
        """
        #Generate the content for the <head>
        self.make_head()
        #Generate the <docTitle>
        self.make_docTitle()
        #Generate the <docAuthor>(s)
        self.make_docAuthor()
        #Generate the <navMap>
        self.ncx.appendChild(self.make_navMap())
        #Generate the List of Figures
        self.make_list_of_figures()
        #Generate the List of Tables
        self.make_list_of_tables()
        filename = os.path.join(self.location, 'OPS', 'toc.ncx')
        with open(filename, 'wb') as output:
            output.write(self.document.toprettyxml(encoding='utf-8'))

    def pull_play_order(self):
        """
        Returns the current playOrder value as string and increments it.
        """
        self.play_order += 1
        return str(self.play_order - 1)

    def use_collection_mode(self):
        """Enables Collection Mode, sets self.collection_mode to True"""
        self.collection_mode = True

    def use_single_mode(self):
        """Disables Collection Mode, sets self.collection_mode to False"""
        self.collection_mode = False

    def make_navLabel(self, text):
        """
        Creates and returns a navLabel element with the supplied text.
        """
        label_node = self.document.createElement('navLabel')
        label_node = self.document.createElement('navLabel')
        text_node = self.document.createElement('text')
        text_node.appendChild(self.document.createTextNode(text))
        label_node.appendChild(text_node)
        return label_node
