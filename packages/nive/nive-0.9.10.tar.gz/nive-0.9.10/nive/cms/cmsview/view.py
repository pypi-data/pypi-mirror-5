#----------------------------------------------------------------------
# Copyright 2012, 2013 Arndt Droullier, Nive GmbH. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------

__doc__ = """
Nive cms toolbox and editor view layer
----------------------------------------
The view configuration includes a list of assets (javascript and css) needed to render the toolbox
and editor widgets. These are included in the design/main template in edit mode through `cmsview.Assets()`.
Asset definitions use a identifier and an asset path like: ::

    ('jquery.js', 'nive.cms.cmsview:static/mods/jquery.min.js'),
    ('toolbox.css', 'nive.cms.cmsview:static/toolbox/toolbox.css'),

If for example jquery is already included in the main page Assets() can be told to ignore certain
entries: ::

    cmsview.Assets(ignore=["jquery.js"])  

"""
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from pyramid.response import Response
from pyramid.renderers import get_renderer, render, render_to_response

    
from nive.i18n import _, translator
from nive.definitions import ViewModuleConf, ViewConf, WidgetConf, FieldConf
from nive.definitions import IContainer, IApplication, IPortal, IPage, IObject, IRoot
from nive.definitions import IToolboxWidgetConf, IEditorWidgetConf, IViewModuleConf, ICMSRoot, IColumn
from nive.utils.utils import SortConfigurationList
from nive.helper import ResolveName

from nive.forms import ObjectForm
from nive.views import BaseView

from nive.cms.cmsview import cutcopy
from nive.cms.cmsview import sort



# view module definition ------------------------------------------------------------------

#@nive_module
configuration = ViewModuleConf(
    id = "editor",
    name = u"CMS Editor",
    static = "nive.cms.cmsview:static",
    templates = "nive.cms.cmsview:",
    permission = "read",
    context = IObject,
    containment = ICMSRoot,  
    view = "nive.cms.cmsview.view.Editor",
    assets = [
        # jquery and jquery-ui
        ('jquery.js', 'nive.cms.cmsview:static/mods/jquery.min.js'),
        ('jquery-ui.js', 'nive.cms.cmsview:static/mods/ui/jquery-ui-1.8.24.custom.min.js'),
        # nive specific
        ('cmseditor.js', 'nive.cms.cmsview:static/cmseditor.js'),
        ('toolbox.css', 'nive.cms.cmsview:static/toolbox/toolbox.css'),
        ('overlay.css', 'nive.cms.cmsview:static/overlay/overlay.css'),
        ('cmseditor.css', 'nive.cms.cmsview:static/cmseditor.css'),
    ],
    description=__doc__
)

# views -----------------------------------------------------------------------------
# copy and sort extension views are imported from their files and added at the end of the list

t = configuration.templates 
configuration.views = [
    ViewConf(name="editor",     attr="editor",  context=IContainer,   permission="read", containment=IApplication),
    ViewConf(name="exiteditor", attr="exit",    context=IContainer,   permission="view", containment=IApplication),
    ViewConf(name="exiteditor", attr="exitapp", context=IApplication, permission="view", containment=IPortal),
    
    #ViewConf(id="rootview", name = "",     attr = "view", context = ICMSRoot, containment=IApplication),
    #ViewConf(id="objview",  name = "",     attr = "view", context = IPage),
    
    # object
    ViewConf(name="edit", attr="edit", renderer=t+"edit.pt", permission="edit"),
    ViewConf(name="meta", attr="meta", renderer=t+"meta.pt"),
    ViewConf(name="delfile", attr="delfile", permission="delete"),
                
    # widgets
    ViewConf(name = "elementListWidget", attr = "elementListWidget", context = IContainer, permission="edit"),
    ViewConf(name = "elementAddWidget",  attr = "elementAddWidget",  context = IObject, permission = "add"),
    ViewConf(name = "elementAddWidget",  attr = "elementAddWidget",  context = IRoot, permission = "add"),
    ViewConf(name = "editblock",         attr = "editBlockElement",  context = IObject, permission = "edit"),
    
    # container
    ViewConf(name = "add",       attr = "add",    context = IContainer, renderer = t+"add.pt", permission="add"),
    ViewConf(name = "delete",    attr = "delete", context = IContainer, renderer = t+"delete.pt", permission = "delete"),
    
    # widgets
    ViewConf(name = "addpageWidget",  attr = "tmpl", renderer = t+"widgets/widget_addpage.pt",    context = IContainer, permission="add"),
    ViewConf(name = "editpageWidget", attr = "tmpl", renderer = t+"widgets/widget_editpage.pt",   context = IContainer, permission="edit"),
    ViewConf(name = "subpagesWidget", attr = "tmpl", renderer = t+"widgets/widget_subpages.pt",   context = IContainer),
    ViewConf(name = "settingsWidget", attr = "tmpl", renderer = t+"widgets/widget_settings.pt",   context = IContainer)
] + sort.views + cutcopy.views


# toolbox and editor widgets ----------------------------------------------------------------------------------
configuration.widgets = [
    WidgetConf(name=_(u"Add new page"),         widgetType=IToolboxWidgetConf, apply=(IContainer,), viewmapper="addpageWidget", id="cms.addpage", sort=100),
    WidgetConf(name=_(u"Edit page"),            widgetType=IToolboxWidgetConf, apply=(IContainer,), viewmapper="editpageWidget", id="cms.editpage", sort=200),
    WidgetConf(name=_(u"Sub pages and parent"), widgetType=IToolboxWidgetConf, apply=(IContainer,), viewmapper="subpagesWidget", id="cms.subpages", sort=300),
    WidgetConf(name=_(u"Settings"),             widgetType=IToolboxWidgetConf, apply=(IApplication,IContainer), viewmapper="settingsWidget", id="cms.settings", sort=400),
    
    WidgetConf(name=_(u"Edit"),          widgetType=IEditorWidgetConf, apply=(IObject,),    viewmapper="edit",   id="editor.edit", sort=100),
    WidgetConf(name=_(u"Add"),           widgetType=IEditorWidgetConf, apply=(IContainer,), viewmapper="add",    id="editor.add",  sort=200),
    WidgetConf(name=_(u"Sort sub pages"),widgetType=IEditorWidgetConf, apply=(IPage,),      viewmapper="sortpages", id="editor.sortpages", sort=300),
    WidgetConf(name=_(u"Meta"),          widgetType=IEditorWidgetConf, apply=(IObject,),    viewmapper="meta",   id="editor.meta", sort=400)
]


        
        
# view implementation ------------------------------------------------------------------
        

class Editor(BaseView, cutcopy.CopyView, sort.SortView):

    def __init__(self, context, request):
        BaseView.__init__(self, context, request)
        request.editmode = "editmode"

    def IsEditmode(self):
        return True
        
    def GetEditorWidgets(self, object):
        app = self.context.app
        widgets = app.QueryConf(IEditorWidgetConf, context=object)
        confs = []
        if not widgets:
            return confs
        #opt
        for n,w in widgets:
            confs.append(w)
        return SortConfigurationList(confs, u"sort")
        
    def Assets(self, assets=None, ignore=None):
        """
        Renders a list of static ressources as html <script> and <link>.
        If assets is None the list of assets is looked up in the 'cmsview'-configuration.
        Asset definitions use a identifier and an asset path like: ::
        
            ('jquery.js', 'nive.cms.cmsview:static/mods/jquery.min.js'),
            ('toolbox.css', 'nive.cms.cmsview:static/toolbox/toolbox.css'),
        
        If for example jquery is already included in the main page Assets() can be told to ignore certain
        entries: ::
        
            cmsview.Assets(ignore=["jquery.js"])  
        
        """
        if not assets:
            app = self.context.app
            conf = app.QueryConfByName(IViewModuleConf, "editor")
            if not conf:
                return u""
            assets = conf.assets

        if not assets:
            return u""
        
        if ignore==None:
            ignore = []

        js_links = [self.StaticUrl(r[1]) for r in filter(lambda v: v[0] not in ignore and v[1].endswith(u".js"), assets)]
        css_links = [self.StaticUrl(r[1]) for r in filter(lambda v: v[0] not in ignore and v[1].endswith(u".css"), assets)]
        js_tags = [u'<script src="%s" type="text/javascript"></script>' % link for link in js_links]
        css_tags = [u'<link href="%s" rel="stylesheet" type="text/css" media="all"/>' % link for link in css_links]
        return (u"\r\n").join(js_tags + css_tags)        
        
    # macros ------------------------------------------------------------------------ 

    def cmsIndex_tmpl(self):
        i = get_renderer('nive.cms.cmsview:index.pt').implementation()
        return i
    
    # redirects ------------------------------------------------------------------------ 

    def editor(self):
        # switch to editor mode
        root = self.context.app.root("editor")
        url = self.FolderUrl(root)
        if not self.context.IsRoot():
            url = url + self.PageUrl(self.context)[len(self.FolderUrl(self.context.GetRoot())):]
        self.Redirect(url)
    
    def exit(self):
        # leave editor mode
        root = self.context.app.root()
        url = self.FolderUrl(root)
        if not self.context.IsRoot():
            url = url + self.PageUrl(self.context)[len(self.FolderUrl(self.context.root())):]
        self.Redirect(url)

    def exitapp(self):
        # leave editor mode in application context
        root = self.context.root()
        url = self.FolderUrl(root)
        self.Redirect(url)
    
    
    # cms editor interface elements -------------------------------------------------
    
    def cms(self, obj=None):
        """
        Renders required widgets and toolbar
        
        Calls
        - self.cmsToolbox() 
        - self.cmsEditorBlocks()
        - self.cmsEditorBlocks() for each column
        """
        if not obj:
            obj=self.context
        html = [self.cmsToolbox(obj), self.cmsEditorBlocks(obj)]
        for column in obj.app.configuration.columns:
            html.append(self.cmsEditorBlocks(obj.page.GetColumn(column)))
        return u"".join(html)

    
    def cmsToolbox(self, obj, elements=None):
        """
        nive toolbox widget.
        call with obj = current object / page
        """
        if not obj:
            obj = self.context
        return render("widgets/toolbox.pt", {u"obj":obj, u"view":self, u"elements": elements}, request=self.request)

    
    def cmsEditorBlocks(self, obj, elements=None):
        """
        Renders javascript needed to load editblocks of page elements. Editblocks are loaded on click.  
        call with obj = current container / page
        """
        if not obj:
            return u""
        js = u"""<script>$(document).ready(function(){ \n%(js)s });</script>"""
        attr = u""" $("#nive-element%(id)s").click(function() { $.fn.editblocks().clickAndLoadElement('%(id)s','%(path)s',arguments[0] || window.event); });\n"""
        newjs = StringIO()
        html = StringIO()
        
        if not elements:
            elements = obj.GetPageElements()
        
        for el in elements:
            if el.GetTypeID()=='box':
                newjs.write(attr % {u"id": unicode(el.GetID()), u"path": self.FolderUrl(el)})
                for elb in el.GetPageElements():
                    newjs.write(attr % {u"id": unicode(elb.GetID()), u"path": self.FolderUrl(elb)})
            else:
                newjs.write(attr % {u"id": unicode(el.GetID()), u"path": self.FolderUrl(el)})
        
        html.write(js % {u"js": newjs.getvalue()})
        return html.getvalue()


    def cmsEditorBlocksPrerender(self, obj, elements=None):
        """
        Renders javascript needed to load editblocks of page elements. Editblocks are rendered directly into the page.  
        call with obj = current container / page
        """
        if not obj:
            return u""
        js = u"""<script>$(document).ready(function(){ %(js)s });</script>"""
        #dbl click: attr = u""" $("#nive-element%(id)s").attr({ondblclick:"$.fn.editblocks().dblClickElement('%(id)s',event)", onclick:"$.fn.editblocks().clickElement('%(id)s',event)"});\n"""
        attr = u""" $("#nive-element%(id)s").click(function() { $.fn.editblocks().clickElement('%(id)s',arguments[0] || window.event); });\n"""
        insert = u""" $("#nive-editblock%(id)s").prependTo("#nive-element%(id)s");\n"""
        newjs = StringIO()
        html = StringIO()
        
        if not elements:
            elements = obj.GetPageElements()
        
        for el in elements:
            if el.GetTypeID()=='box':
                html.write(self.editBlockElement(obj=el, addResponse=False))
                newjs.write(insert % {u"id": unicode(el.GetID())})
                newjs.write(attr % {u"id": unicode(el.GetID())})
                for elb in el.GetPageElements():
                    html.write(self.editBlockElement(obj=elb, addResponse=False))
                    newjs.write(insert % {u"id": unicode(elb.GetID())})
                    newjs.write(attr % {u"id": unicode(elb.GetID())})
        
            else:
                html.write(self.editBlockElement(obj=el, addResponse=False))
                newjs.write(insert % {u"id": unicode(el.GetID())})
                newjs.write(attr % {u"id": unicode(el.GetID())})
        
        html.write(js % {u"js": newjs.getvalue()})
        return html.getvalue()


    def editBlockPage(self, page=None):
        """
        Edit bar for page main content area or columns
        if page is None current context is used
        """
        if not page:
            page=self.context
        return render("widgets/editblock_page.pt", {u"obj":page, u"view":self}, request=self.request)

    
    def editBlockElement(self, obj=None, addResponse=True):
        """
        Edit bar for elements
        if obj is None current context is used
        """
        if not obj:
            obj=self.context
        data = render("widgets/editblock_element.pt", {u"obj":obj, u"view":self}, request=self.request)
        if addResponse:
            r = Response(content_type="text/html", conditional_response=True)
            r.unicode_body = data
            return r
        return data


    def editBlockColumn(self, name=None, page=None, column=None):
        """
        Edit bar for columns
        if column is None the current context is used
        """
        if not page:
            page = self.context.page
        if not column:
            column=self.context
            if not IColumn.providedBy(column):
                if name:
                    column = page.GetColumn(name)
        if column != None:
            name = column.meta.get("title")
        return render("widgets/editblock_column.pt", 
                      {u"column":column, u"page": page, u"name": name, u"view":self}, 
                      request=self.request)

    
    def editBlockList(self, obj=None, page=None, showCCP=False):
        """
        Edit bar used in lists
        call with obj = current object / page
        """
        if not obj:
            obj=self.context
        if not page:
            page = obj.GetPage()
            elementContainer = obj.GetElementContainer()
        else:
            elementContainer = page
        return render("widgets/editblock_list.pt", 
                      {u"obj":obj, u"page": page, u"elementContainer": elementContainer, u"view":self, u"showCCP":showCCP}, 
                      request=self.request)

    
    def elementAddWidget(self, obj=None, addResponse=True):
        """
        Widget with links to add elements as subobjects of obj
        call with obj = current object / element
        """
        if not obj:
            obj=self.context
        if addResponse:
            return render_to_response("widgets/element_add_list.pt", {"obj":obj, "view":self}, request=self.request)
        return render("widgets/element_add_list.pt", {u"obj":obj, u"view":self}, request=self.request)


    def elementListWidget(self, obj=None, elements=None, addResponse=True):
        """
        Widget with existing elements list and edit options
        call with obj = current object / page
        """
        #i18n?
        if not obj:
            obj=self.context
        html = u"""<div>
  <h4 onclick="$.fn.editblocks().toggleBlock('#elements%(id)s',event)">%(title)s</h4>
  %(blocks)s
</div>
        """
        
        elHtml = u"""<div class="element">
  <div class="el_title">%(title)s</div>
  <div class="el_options">%(options)s</div>
  <br style="clear:both"/>
</div>"""
        
        if not elements:
            elements = obj.GetPageElements()
            
        localizer = translator(self.request)
        
        blocks = StringIO()
        static = self.StaticUrl("nive.cms.cmsview:static/images/types/")
        for el in elements:
        
            t = el.GetTitle()
            if not t:
                t = u"<em>%s</em>" % (localizer(el.GetTypeName(), self.request))

            if el.GetTypeID()=="box":
                title = u"<img src='%s%s.png' align='top'/> %s: %s" % (static, el.GetTypeID(), localizer(u"Box"), t)
                blocks.write(elHtml % {u"title": title, u"options": self.editBlockList(obj=el, showCCP=True)})
                for elb in el.GetPageElements():
                    t = elb.GetTitle()
                    if not t:
                        t = u"<em>%s</em>" % (localizer(elb.GetTypeName()))
                    title = u"&gt; <img src='%s%s.png' align='top'/> %s" % (static, elb.GetTypeID(), t)
                    blocks.write(elHtml % {u"title": title, u"options": self.editBlockList(obj=elb, showCCP=True)})
        
            else:
                title = u"<img src='%s%s.png' align='top'/> %s" % (static, el.GetTypeID(), t)
                blocks.write(elHtml % {u"title": title, u"options": self.editBlockList(obj=el, showCCP=True)})
        if not len(elements):
            blocks.write(localizer(_(u"<p><i>empty</i></p>")))
        data = html % {u"blocks": blocks.getvalue(), u"id": str(obj.GetID()), u"title": localizer(_(u"Page elements"))}
        if addResponse:
            r = Response(content_type="text/html", conditional_response=True)
            r.unicode_body = data
            return r
        return data
        

    def pageListWidget(self, page=None, pages=None):
        """
        Widget with existing pages list and edit options
        call with page = current page
        """
        if not page:
            page=self.context
        html = u"""<div class="subpages"> %(blocks)s </div>"""
        
        pHtml = u"""<div class="element">
  <div class="el_title">%(workflow)s<a href="%(url)s">%(title)s </a> </div>
  <div class="el_options">%(options)s</div>
  <br style="clear:both"/>
</div>"""
        
        useworkflow = 1
        localizer = translator(self.request)
        static = self.StaticUrl("nive.cms.workflow:static/exclamation.png")

        if not pages:
            pages = page.GetPages(includeMenu=1)
        blocks = StringIO()
        for p in pages:
            wf = u""
            if useworkflow and not p.meta.pool_state:
                wf = u"""<a href="%(url)sworkflow" class="right" rel="niveOverlay"><img src="%(static)s" title="%(name)s"/></a>""" % {
                                    u"static": static, 
                                    u"url": self.FolderUrl(p), 
                                    u"name": localizer(_(u"This page is not public."))
                                }
            title = p.meta.get(u"title")
            options = self.editBlockList(obj=p, page=page)
            blocks.write(pHtml % {u"url": self.FolderUrl(p), u"title": title, u"options": options, u"workflow": wf})
        if not len(pages):
            blocks.write(localizer(_(u"<p><i>no sub pages</i></p>")))
        return html % {u"blocks": blocks.getvalue()}
        

    def breadcrumbs(self, addHome=0, link=True):
        """
        """
        base = self.context #.GetPage()
        parents = base.GetParents()
        parents.reverse()
        if not addHome:
            parents = parents[1:]
        if len(parents)==0:
            return u""
        html = StringIO()
        for page in parents:
            if not link:
                html.write(u"""<span>%s</span> &gt; """ % (page.GetTitle()))
            else:
                html.write(u"""<a href="%s" class="nivecms">%s</a> &gt; """ % (self.PageUrl(page), page.GetTitle()))
        if not link:
            html.write(u"""<span>%s</span>""" % (base.GetTitle()))
        else:
            html.write(u"""<a href="%s" class="nivecms">%s</a>""" % (self.PageUrl(base), base.GetTitle()))
        return html.getvalue()
    
    
    def insertMessages(self):
        messages = self.request.session.pop_flash("")
        if not messages:
            return u""
        html = u"""<div class="alert"> <a href="#" class="close" data-dismiss="alert">&times;</a> <ul><li>%s</li></ul></div>"""
        try:
            return html % (u"</li><li>".join(messages))
        except:
            return u""
        
    def insertPageWidgets(self):
        return self.insertToolboxWidgets(self.context.GetPage())
        
    def insertAppWidgets(self):
        return self.insertToolboxWidgets(self.context.app)

    def insertToolboxWidgets(self, object):
        app = self.context.app
        widgets = app.QueryConf(IToolboxWidgetConf, context=object)
        html = u""
        if not widgets:
            return html
        l = []
        #opt
        for n,w in widgets:
            l.append({u"id":w.sort, u"data": self.RenderView(object, name=w.viewmapper, secure=True, raiseUnauthorized=False)})
        for i in SortConfigurationList(l, u"id"):
            if i[u"data"]:
                html += i[u"data"]
        return html


    # add list widgets -------------------------------------------------------------------

    def selectType(self):
        user = self.User()
        lt = self.context.GetAllowedTypes(user)
        tmpl = u"""<a href="add?pool_type=%s" rel="niveOverlay" class="nivecms addlink">%s</a> """
        html = StringIO()
        html.write(u"""<div class="addElements">""")
        #opt
        for t in lt:
            html.write(tmpl % (t[u"id"], _(t[u"name"])))
        html.write(u"</div>")
        return html.getvalue()
    
    def selectPageElement(self):
        user = self.User()
        lt = self.context.GetAllowedTypes(user)
        tmpl = u"""<a href="add?pool_type=%s" rel="niveOverlay" class="nivecms addlink">%s</a> """
        html = StringIO()
        html.write(u"""<div class="addElements">""")
        #opt
        for t in lt:
            html.write(tmpl % (t[u"id"], _(t[u"name"])))
        html.write(u"</div>")
        return html.getvalue()
    


    # template rendering -----------------------------------------------------------------------
    
    @property
    def editorview(self):
        return self
    
    @property
    def designview(self):
        """
        Tries to load the editor view class. If none is registered the function 
        will simply return None. Otherwise the editor view class instance with 
        context and request set.
        """
        if hasattr(self, "_c_design"):
            return self._c_design
        module = self.context.app.QueryConfByName(IViewModuleConf, "design")
        if not module:
            return None
        cls =  ResolveName(module.view)
        design = cls(self.context, self.request)
        self._c_design = design
        return design
        
    
    def add(self):
        typeID = self.GetFormValue("pool_type")
        if not typeID:
            return {u"content": u"", u"showAddLinks": True, u"result": True, u"head": u""}
        form = ObjectForm(view=self, loadFromType=typeID)
        form.Setup(subset="create", addTypeField=True)
        form.use_ajax = True
        head = form.HTMLHead()
        result, data, action = form.Process(redirectSuccess="page_url")
        return {u"content": data, u"result": result, u"cmsview": self, u"showAddLinks": False, u"head": head}

    
    def delete(self):
        id = self.GetFormValue(u"id")
        result = {u"msgs": [], u"objToDelete": None, u"content":u"", u"cmsview": self, u"result": False}
        if not id:
            result[u"msgs"] = [_(u"Nothing to delete")]
            return result
        delete = self.GetFormValue(u"delete")
        obj = self.context.obj(id)
        if not obj:
            result[u"msgs"] = [_(u"Object not found")]
            return result
        if obj.IsContainer() and delete != u"1":
            result[u"objToDelete"] = obj
            return result
        result[u"result"] = self.context.Delete(id, user=self.User(), obj=obj)
        if result[u"result"]:
            result[u"msgs"] = [_(u"OK. Deleted.")]
        self.Relocate("""<script type="text/javascript">window.parent.close("%s");</script>""" % (self.PageUrl()), 
                      [_(u"OK. Deleted.")], 
                      raiseException=True)
        return result
    
    
    def edit(self):
        form = ObjectForm(view=self, loadFromType=self.context.configuration)
        form.use_ajax = True
        form.Setup(subset="edit")
        head = form.HTMLHead()
        result, data, action = form.Process(redirectSuccess="page_url")
        return {u"content": data, u"result": result, u"cmsview":self, u"head": head}


    def delfile(self):
        file = self.GetFormValue(u"fid")
        try:
            r=self.context.DeleteFile(file, self.User())
            if not r:
                m=_(u"Delete failed")
            else:
                m=_(u"OK")
        except Exception, e:
            m=str(e)
        r = Response(content_type="text/html", conditional_response=True)
        r.text = """<span>%(msg)s</span>""" % {"name": str(file), "msg":m}
        return r


    def meta(self):
        return {}


    # bw 0.9.4 ----------------------------------------------------------------------------
    def cmsMain(self, obj, elements=None):
        return self.cmsToolbox(obj, elements=elements)