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

import string

from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from nive.definitions import _
from nive.tools import Tool
from nive.helper import FakeLocalizer

from nive.utils.utils import ConvertToNumberList
from nive.utils.utils import ConvertHTMLToText
from nive.definitions import implements, Interface, ModuleConf, ToolConf, Conf 
from nive.definitions import IApplication, IPage, IRoot

class IFulltext(Interface):
    pass


class PageFulltext(object):
    """
    Fulltext support for cms pages. Automatically updates fulltext on commit. 
    """
    implements(IFulltext)

    def Init(self):
        self.ListenEvent("commit", "UpdateFulltext")
        

    # Fulltext ------------------------------------------

    def UpdateFulltext(self):
        """
        Update fulltext for entry. Text is generated automatically.
        """
        if not self.app.configuration.fulltextIndex:
            return
        if IPage.providedBy(self):
            # get text from contained elements
            text = [self.GetTexts()]
            for e in self.GetPageElements(addBoxContents=1, addColumnContents=1):
                text.append(e.GetTexts())
            self.dbEntry.WriteFulltext(self.FormatFulltext(text))
        elif IPage.providedBy(self) or IRoot.providedBy(self):
            # get text from contained elements
            text = []
            for e in self.GetPageElements(addBoxContents=1, addColumnContents=1):
                text.append(e.GetTexts())
            #!fulltext storage root
            #self.dbEntry.WriteFulltext(self.FormatFulltext(text))
        else:
            self.GetPage().UpdateFulltext()
            
    def FormatFulltext(self, textlist):
        # formats the raw text better display
        text = u"\n".join(textlist)
        text = text.replace(u"\n\n\n", u"\n")
        text = text.replace(u"\n\n", u"\n")
        return text

    def GetTexts(self):
        # loop all fulltext fields and make one string
        text = []
        root = self.root()
        for f in self.app.GetAllMetaFlds(ignoreSystem=False):
            if f.get("fulltext") != True:
                continue
            #print inUnit.GetID(),f
            if f["datatype"]=="unit":
                id = self.meta.get(f["id"])
                t = root.LookupObjTitle(id)
                if t:
                    text.append(t)
            elif f["datatype"]=="unitlist":
                ids = ConvertToNumberList(self.meta.get(f["id"]))
                for id in ids:
                    t = root.LookupObjTitle(id)
                    if t:
                        text.append(t)
            else:
                t = self.meta.get(f["id"],u"")
                if t:
                    text.append(ConvertHTMLToText(t, url="", removeReST=True))

        # data
        for f in self.configuration.data:
            if f.get("fulltext") != True:
                continue
            if f["datatype"]=="unit":
                id = self.data.get(f["id"])
                t = root.LookupObjTitle(id)
                if t:
                    text.append(t)
            elif f["datatype"]=="unitlist":
                ids = ConvertToNumberList(self.data.get(f["id"]))
                for id in ids:
                    t = root.LookupObjTitle(id)
                    if t:
                        text.append(t)
            else:
                t = self.data.get(f["id"],u"")
                if t:
                    text.append(ConvertHTMLToText(t, url="", removeReST=True))
        return u"\n\n".join(text)


    def GetFulltext(self):
        """
        Get current fulltext value
        """
        if not self.app.configuration.fulltextIndex:
            return u""
        return self.dbEntry.GetFulltext()

    
    def DeleteFulltext(self):
        """
        Delete fulltext
        """
        if not self.app.configuration.fulltextIndex:
            return
        self.dbEntry.DeleteFulltext()


class RewriteFulltext(Tool):

    def _Run(self, **values):

        try:
            localizer = get_localizer(get_current_request())
        except:
            localizer = FakeLocalizer()

        app = self.app
        root = app.root()
        datapool = app.db
        conn = datapool.connection
        c = conn.cursor()

        # delete
        sql = u"delete from pool_fulltext"
        c.execute(sql)
        c.close()
        conn.commit()
        self.stream.write(localizer.translate(_(u"Deleted previous fulltext index.<br/>")))
        
        pages = root.Select(parameter={"pool_stag":10,"pool_state":1})
        cnt = len(pages)
        err = 0
        for page in pages:
            page = page[0]
            obj = root.LookupObj(page)
            if not obj:
                err += 1
                self.stream.write(localizer.translate(_(u"Error: Unable to open page (${id}).<br/>", mapping={"id":page})))
            else:
                try:
                    obj.UpdateFulltext()
                except Exception, e:
                    err += 1
                    self.stream.write(localizer.translate(_(u"Error: Unable to update page (${id}).<br/>", mapping={"id":page})))
                    self.stream.write(unicode(e))
                    self.stream.write(u"<br/><br/>")
        conn.commit()
        self.stream.write(localizer.translate(_(u"Updated fulltext index. Finished.<br/>")))
        self.stream.write(localizer.translate(_(u"${cnt} pages ok. ${err} failed.<br/>", mapping={"cnt":cnt,"err":err})))
        return 1



def SetupFulltext(app, pyramidConfig):
    # get all objects and add extension
    extension = "nive.components.extensions.fulltextpage.PageFulltext"
    def add(confs):
        for c in confs:
            e = c.extensions
            if e == None:
                e = []
            elif extension in e:
                continue
            if isinstance(e, tuple):
                e = list(e)
            e.append(extension)
            c.unlock()
            c.extensions = tuple(e)
            c.lock()
    
    add(app.GetAllRootConfs())
    add(app.GetAllObjectConfs())


toolconf = ToolConf(
    id = "updatefulltext",
    context = "nive.components.extensions.fulltextpage.RewriteFulltext",
    name = _(u"Rewrite fulltext index"),
    description = _("Delete and rewrite the fulltext index."),
    apply = (IApplication,),
    data = [],
    mimetype = "text/html"
)

configuration = ModuleConf(
    id = "pagefulltext",
    name = u"Web page fulltext extension",
    context = PageFulltext,
    events = (Conf(event="startRegistration", callback=SetupFulltext),),
    modules = [toolconf]
)


