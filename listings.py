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
from datetime import datetime, timedelta

class Listing():
    
    #Fix formatting for the sucky windows console
    if sys.platform == 'win32':
        BOLD=""
        RESET=""
        SEPARATOR="--------------------------------------------------------------------------------"
        NEWLINE=""
    else:
        BOLD="\033[1m"
        RESET="\033[0m"
        SEPARATOR="\n--------------------------------------------------------------------------------\n"
        NEWLINE="\n"
    
    def __init__(self, title, prompt, generator):
        self.title=title
        self.prompt=prompt
        self.generator=generator
        self.prev=[] #pages that come before the current one
        self.next=[] #pages that come after the current one
        self.content=""
        self.items=None
        #bypass asciify for non-windows systems
        if(sys.platform!='win32'): self._asciify=lambda x,strip_newlines=True: x
        self.str_str=lambda x: x
        self.next_Page()
    
    def _time(self,timestamp):
        delta = (datetime.utcnow()-datetime.fromtimestamp(timestamp))
        if(delta.days>0):
            if delta.days > 365:
                return str(int(delta.days//365))+(" year" if delta.days//365==1 else " years")
            elif delta.days>31:
                return str(int(delta.days//31))+(" month" if delta.days//31==1 else " months")
            else:
                return str(int(delta.days))+(" day" if delta.days==1 else " days")
        else:
            if delta.total_seconds()>3600:
                return str(int(delta.total_seconds()//3600))+(" hour" if delta.total_seconds()//3600==1 else " hours")
            elif delta.total_seconds()>60:
                return str(int(delta.total_seconds()//60))+(" minute" if delta.total_seconds()//60==1 else " minutes")
            else:
                return str(int(delta.total_seconds()))+(" second" if delta.total_seconds()==1 else " seconds")


    def _asciify(self,s,strip_newlines=True):
        """Strip non-ascii chars from the string  because windows is dumb"""
        return "".join(i for i in s if (ord(i)<128 and ( ord(i)!=10 if strip_newlines else True ) ))

    def _shorten(self, s, n):
        """Shortens a string to n characters, including ellipsis (...)"""
        if(len(s)<=n): return s 
        else: return s[:n-3]+"..."


    def _wrap(self,string,width,margin):
        """Splits a string across several lines, each 80 columns wide"""
        #TODO: Make it word-wrap
        out=[]
        if width>80-len(margin): width=80-len(margin)
        for s in string.split("\n"):
            while s:
                out.append( (margin+"{:<"+str(80-len(margin))+"}").format(s[:width]))
                s=s[width:]
        return Listing.NEWLINE.join(out)
    
    def go(self,num):
        return self.items[num-1]

        
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
                for i in range(10):
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
        if not self.prev:
            out.append(self.content)
            
        out.append("{}{:<72}{} page {:>2}".format(
                                                 Listing.BOLD,
                                                 self.title,
                                                 Listing.RESET,
                                                 len(self.prev)+1
                                                 ))
        counter=1
        for i in self.items:
            try:
                out.append("{:>2} ".format(counter)+getattr(self,"str_"+i.__class__.__name__)(i))
            except AttributeError:
                out.append("{:>2} ".format(counter)+"Can't handle a(n) "+i.__class__.__name__)
            counter=counter+1

        if self.items:
            out.append("{:<80}".format("To enter an item, type 'go <number>'. For more items, type 'next'"))
        else:
            out.append("{:<80}".format("There doesn't seem to be anything here"))

        return Listing.SEPARATOR.join(out)
    
    def str_Submission(self,submission):
        
        title=self._asciify(submission.title+" ("+submission.domain+")") 

        out=["{}{:>4} {:<46}{} {:>25}".format(
                                                    Listing.BOLD,
                                                    submission.score,
                                                    title[:46],
                                                    Listing.RESET,
                                                    "/r/"+submission.subreddit.display_name
                                                    )]
        if len(title)>46:
            out.append(Listing.BOLD+ self._wrap(title[46:],46,"        " )+Listing.RESET)
        return Listing.NEWLINE.join(out)
        
    
    def str_Comment(self,comment):
        out=["in {:<62} {:>4} points".format(
                                   self._shorten(self._asciify(comment.submission.title),62),
                                    comment.ups-comment.downs,
                                          )]

        out.append(Listing.BOLD+self._wrap(comment.body,77,"   " )+Listing.RESET)
        return Listing.NEWLINE.join(out)
        
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
        title=self._asciify(subreddit.title)
        out=[ "{}{:<38}{} {:>25} {:>4} readers".format(
                                                   Listing.BOLD,
                                                   title[:38],
                                                   Listing.RESET,
                                                   "/r/"+subreddit.display_name,
                                                   self.format_count(subreddit.subscribers)
                                                  )]
        if len(title)>38:
            out.append(Listing.BOLD+self._wrap(title[38:],38,"   " )+Listing.RESET)
        return Listing.NEWLINE.join(out)
        
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
                         "{}{:<46}{} {:>25}".format(Listing.BOLD,self._shorten(self._asciify(sub.title),46),Listing.RESET,"/r/"+sub.display_name),
                         "/r/"+sub.display_name+">",
                         generator
                                            )
        
    def str_Submission(self,submission):
        
        title=self._asciify(submission.title+" ("+submission.domain+")") 

        out=["{}{:>4} {:<46}{} {:>25}".format(
                                                    Listing.BOLD,
                                                    submission.score,
                                                    title[:46],
                                                    Listing.RESET,
                                                    "by "+submission.author.name
                                                    )]
        if len(title)>46:
            out.append(Listing.BOLD+self._wrap(title[46:],46,"        " )+Listing.RESET)
        return Listing.NEWLINE.join(out)
        
class Frontpage_Listing(Listing):
    """Listing for the reddit.com front page"""
    def __init__(self,generator):
        super().__init__("Front Page","frontpage>",generator)
        

class User_Listing(Listing):
    """Listing for an user's overview"""
    def __init__(self,user):
        self.user=user
        super().__init__(
                         "Overview for "+user.name,
                         "user>",
                         user.get_overview(limit=None)
                         )
        self.content="{}User {:<74}{}{}Link karma:{:<14} Comment karma:{:<14} Reditor for {:>12}".format(
                                Listing.BOLD,
                                user.name,
                                Listing.RESET,
                                Listing.NEWLINE,
                                user.link_karma,
                                user.comment_karma,
                                self._time(user.created)
                                                                                  )
        

class Submission_Listing(Listing):
    """Listing for a submission's comment page"""
    def __init__(self,submission):
        self.submission=submission
        super().__init__(
                         "Comments",
                         "submission>",
                         (i for i in submission.comments)
                        )
        if(self.submission.is_self):
            body= self._wrap(self._asciify(self.submission.selftext,strip_newlines=False),80,"")
        else:
            body= "Link: {:<74}".format(self.submission.url)
        
        self.content=Listing.BOLD+self._wrap(submission.title,80,"")+Listing.RESET+Listing.SEPARATOR+body
        
    def str_Comment(self,comment):
        out=["by {:<43} {:>4} points  {:>12} ago".format(
                                   self._shorten(self._asciify(comment.author.name),48),
                                    comment.ups-comment.downs,
                                    self._time(comment.created)
                                    #comment.created
                                          )]

        out.append(Listing.BOLD+self._wrap(comment.body,77,"   " )+Listing.RESET)
        return Listing.NEWLINE.join(out)
           




        