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

from nive.i18n import _
from nive.utils.utils import ConvertListToStr, ConvertToNumberList

from nive.definitions import StagPage, StagPageElement
from nive.definitions import IContainer, ViewConf

from nive.cms.cmsview.sort import ISort






class ObjCopy:
    """
    Cut, copy and paste functionality for objects 
    """
    
    def CanCopy(self):
        """
        """
        return not hasattr(self, "disableCopy") or not self.disableCopy


    def CanPaste(self):
        """
        """
        return False



class ContainerCopy:
    """
    Cut, copy and paste functionality for object container
    """
    
    def CanCopy(self):
        """
        """
        return not hasattr(self, "disableCopy") or not self.disableCopy


    def CanPaste(self):
        """
        """
        return not hasattr(self, "disablePaste") or not self.disablePaste


    def Paste(self, ids, pos, user):
        """
        Paste the copied object with id to this object
        """
        root = self.GetRoot()
        new = []
        msgs = []
        result = True
        for id in ids:
            id = int(id)
            if self.GetID() == id:
                continue
            obj = root.LookupObj(id, preload="skip")
            if not obj:
                msgs.append(_(u"Object not found"))
                result = False
                continue
            newobj = self.Duplicate(obj, user) 
            if not newobj:
                raise TypeError, "Duplicate failed"
            if ISort.providedBy(self):
                self.InsertAfter(newobj.id, pos, user=user)
            new.append(newobj)
        if not self.app.configuration.autocommit:
            for o in new:
                o.Commit(user)
        if result:
            msgs.append(_(u"OK. Copied and pasted."))
        return result, msgs
    

    def Move(self, ids, pos, user):
        """
        Move the object with id to this object
        
        Events
        
        - beforeAdd(data=obj.meta, type=type)
        - afterDelete(id=obj.id)
        - moved()
        - afterAdd(obj=obj)
        """
        root = self.root()
        oldParent=None

        moved = []
        msgs = []
        result = True
        for id in ids:
            id = int(id)
            if self.GetID() == id:
                continue
            obj = root.LookupObj(id, preload="skip")
            if not obj:
                msgs.append(_(u"Object not found"))
                result = False
                continue

            type=obj.GetTypeID()
            # allow subobject
            if not self.IsTypeAllowed(type, user):
                raise TypeError, "Object cannot be added here"

            self.Signal("beforeAdd", data=obj.meta, type=type)
            if not oldParent or oldParent.id != obj.GetParent().id:
                oldParent = obj.GetParent()
            obj.__parent__ = self
            obj.meta["pool_unitref"] = self.GetID()
            oldParent.Signal("afterDelete", id=obj.id)
            obj.Signal("moved")
            #obj.Close()
            moved.append(obj)

        for o in moved:
            o.Commit(user)
            if ISort.providedBy(self):
                self.InsertAfter(o.id, pos, user=user)
            self.Signal("afterAdd", obj=o)
        if result:
            msgs.append(_(u"OK. Cut and pasted."))
        return result, msgs
    


views = [
    # cut, copy
    ViewConf(name = "cut",  attr = "cut",  context = IContainer, permission="edit"),
    ViewConf(name = "copy", attr = "copy", context = IContainer, permission="edit"),    
    # paste
    ViewConf(name = "paste", attr = "paste", context = IContainer, permission = "add")
]


class CopyView:
    """
    View functions for cut, copy and paste
    """
    CopyInfoKey = "CCP__"

    def cut(self):
        """
        """
        ids = self.GetFormValue(u"ids")
        if not ids:
            ids = [self.context.id]
        cp = self.SetCopyInfo(u"cut", ids, self.context)
        url = self.GetFormValue(u"url")
        if not url:
            url = self.PageUrl(self.context)
        msgs = _(u"OK. Cut.")
        ok = True
        return self.Redirect(url, [msgs])


    def copy(self):
        """
        """
        ids = self.GetFormValue(u"ids")
        if not ids:
            ids = [self.context.id]
        cp = self.SetCopyInfo(u"copy", ids, self.context)
        url = self.GetFormValue(u"url")
        if not url:
            url = self.PageUrl(self.context)
        msgs = _(u"OK. Copied.")
        return self.Redirect(url, [msgs])


    def paste(self):
        """
        """
        deleteClipboard=1
        url = self.GetFormValue(u"url")
        if not url:
            url = self.PageUrl(self.context)
        action, ids = self.GetCopyInfo()
        if not action or not ids:
            msgs = []
            return self.Redirect(url, msgs)

        pepos = self.GetFormValue(u"pepos",0)
        result = False
        msgs = [_(u"Method unknown")]
        if action == u"cut":
            result, msgs = self.context.Move(ids, pepos, user=self.User())
            if result and deleteClipboard:
                cp = self.DeleteCopyInfo()
        elif action == u"copy":
            result, msgs = self.context.Paste(ids, pepos, user=self.User())
        return self.Redirect(url, msgs)
    
    
    def SetCopyInfo(self, action, ids, context):
        """
        store in session or cookie
        """
        if not ids:
            return u""
        if isinstance(ids, basestring):
            ids=ConvertToNumberList(ids)
        cp = ConvertListToStr([action]+ids).replace(u" ",u"")
        self.request.session[self.CopyInfoKey] = cp
        return cp


    def GetCopyInfo(self):
        """
        get from session or cookie
        """
        cp = self.request.session.get(self.CopyInfoKey,u"")
        if isinstance(cp, basestring):
            cp = cp.split(u",")
        if not cp or len(cp)<2:
            return u"", []
        return cp[0], cp[1:]

    
    def ClipboardEmpty(self):
        """
        check if clipboard is empty
        """
        cp = self.request.session.get(self.CopyInfoKey,u"")
        return cp==u""
    

    def DeleteCopyInfo(self):    
        """
        reset copy info
        """
        self.request.session[self.CopyInfoKey] = u""

    