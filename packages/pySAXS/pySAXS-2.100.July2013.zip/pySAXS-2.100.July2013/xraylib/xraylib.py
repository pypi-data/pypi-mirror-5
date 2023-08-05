#!/usr/bin/env python

#Copyright (c) 2009, 2010, Bruno Golosio, Antonio Brunetti, Manuel Sanchez del Rio, Tom Schoonjans and Teemu Ikonen
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    * The names of the contributors may not be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY Bruno Golosio, Antonio Brunetti, Manuel Sanchez del Rio, Tom Schoonjans and Teemu Ikonen ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Bruno Golosio, Antonio Brunetti, Manuel Sanchez del Rio, Tom Schoonjans and Teemu Ikonen BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.





from math import *
from _xraylib import *
import getopt, sys, string, traceback
from xraymessages import *
from xrayhelp import *

if __name__ == '__main__' :
    if len(sys.argv) == 1:
        display_banner()
        display_usage()
        sys.exit(0)
    short = 'hdf:'
    long = ('help', 'doc', 'func=')
    arglist = string.split(sys.argv[1])
    opts,args = getopt.getopt(arglist, short, long)
    for opt,val in opts:
        if opt in ('-h', '--help'):
            display_banner()
	    display_help()
	    sys.exit(0)
        elif opt in ('-d', '--doc'):
            display_banner()
	    display_doc()
	    sys.exit(0)
        elif opt in ('-f', '--func'):
            print val
	    display_func(val)
	    sys.exit(0)
    try:    
        XRayInit()
        print "%.5g" % eval(sys.argv[1])
    except:
        traceback.print_exc()
        display_usage()
