# -*- coding: ISO-8859-1 -*-
# ./stackWordSet.py

"""
#------------------------------------------------------------------
#  Copyright (C) 2006
#  Author:  gerd franzkowiak <gfranzkowiak@forth-ev.de>
#  Date:    2006-05-16
#  Version: 0.01
#  License: "GPLv2"
#------------------------------------------------------------------

This source is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#------------------------------------------------------------------
"""

#[Stack Word Set]
stackWordSet = { 'DROP'  :	    '( x1 - )                             ',
                 '2DUP'  :	    '( x1 x2 - x1 x2 x1 x2 )              ',
                 '2OVER' :	    '( x1 x2 x3 x4 - x1 x2 x3 x4 x1 x2 )  ',
                 '2SWAP' :	    '( x1 x2 x3 x4 - x3 x4 x1 x2 )        ',
                 '>R'    :	    'Execution: ( x - ) und ( R: - x )    ',
                 '?DUP'  :	    'entweder: ( x - 0 ) oder: ( x - x x )',
                 'DEPTH' :	    '( - +n )drop( x - )                  ',
                 'DUP'   :	    '( x - x x )                          ',
                 'OVER'  :	    '( x1 x2 - x1 x2 x1 )                 ',
                 'R>'    :	    'Execution: ( - x ) und ( R: x - )    ',
                 'RDROP' :	    '( R: x - )                           ',
                 'RP@'   :	    '( - a-addr )                         ',
                 'RP!'   :	    '( a-addr - )                         ',
                 'R@'    :	    'Execution: ( - x ) und ( R: x - x )  ',
                 'ROT'   :	    '( x1 x2 x3 - x2 x3 x1 )              ',
                 'SP@'   :	    '( - a-addr )                         ',
                 'SP!'   :	    '( a-addr - )                         ',
                 'SWAP'  :	    '( x1 x2 - x2 x1 )                    '  }
