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
Administration interface extensions

"""

from pyramid.renderers import render

from nive.i18n import _
from nive.definitions import ViewConf, ViewModuleConf, FieldConf, WidgetConf, Conf
from nive.definitions import IApplication, IAdminWidgetConf   
from nive.adminview.view import AdminBasics, ConfigurationForm

# view module definition ------------------------------------------------------------------

#@nive_module
configuration = ViewModuleConf(
    id = "cms_admin",
    name = _(u"CMS Administration"),
    context = IApplication,
    view = "nive.cms.cmsview.admin.CMSAdminView",
    templates = "nive.adminview:",
    permission = "administration"
)

t = configuration.templates
configuration.views = [
    ViewConf(name = "design",   attr = "design",     renderer = t+"form.pt"),
    ViewConf(name = "help",     attr = "help",       renderer = t+"help.pt", permission="read"),
]

configuration.widgets = [
    WidgetConf(name=_(u"Design"), viewmapper="design", id="admin.design", sort=1500,   apply=(IApplication,), widgetType=IAdminWidgetConf,
               description=u""),
    WidgetConf(name=_(u"Help"),                 viewmapper="help",   id="admin.help",   sort=50000,  apply=(IApplication,), widgetType=IAdminWidgetConf,
               description=_(u"Help and documentation.")),
]




class CMSAdminView(AdminBasics):
    
    def doc(self, template=u"default.pt"):
        return render(u"nive.cms:doc/"+template, {u"context":self.context, u"view":self, u"request": self.request}, request=self.request)
    
    def design(self):
        fields = (
            FieldConf(id=u"columns", datatype="lines",  size=100,  required=0, name=_(u"Column names"), description=_(u"Column names used in the main template. For multiple columns enter one per line.")),
        )
        form = ConfigurationForm(view=self, context=self.context.configuration, app=self.context)
        form.fields = fields
        form.Setup() 
        # process and render the form.
        result, data, action = form.Process()
        return {u"content": data, u"result": result, u"head": form.HTMLHead()}
    
    def help(self):
        return {}
    

