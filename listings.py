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

class Listing():
    def __init__(self, title, prompt, generator):
        self.title=title
        self.prompt=prompt
        self.generator=generator
        self.prev=[] #pages that come before the current one
        self.next=[] #pages that come after the current one
        self.items=None
        self.next_Page()
        
    def next_Page(self):
        """Retrieves the next page of items either from reddit, or the local copies
        if they've already been visited"""
        if(self.items):
            self.prev.append(self.items)  
        if(self.next):
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
        if(self.prev[-1]):
            self.next.append(self.items)
            self.items=self.prev.pop()
        else:
            raise IndexError
    
        
    def format_count(self,count):
        """Abbreviates a number to 4 characters"""
        if(count>9999999):
            return str(count//1000000)+"M"
        elif(count>999999):
            return ("%.1f" % (count/1000000) )+"M"
        elif(count>1000):
            return str(count//1000)+"K"
        else:
            return count
        
    
    def __str__(self):
        out=[]
        out.append("{:<72} page {:>2}".format(
                                                 self.title,
                                                 len(self.prev)
                                                 )) 
        if(not self.items):
            out.append("There doesn't seem to be anything here")
        out.append("To enter an item, type go <number>")
        
        for i in self.items:
            try:
                out.append(getattr(self,"str_"+i.__class__.__name__)(self.items.index(i)+1,i))
            except AttributeError:
                out.append("Object of type "+i.__class__.__name__)
        return "\n".join(out)
    
    def str_Submission(self, number, submission):
        return "Submission OK"
    
    def str_Subreddit(self,number,subreddit):
        return "{:<3} \033[1m{:<63}\033[0m {:>4} readers".format(
                                                   number,
                                                   subreddit.display_name,
                                                   self.format_count(subreddit.subscribers)
                                                  )
    def str_Comment(self,number,comment):
        #TODO: Wrap comments and indent depending on level
        return "Comment OK"
        
class My_Subreddits_Listing(Listing):
    def __init__(self,generator):
        super().__init__(
                         "Your suscribed Subreddits:",
                         "subreddits>",
                         generator
                         )
        
class Search_Listing(Listing):
    def __init__(self,terms,generator):
        super().__init__(
                         "Search results for: "+terms,
                         "search results>",
                         generator
                         )
        
class Subreddit_Search_Listing(Search_Listing):
    def __init__(self, terms, sub, generator):
        self.subreddit=sub
        super().__init__(
                         terms,
                         generator
                        )
        self.title="Subreddit search results for: '"+terms+"' in /r/"+sub.display_name
        
class Subreddit_Listing(Listing):
    def __init__(self, sub, sort='hot'):
        self.subreddit=sub
        generator = getattr(self.subreddit, 'get_'+sort)(limit=None)
        super().__init__(
                         "\033[1m{:<31}\033[0m {:>31}".format(sub.title,"/r/"+sub.display_name),
                         "/r/"+sub.display_name+">",
                         generator
                                            )


        