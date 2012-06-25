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
    Listing classes for resh, the reddit command-line shell 
    @author: Luis E. Perez (edd07 at github)
"""

import reddit
import sys

class Listing():
    BOLD="\033[1m"
    RESET="\033[0m"
    NEWLINE="\n"
    
    def __init__(self, title, prompt, generator):
        self.title=title
        self.prompt=prompt
        self.generator=generator
        self.prev=[] #pages that come before the current one
        self.next=[] #pages that come after the current one
        self.items=None
        self.next_Page()
        #turn off ANSI escape codes for the sucky windows console
        if sys.platform == 'win32':
            Listing.BOLD=""
            Listing.RESET=""
            Listing.NEWLINE="\r\n"                
        
    def next_Page(self):
        """Retrieves the next page of items either from reddit, or the local copies
        if they've already been visited"""
        if self.items:
            self.prev.append(self.items)  
        if self.next:
            #local copies
            self.items=self.next.pop()
        else:
            #retrieve new stories
            self.items=[]
            try:
                for i in range(25):
                    self.items.append(next(self.generator))
            except StopIteration:
                pass
        
    
    def prev_Page(self):
        """Retrieves previous pages of items from local copies"""
        if self.prev[-1]:
            self.next.append(self.items)
            self.items=self.prev.pop()
        else:
            raise IndexError
    
    def __str__(self):
        out=[]
        out.append("{:<72} page {:>2}".format(
                                                 self.title,
                                                 len(self.prev)+1
                                                 ))
        if self.items:
            out.append("To enter an item, type go <number>")
        else:
            out.append("There doesn't seem to be anything here")
        
        for i in self.items:
            try:
                out.append("{:>2} ".format(self.items.index(i)+1)+getattr(self,"str_"+i.__class__.__name__)(i))
            except AttributeError:
                out.append("{:>2} ".format(self.items.index(i)+1)+"Can't handle a(n) "+i.__class__.__name__)
        return Listing.NEWLINE.join(out)
    
    def str_Submission(self,submission):
        title=submission.title
        out=["{}{:>4} {:<40}{}    /r/{:<25}".format(
                                                    Listing.BOLD,
                                                    submission.score,
                                                    title[:40],
                                                    Listing.RESET,
                                                    submission.subreddit.display_name
                                                    )]
        title=title[40:]
        while title: #split the title in several lines if necessary
            out.append("        "+title[:40])
            title=title[40:]
        return Listing.NEWLINE.join(out)
        
    
    def str_Comment(self,comment):
        #TODO: Wrap comments and indent depending on level
        return "Comment OK"
        
class My_Subreddits_Listing(Listing):
    """Listing of the user's subscribed subreddits"""
    def __init__(self,generator):
        super().__init__(
                         "Your suscribed Subreddits:",
                         "subreddits>",
                         generator
                         )
    def format_count(self,count):
        """Abbreviates a number to 4 characters"""
        if count>9999999:
            return str(count//1000000)+"M"
        elif count>999999:
            return ("%.1f" % (count/1000000) )+"M"
        elif count>1000:
            return str(count//1000)+"K"
        else:
            return count
    
    def str_Subreddit(self,subreddit):
        return "{}{:<63}{} {:>4} readers".format(
                                                   Listing.BOLD,
                                                   subreddit.display_name,
                                                   Listing.RESET,
                                                   self.format_count(subreddit.subscribers)
                                                  )
        
class Search_Listing(Listing):
    """Listing of posts matching a search term"""
    def __init__(self,terms,generator):
        self.terms=terms
        super().__init__(
                         "Search results for: "+terms,
                         "search results>",
                         generator
                         )
        
class Subreddit_Search_Listing(Search_Listing):
    """Listing of posts matching a search term inside a subreddit"""
    def __init__(self, terms, sub, generator):
        self.subreddit=sub
        super().__init__(
                         terms,
                         generator
                        )
        self.title="Subreddit search results for: '"+terms+"' in /r/"+sub.display_name
        
class Subreddit_Listing(Listing):
    """Listing of a subreddit's front page"""
    def __init__(self, sub, sort='hot'):
        self.subreddit=sub
        generator = getattr(self.subreddit, 'get_'+sort)(limit=None)
        super().__init__(
                         "{}{:<46}{} {:>25}".format(Listing.BOLD,sub.title,Listing.RESET,"/r/"+sub.display_name),
                         "/r/"+sub.display_name+">",
                         generator
                                            )
        
class Frontpage_Listing(Listing):
    """Listing for the reddit.com front page"""
    def __init__(self,generator):
        super().__init__("Front Page","frontpage>",generator)


        