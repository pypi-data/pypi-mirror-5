### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.hplskin.layer import IHPLSkin

# import Zope3 packages

# import local packages
from ztfy.skin.menu import SkinTargetMenuItem, SkinTargetJsMenuItem, SkinTargetDialogMenuItem


class HPLSkinMenuItem(SkinTargetMenuItem):
    """Customized menu item for ZBlog skin targets"""

    skin = IHPLSkin


class HPLSkinJsMenuItem(SkinTargetJsMenuItem):
    """Customized menu item for ZBlog skin targets"""

    skin = IHPLSkin


class HPLSkinDialogMenuItem(SkinTargetDialogMenuItem):
    """Customized menu item for ZBlog skin targets"""

    skin = IHPLSkin
