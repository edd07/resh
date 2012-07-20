#===============================================================================
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
# 
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

""" 
    Functions for viewing files inside resh, the reddit shell
    And
    Functions and constants for output formatting
    @author: Luis E. Perez (edd07 at github)
"""

import sys

from urllib.request import urlopen, Request
from urllib.parse import urlencode

from bs4 import BeautifulSoup

#Fix formatting for the sucky windows console
if sys.platform == 'win32':
    BOLD=""
    RESET=""
    ORANGERED=""
    SEPARATOR="--------------------------------------------------------------------------------"
    NEWLINE=""
else:
    BOLD="\033[1m"
    RESET="\033[0m"
    ORANGERED="\033[31m"
    SEPARATOR="\n--------------------------------------------------------------------------------\n"
    NEWLINE="\n"

def asciify(self,s,strip_newlines=True):
    """Strip non-ascii chars from the string  because Windows is dumb"""
    return "".join(i for i in s if (ord(i)<128 and ( ord(i)!=10 if strip_newlines else True ) ))

if(sys.platform!='win32'): asciify=lambda x,strip_newlines=True: x

def shorten(self, s, n):
    """Shortens a string to n characters, including ellipsis (...)"""
    if(len(s)<=n): return s 
    else: return s[:n-3]+"..."


def wrap(self,string,width,margin):
    """Splits a string across several lines, each 80 columns wide"""
    #TODO: Make it word-wrap
    out=[]
    if width>80-len(margin): width=80-len(margin)
    for s in string.split("\n"):
        while s:
            out.append( (margin+"{:<"+str(80-len(margin))+"}").format(s[:width]))
            s=s[width:]
    return Listing.NEWLINE.join(out)

def view_image(url):
    """Converts an image to ascii-art using http://www.glassgiant.com/ascii/"""
    values={
            'maxwidth': '80',
            'fontsize': '8',
            'webaddress': url,
            'negative': 'Y'
            }
    req = Request("http://www.glassgiant.com/ascii/ascii.php", urlencode(values).encode('ascii'))
    response = urlopen(req)
    bs = BeautifulSoup(response.read())
    
    print(''.join(bs.body.strings).replace('\n', NEWLINE))
    
def view_html(url):
    """Converts an html document to a markdown'd string
    using my own fork of python-readability"""
    try:
        from readability import Document
    except ImportError:
        print("Can't convert document: python-readability is not installed")
        return
    
    html = urlopen(url).read()
    doc=Document(html)
    print(wrap(asciify(BOLD+doc.short_title()+RESET+"\n"+doc.markdown(),strip_newlines=False),80,''))
    
def view_text(url):
    """Wraps and prints a text file"""
    print(wrap(asciify(urlopen(url).read(),strip_newlines=False),80,''))