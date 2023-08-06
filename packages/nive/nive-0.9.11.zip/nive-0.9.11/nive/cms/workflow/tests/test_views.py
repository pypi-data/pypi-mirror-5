# -*- coding: utf-8 -*-

import time
import unittest

from nive.cms.tests.db_app import *

from nive.cms.cmsview.view import *
from nive.cms.workflow.view import WorkflowEdit
from nive.cms.workflow import wf

from pyramid import testing 
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render



class tWf(unittest.TestCase):

    def setUp(self):
        request = testing.DummyRequest()
        request._LOCALE_ = "en"
        self.config = testing.setUp(request=request)
        self.request = request
        self.app = app(["nive.cms.workflow.wf.wfProcess", "nive.cms.workflow.view"])
        self.app.Startup(self.config)
        self.root = self.app.root()
        user = User(u"test")
        user.groups.append("group:editor")
        self.page = create_page(self.root, user)
        self.request.context = self.page

    def tearDown(self):
        user = User(u"test")
        testing.tearDown()
        root = self.app.root()
        self.root.Delete(self.page.id, user=user)
        self.app.Close()


    def test_functions(self):
        user = User(u"test")
        user.groups.append("group:editor")
        wf.publish(None, self.page, user, {})
        self.assert_(self.page.meta.pool_state==1)
        wf.revoke(None, self.page, user, {})
        self.assert_(self.page.meta.pool_state==0)

    
    def test_views1(self):
        view = WorkflowEdit(self.page, self.request)
        self.assertRaises(HTTPFound, view.action)
        self.assertRaises(HTTPFound, view.publishRecursive)
        view.widget()
        view.workflow()
        
    
    def test_templates(self):
        user = User(u"test")
        user.groups.append("group:editor")
        view = WorkflowEdit(self.page, self.request)
        vrender = {"context":self.page, "view":view, "request": self.request, "cmsview":view}
        values = view.widget()
        values.update(vrender)
        render("nive.cms.workflow:templates/widget.pt", values)
        values = view.workflow()
        values.update(vrender)
        render("nive.cms.workflow:templates/editorpage.pt", values)

        
        

if __name__ == '__main__':
    unittest.main()
