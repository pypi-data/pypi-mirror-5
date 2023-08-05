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
"""

from nive.i18n import _
from nive.definitions import IPage
from nive.definitions import IToolboxWidgetConf, IEditorWidgetConf
from nive.definitions import ViewModuleConf, ViewConf, WidgetConf
from nive.cms.cmsview.view import Editor


configuration = ViewModuleConf(
    id = "wfview",
    name = _(u"CMS workflow extension"),
    static = "nive.cms.workflow:static",
    permission = "read",
    context = IPage,
    containment = "nive.cms.cmsview.cmsroot.cmsroot",
    view = "nive.cms.workflow.view.WorkflowEdit"
)

configuration.views = [
    ViewConf(name = "wfWidget", attr = "widget",   renderer = "nive.cms.workflow:templates/widget.pt"),
    ViewConf(name = "workflow", attr = "workflow", renderer = "nive.cms.workflow:templates/editorpage.pt"),
    ViewConf(name = "action",   attr = "action"),
    ViewConf(name = "pubr",     attr = "publishRecursive", permission = "edit")
]

configuration.widgets = [
    WidgetConf(name=_("Workflow"), widgetType=IToolboxWidgetConf, apply=(IPage,), viewmapper="wfWidget", id="cms.wf",    sort=250),
    WidgetConf(name=_("Workflow"), widgetType=IEditorWidgetConf,  apply=(IPage,), viewmapper="workflow", id="editor.wf", sort=250)
]


class WorkflowEdit(Editor):

    def widget(self):
        wf = self.context.GetWfInfo(self.User())
        return {u"wf": wf}   
    
    def workflow(self):
        wf = self.context.GetWfInfo(self.User())
        return {u"wf": wf,u"content": u"", u"result": True, u"cmsview":self, u"head": u""}

    def action(self):
        transition = self.GetFormValue(u"t")
        url = self.GetFormValue("redirect_url")
        if not url:
            url = self.PageUrl()
            
        user = self.User()
        self.context.WfAction("", user, transition=transition)
        self.context.CommitInternal(user)
        msg = _(u"OK")
        self.Redirect(url, messages=[msg])
        
    def publishRecursive(self):
        msgs = []
        ok = 0
        user = self.User()
        
        def recursive(self, page, ok):
            for p in page.GetPages(includeMenu=1):
                if not p.meta.pool_state:
                    try:
                        p.WfAction("publish", user)
                        p.CommitInternal(user)
                        msgs.append("Published: " + p.meta.title)
                        ok += 1
                    except Exception, e:
                        msgs.append(u"Failure: "+str(e))
                        pass
                ok = recursive(self, p, ok)
            return ok
        
        ok = recursive(self, self.context, ok)
             
        url = self.GetFormValue("redirect_url")
        if not url:
            url = self.PageUrl()
        msgs.insert(0, "%d pages published!"%ok)
        self.Redirect(url, messages=msgs)
        
