# -*- coding: utf-8 -*-

import time
import unittest

from nive.userdb.root import adminuser, UserCache
from db_app import *

class ObjectTest(unittest.TestCase):

    def setUp(self):
        self.app = app()

    def tearDown(self):
        self.app.Close()
        pass

    def test_add(self):
        a=self.app
        root=a.root()
        user = User("test")
        # root
        root.DeleteUser("user1")
        root.DeleteUser("user2")
        root.DeleteUser("user3")
        data = {"password": "11111", "surname": "surname", "lastname": "lastname", "organistion": "organisation"}
        
        data["name"] = "user1"
        data["email"] = "user1@aaa.ccc"
        o,r = root.AddUser(data, activate=1, generatePW=0, mail=None, notify=False, groups="", currentUser=user)
        self.assert_(o,r)
        o,r = root.AddUser(data, activate=1, generatePW=0, mail=None, notify=False, groups="", currentUser=user)
        self.assertFalse(o,r)

        data["name"] = "user2"
        data["email"] = "user2@aaa.ccc"
        o,r = root.AddUser(data, activate=1, generatePW=1, mail=None, notify=False, groups="group:author", currentUser=user)
        self.assert_(o,r)

        data["name"] = "user3"
        data["email"] = "user3@aaa.ccc"
        o,r = root.AddUser(data, activate=0, generatePW=1, mail=None, notify=False, groups="group:editor", currentUser=user)
        self.assert_(o,r)
        self.assert_("group:editor" in o.data.groups, o.data.groups)
        self.assert_(o.data.password != "11111")
        self.assertFalse(o.meta.pool_state)
        
        root.MailUserPass(email = "user1", mailtmpl = None)
        root.MailUserPass(email = "user2@aaa.ccc", mailtmpl = None, createNewPasswd=False)
        root.MailUserPass(email = "user3@aaa.ccc", mailtmpl = None)
        
        self.assert_(root.GetUserByName("user2", activeOnly=1))
        self.assert_(root.GetUserByID(o.id, activeOnly=0))
        self.assert_(root.GetUserByMail("user2@aaa.ccc", activeOnly=1))
        ggg = root.GetUserGroups("user2", activeOnly=1)
        self.assert_("group:author" in ggg, ggg)
        
        self.assert_(root.LookupUser(name="user1", id=None, activeOnly=1, reloadFromDB=1))
        self.assertFalse(root.LookupUser(name="user3", id=None, activeOnly=1, reloadFromDB=1))
        self.assert_(root.LookupUser(name="user3", id=None, activeOnly=0, reloadFromDB=1))
        
        self.assert_(len(root.GetUserInfos(["user1", "user2"], fields=["name", "email", "title"], activeOnly=True)))
        self.assert_(len(root.GetUsersWithGroup("group:author", fields=["name"], activeOnly=True)))
        self.assert_(len(root.GetUsersWithGroup("group:editor", fields=["name"], activeOnly=False)))
        self.assertFalse(len(root.GetUsersWithGroup("group:editor", fields=["name"], activeOnly=True)))
        self.assert_(len(root.GetUsers()))
        
        root.DeleteUser("user1")
        root.DeleteUser("user2")
        root.DeleteUser("user3")

        
    def test_login(self):
        a=self.app
        root=a.root()
        user = User("test")
        # root
        root.DeleteUser("user1")
        root.DeleteUser("user2")
        root.DeleteUser("user3")
        data = {"password": "11111", "surname": "surname", "lastname": "lastname", "organistion": "organisation"}
        
        data["name"] = "user1"
        data["email"] = "user1@aaa.ccc"
        o,r = root.AddUser(data, activate=1, generatePW=0, mail=None, notify=False, groups="", currentUser=user)
        self.assert_(o,r)
        l,r = root.Login("user1", "11111", raiseUnauthorized = 0)
        self.assert_(l,r)
        self.assert_(root.Logout("user1"))
        l,r = root.Login("user1", "aaaaa", raiseUnauthorized = 0)
        self.assertFalse(l,r)
        l,r = root.Login("user1", "", raiseUnauthorized = 0)
        self.assertFalse(l,r)

        data["name"] = "user2"
        data["email"] = "user2@aaa.ccc"
        o,r = root.AddUser(data, activate=1, generatePW=1, mail=None, notify=False, groups="", currentUser=user)
        self.assert_(o,r)
        l,r = root.Login("user2", o.data.password, raiseUnauthorized = 0)
        self.assertFalse(l,r)
        self.assert_(root.Logout("user1"))
        l,r = root.Login("user2", "11111", raiseUnauthorized = 0)
        self.assertFalse(l,r)

        data["name"] = "user3"
        data["email"] = "user3@aaa.ccc"
        o,r = root.AddUser(data, activate=0, generatePW=1, mail=None, notify=False, groups="group:author", currentUser=user)
        self.assert_(o,r)
        l,r = root.Login("user3", o.data.password, raiseUnauthorized = 0)
        self.assertFalse(l,r)
        self.assertFalse(root.Logout("user3"))
        
        root.DeleteUser("user1")
        root.DeleteUser("user2")
        root.DeleteUser("user3")


    def test_user(self):
        a=self.app
        root=a.root()
        user = User("test")
        # root
        root.DeleteUser("user1")
        data = {"password": "11111", "surname": "surname", "lastname": "lastname", "organistion": "organisation"}
        
        data["name"] = "user1"
        data["email"] = "user1@aaa.ccc"
        o,r = root.AddUser(data, activate=1, generatePW=0, mail=None, notify=False, groups="", currentUser=user)

        self.assert_(o.SecureUpdate(data, user))
        self.assert_(o.UpdateGroups(["group:author"]))
        self.assert_(o.GetGroups()==("group:author",), o.GetGroups())
        self.assert_(o.AddGroup("group:editor", user))
        self.assert_(o.GetGroups()==("group:author","group:editor"), o.GetGroups())
        self.assert_(o.InGroups("group:editor"))
        self.assert_(o.InGroups("group:author"))
    
        self.assert_(o.TitleFromName("surname", "lastname", "name")=="surname lastname")
        self.assert_(o.TitleFromName("", "", "name")=="name")
        o.AddToCache()
        self.assert_(root.GetFromCache(id=o.id))
        o.RemoveFromCache()
        self.assertFalse(root.GetFromCache(id=o.id))

        root.DeleteUser("user1")



class AdminuserTest(unittest.TestCase):

    def test_user(self):
        u = adminuser({"name":"admin", "password":"password", "email":"aa@eee.com", "groups":("group:admin",)})
        
        self.assert_(str(u)=="admin")
        self.assert_(u.Authenticate("password"))
        self.assertFalse(u.Authenticate("aaaaaaa"))
        u.Login()
        u.Logout()
        self.assert_(u.GetGroups()==("group:admin",))
        self.assert_(u.InGroups("group:admin"))
        self.assertFalse(u.InGroups("group:traa"))
        u.AddToCache()
        u.RemoveFromCache()        
        
        
class CacheTest(unittest.TestCase):
        
    def setUp(self):
        self.app = app()

    def tearDown(self):
        self.app.Close()
        pass

    def test_cache(self):
        a=self.app
        root=a.root()
        user = User("test")
        # root
        root.DeleteUser("user1")
        data = {"password": "11111", "surname": "surname", "lastname": "lastname", "organistion": "organisation"}
        
        data["name"] = "user1"
        data["email"] = "user1@aaa.ccc"
        o,r = root.AddUser(data, activate=1, generatePW=0, mail=None, notify=False, groups="", currentUser=user)
        self.assert_(o,r)
        
        obj = root.GetUserByName("user1")
        cache = UserCache()
        
        cache.Cache(obj, obj.id)
        self.assertFalse(cache.GetFromCache(0))
        self.assertFalse(cache.GetFromCache(123))
        self.assert_(cache.GetFromCache(obj.id))
        self.assert_(len(cache.GetAllFromCache())==1)
        cache.RemoveCache(123)
        self.assert_(len(cache.GetAllFromCache())==1)
        cache.RemoveCache(obj.id)
        self.assert_(len(cache.GetAllFromCache())==0)
        cache.Cache(obj, 1)
        cache.Cache(obj, 2)
        cache.Cache(obj, 3)
        self.assert_(len(cache.GetAllFromCache())==3)
        
        
if __name__ == '__main__':
    unittest.main()
