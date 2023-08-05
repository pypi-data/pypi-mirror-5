# -*- coding: utf-8 -*-
#################################################################################
#										#
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,		#
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez    		#
# Christian Martel								#
#										#
# This program is free software; you can redistribute it and/or			#
# modify it under the terms of the GNU General Public License			#
# as published by the Free Software Foundation; either version 2		#
# of the License, or (at your option) any later version.			#
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software      		#
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#										#
#################################################################################

__doc__ = """ Zope OAI Sets Repository """

from Globals import HTMLFile
from OFS.Folder import Folder


def manage_addOAIExistSetRepository(self,
                                 id="",
                                 title="OAI Exist Sets repository"):
    """ method for adding a new OAI Exist sets repository """
    try:
        OAIO = zOAIExistSetRepository(id)
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, OAIO)
    OAIO = getattr(self, id)
    OAIO.title = title



class zOAIExistSetRepository(Folder):
    """ """
    
    meta_type = "Exist Open Archive set repository"
    
    manage_main = HTMLFile("dtml/manage_OAIExistRepositorySetMainForm",globals())
    