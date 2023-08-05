#-----------------------------------------------------------------------
# $Id: wcst11ActionUpdateDataPart.py 1266 2012-02-12 14:32:48Z meissls $
#
# Description: 
#
#   WCS 1.1.x Transaction extension -  implementation of the UpdateDataPart action  
#
#-------------------------------------------------------------------------------
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Martin Paces <martin.paces@iguassu.cz>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 Iguassu Software Systems, a.s 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------

import os 
import sys 
import os.path
import traceback

import logging
import shutil

from wcst11ActionCommon import ExActionFailed

#-------------------------------------------------------------------------------

# ACTION: UPDATE DATA PART 

def wcst11ActionUpdateDataPart( action , context ) : 

    aname = action["Action"]
    logging.debug( "WCSt11:%s: START" % aname ) 

    # action not implemented 

    msg = "WCSt11:%s: Action not implemented!" % aname 
    logging.error( msg ) 
    raise ExActionFailed , msg 

    return coverageId
