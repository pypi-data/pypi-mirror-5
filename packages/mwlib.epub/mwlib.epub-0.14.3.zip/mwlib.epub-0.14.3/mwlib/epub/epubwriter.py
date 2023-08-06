#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2012, PediaPress GmbH
# See README.txt for additional licensing information.

import os
import shutil
import zipfile
import tempfile
import mimetypes
import urlparse
from xml.sax.saxutils import escape as xmlescape

from pprint import pprint

from collections import namedtuple

from lxml import etree
from lxml.builder import ElementMaker

from mwlib.epub import config
from mwlib.epub.treeprocessor import TreeProcessor, safe_xml_id, clean_url, remove_node
from mwlib.epub import collection
from mwlib.epub.utils import misc

_ = lambda txt: txt # FIXME: add proper translation support

ArticleInfo = namedtuple('ArticleInfo', 'id path title type')

E = ElementMaker()

def serialize(f):
    return lambda : etree.tostring(f(), pretty_print=True)

class EpubContainer(object):

    def __init__(self, fn, coll):
        self.zf = zipfile.ZipFile(fn, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
        self.zf.debug = 3
        self.added_files = set()
        self.write_mime_type()
        self.write_meta_inf()
        self.articles =[]
        self.coll = coll
        self.cover_img_path = None

    def add_file(self, fn, content, compression=True):
        if fn in self.added_files:
            return
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        self.zf.writestr(fn, content)
        self.added_files.add(fn)

    def link_file(self, fn, arcname, compression=True):
        if arcname in self.added_files:
            return
        compression_flag = zipfile.ZIP_DEFLATED if compression else zipfile.ZIP_STORED
        self.zf.write(fn, arcname, compression_flag)
        self.added_files.add(arcname)

    def write_mime_type(self):
        fn = os.path.join(os.path.dirname(__file__), 'mimetype')
        self.link_file(fn, 'mimetype', compression=False)

    def write_meta_inf(self):
        opf_content=u'''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="%(opf_fn)s" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
''' % {'opf_fn': config.opf_fn}
        self.add_file(fn=config.meta_inf_fn, content=opf_content)

    def close(self):
        self.writeOPF()
        self.writeNCX()
        self.zf.close()

    def writeNCX(self):
        meta = [E.meta({'name': item[0],
                        'content': item[1]}
                       ) for item in [("dtb:uid", self.coll.coll_id),
                                      ("dtb:depth", "1"),
                                      ("dtb:totalPageCount", '0'),
                                      ("dtb:maxPageNumber", '0') ]]
        if self.cover_img_path:
            meta.append(E.meta(dict(name='cover',
                                    content='cover-image')))
        tree = E.ncx({'version': '2005-1',
                      'xmlns': 'http://www.daisy.org/z3986/2005/ncx/'},
                     E.head(*meta),
                     E.docTitle(E.text(self.coll.title)),
                     E.docAuthor(E.text(self.coll.editor)),
                     )


        nav_map = E.navMap()
        last_chapter = None
        for (idx, article) in enumerate(self.articles):
            nav_point = E.navPoint({'id': article.id,
                                    'playOrder': str(idx+1)},
                                   E.navLabel(E.text(article.title)),
                                   E.content(src=article.path))
            if article.type == 'article' and last_chapter != None:
                last_chapter.append(nav_point)
                continue
            if article.type == 'chapter':
                last_chapter = nav_point
            nav_map.append(nav_point)

        tree.append(nav_map)
        xml = etree.tostring(tree, method='xml', encoding='utf-8',pretty_print=True, xml_declaration=True)

        self.add_file(config.ncx_fn, xml)

    def writeOPF(self):
        nsmap = {'dc': "http://purl.org/dc/elements/1.1/",
                 'opf': "http://www.idpf.org/2007/opf"}
        def writeOPF_metadata():
            E = ElementMaker(nsmap=nsmap)
            DC = ElementMaker(namespace=nsmap['dc'])
            tree = E.metadata(DC.identifier({'id':'bookid'}, self.coll.coll_id),
                              DC.language(self.coll.language),
                              DC.title(self.coll.title or 'untitled'),
                              DC.creator(self.coll.editor),
                              DC.publisher(config.publisher),
                              )
            return tree

        def writeOPF_manifest():
            tree = E.manifest()
            tree.extend([E.item({'id': article.id,
                                 'href': article.path,
                                 'media-type': 'application/xhtml+xml'})
                         for article in self.articles])
            tree.append(E.item({'id':'ncx',
                                'href': os.path.basename(config.ncx_fn),
                                'media-type': 'application/x-dtbncx+xml'}))
            #FIXME add missing resources:
            # images
            # css
            for fn in self.added_files:
                if fn.startswith('OPS/'):
                    fn = fn[4:]
                mimetype, encoding = mimetypes.guess_type(fn)
                if mimetype in ['text/css',
                                'image/png',
                                'image/jpeg',
                                'image/gif',
                                ]:
                    _id = 'cover-image' if fn==self.cover_img_path else safe_xml_id(fn)
                    tree.append(E.item({'id': _id,
                                        'href': fn,
                                        'media-type': mimetype}))

            return tree

        def writeOPF_spine():
            tree = E.spine({'toc': 'ncx'})
            for article in self.articles:
                if article.type == 'cover':
                    tree.append(E.itemref(idref=article.id, linear="no"))
                else:
                    tree.append(E.itemref(idref=article.id))
            return tree

        tree = E.package({'version': "2.0",
                          'xmlns': nsmap['opf'],
                          'unique-identifier': 'bookid'})


        tree.extend([writeOPF_metadata(),
                     writeOPF_manifest(),
                     writeOPF_spine()]
                     )
        #FIXME: check if guide section should be written
        if self.cover_img_path:
            tree.append(E.guide(
                E.reference(dict(type='cover', href=self.cover_img_path)
                )))
        xml = etree.tostring(tree, method='xml', encoding='utf-8',pretty_print=True, xml_declaration=True)
        self.add_file(config.opf_fn, xml)

    def addArticle(self, webpage):
        path = 'OPS/%s.xhtml' % webpage.id
        self.add_file(path, webpage.xml)
        self.articles.append(ArticleInfo(id=safe_xml_id(webpage.id),
                                         path=os.path.basename(path),
                                         title=webpage.title,
                                         type='article' if isinstance(webpage, collection.WebPage) else 'chapter'))

        if getattr(webpage, 'tree', False) != False:
            used_images = [src[len(config.img_rel_path):] for src in webpage.tree.xpath('//img/@src')]
        else:
            used_images = []

        if getattr(webpage, 'images', False) != False:
            for img_src, img_fn in webpage.images.items():
                basename = os.path.basename(img_fn)
                if basename not in used_images:
                    continue
                zip_fn = os.path.join(config.img_abs_path, basename)
                self.link_file(img_fn, zip_fn, compression=False)

    def addCover(self, xml, cover_img_path):
        path = 'OPS/cover.html'
        self.add_file(path, xml)
        self.articles.append(ArticleInfo(id='cover',
                                         path=os.path.basename(path),
                                         title='cover',
                                         type='cover',
                                         ))

        zip_fn = os.path.join(config.img_abs_path, 'cover'+ os.path.splitext(cover_img_path)[1])
        self.link_file(cover_img_path, zip_fn, compression=False)
        self.cover_img_path = zip_fn[4:] if zip_fn.startswith('OPS/') else zip_fn


class EpubWriter(object):

    def __init__(self, output, coll, status_callback=None, cover_img=None):
        self.output = output
        self.target_dir = os.path.dirname(output)
        self.coll = coll
        self.scaled_images = {}
        self.status_callback = status_callback
        self.cover_img = cover_img

    def initContainer(self):
        if not os.path.exists(self.target_dir):
            print 'created dir'
            os.makedirs(self.target_dir)
        self.container = EpubContainer(self.output, self.coll)
        self.container.link_file(os.path.join(os.path.dirname(__file__), 'wp.css'),
                                 'OPS/wp.css')

    def closeContainer(self):
        self.container.close()

    def renderColl(self, dump_xhtml=False):
        xhtml = None
        self.initContainer()
        self.processCoverImage()
        self.processTitlePage()
        progress_inc = 100.0/len(self.coll.outline.items)
        for n, (lvl, webpage) in enumerate(self.coll.outline.walk()):
            if isinstance(webpage, collection.WebPage):
                xhtml = self.processWebpage(webpage, dump_xhtml=dump_xhtml)
            elif isinstance(webpage, collection.Chapter):
                self.processChapter(webpage)
            if self.status_callback:
                self.status_callback(progress=n*progress_inc)
        self.processMetaInfo()
        self.closeContainer()
        if dump_xhtml:
            return xhtml

    def processCoverImage(self):
        if not self.cover_img:
            return
        content = [E.div(dict(style='width:100%;height:100%;'),
                         E.img(dict(src='images/' + 'cover'+ os.path.splitext(self.cover_img)[1],
                                    alt='',
                                    #width='100%',
                                    height='100%',
                                    style='max-height:100%;max-width:100%;margin:auto;',
                                    ))),
                   ]
        xml = misc.xhtml_page(title='cover',
                               body_content=content,
                               flatten=True)
        self.container.addCover(xml, os.path.abspath(self.cover_img))


    def processTitlePage(self):
        if not any(txt != '' for txt in [self.coll.title,
                                         self.coll.subtitle,
                                         self.coll.editor]):
            return
        titlepage = collection.Chapter(self.coll.title)
        titlepage.id = 'titlepage'
        body_content = [E.h1(self.coll.title,
                             style="margin-top:20%;font-size:200%;text-align:center;"),
                        E.h2(self.coll.subtitle,
                             style="margin-top:1em;font-size:150%;text-align:center;"),
                        E.h3(self.coll.editor,
                             style="margin-top:1em;font-size:100%;text-align:center;"),
                        ]
        if any('wikipedia.org' in url for url in self.coll.url2webpage):
            img_src = 'wikipedia_logo.jpg'
            titlepage.images = {img_src:
                                os.path.join(os.path.dirname(__file__), img_src)}
            body_content.append(E.div(E.img(src='images/'+img_src,
                                            width='50%', alt='',
                                            ),
                                      style='text-align:center;margin-top:4em;'
                                      ))
        tree = misc.xhtml_page(title=self.coll.title,
                               body_content=body_content,
                               flatten=False)
        titlepage.tree = tree
        titlepage.xml = misc.flatten_tree(tree)
        self.container.addArticle(titlepage)

    def processMetaInfo(self):
        from mwlib.epub import metainfo
        chapter = collection.Chapter(_('Article Sources and Contributors'))
        chapter.id = '_articlesources'
        chapter.xml = metainfo.getArticleMetainfo(chapter, self.coll)
        self.container.addArticle(chapter)

        chapter = collection.Chapter(_('Image Sources, Licenses and Contributors'))
        chapter.id = '_imagesources'
        chapter.xml = metainfo.getImageMetainfo(chapter, self.coll)
        self.container.addArticle(chapter)

    def processChapter(self, chapter):
        self.num_chapters = getattr(self, 'num_chapters', 0) + 1
        chapter.id = 'chapter_%02d' % self.num_chapters
        title = xmlescape(chapter.title)
        chapter.xml = misc.xhtml_page(
            title=title,
            body_content=[E.h1({'style':
                                'margin-top:15%;font-size:200%;text-align:center;'},
                               title)]
            )
        self.container.addArticle(chapter)


    def processWebpage(self, webpage, dump_xhtml=False):
        if not hasattr(webpage, 'tree'):
            webpage.tree = webpage._get_parse_tree()
        from copy import copy
        self.remapLinks(webpage)
        self.tree_processor = TreeProcessor()
        #self.tree_processor.getMetaInfo(webpage)
        self.tree_processor.annotateNodes(webpage)
        self.tree_processor.clean(webpage)
        webpage.xml = self.serializeArticle(copy(webpage.tree))
        self.container.addArticle(webpage)
        if dump_xhtml:
            return webpage.xml
        del webpage.tree
        del webpage.xml

    def remapLinks(self, webpage):
        for img in webpage.tree.findall('.//img'):
            img_fn = webpage.images.get(img.attrib['src'])
            if img_fn:
                zip_rel_path = os.path.join(config.img_rel_path, os.path.basename(img_fn))
                img.attrib['src'] = zip_rel_path
            else:
                remove_node(img)

        target_ids = [safe_xml_id(_id) for _id in webpage.tree.xpath('.//@id')]
        for a in webpage.tree.findall('.//a'):
            href = a.get('href')
            if not href: # this link is probably just an anchor
                continue
            if href.startswith('#'):
                target_id = safe_xml_id(href)[1:]
                if target_id not in target_ids:
                    a.set('id', target_id)
                    target_ids.append(target_id)
                a.set('href', '#'+target_id)
            else:
                url = clean_url(urlparse.urljoin(webpage.url, href))
                linked_wp = webpage.coll.url2webpage.get(url)
                if linked_wp:
                    a.set('href', linked_wp.id + '.xhtml')
                else:
                    a.set('href', url)

    def serializeArticle(self, node):
        assert not node.find('.//body'), 'error: node contains BODY tag'

        html = E.html({'xmlns':"http://www.w3.org/1999/xhtml"},
                      E.head(E.meta({'http-equiv':"Content-Type",
                                     'content': "application/xhtml+xml; charset=utf-8"})
                             ),
                      )

        head = html.find('.//head')
        node_head = node.find('.//head')
        for head_content in node_head.iterchildren():
            head.append(head_content)
        node_head.getparent().remove(node_head)

        body = E.body()
        html.append(body)
        body.extend(node)

        return misc.flatten_tree(html)

def render_fragment(epub_fn, fragment, dump_xhtml=False):
    collection_dir = os.path.dirname(epub_fn)
    coll = collection.collection_from_html_frag(fragment, collection_dir)
    epub = EpubWriter(epub_fn, coll)
    xhtml = epub.renderColl(dump_xhtml=dump_xhtml)
    return xhtml

def writer(env, output,
           status_callback=None,
           validate=False,
           dump_xhtml=False,
           cover_img=None,
           ):
    if status_callback:
        image_scaling_status = status_callback.getSubRange(1, 65)
        image_scaling_status(status='scaling images')
        rendering_status = status_callback.getSubRange(66, 100)

    tmpdir = tempfile.mkdtemp()
    zipfn = env
    coll = collection.coll_from_zip(tmpdir, zipfn, status_callback=image_scaling_status)
    rendering_status(status='generating epubfile')
    epub = EpubWriter(output, coll, status_callback=rendering_status, cover_img=cover_img)
    epub.renderColl(dump_xhtml=dump_xhtml)
    # import cProfile
    # cProfile.runctx('epub.renderColl(dump_xhtml=dump_xhtml)',globals(), locals(), 'profile')
    shutil.rmtree(tmpdir)

    if validate:
        import subprocess
        cmd = ['epubcheck', output]
        cmd = 'epubcheck {0}'.format(output)
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        try:
            stdout, stderr = p.communicate()
            ret = p.returncode
        except OSError, e:
            print 'WARNING: epubcheck not found - epub not validated'
            print 'ERROR', e
        else:
            print 'VALIDATING EPUB'
            print 'validation result:', ret
            print stdout
            print stderr

writer.description = 'epub Files'
writer.content_type = 'application/epub+zip'
writer.file_extension = 'epub'
writer.options = {
    'dump_xhtml': {
        'help': 'Debugging flag - when set output generated xhtml of all articles',
        },
    'cover_img': {
        'param': 'FILENAME',
        'help': 'filename of an image for the cover page',
        },
    }
