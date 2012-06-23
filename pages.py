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
    Page classes for resh, the reddit command-line shell 
    @author: Luis E. Perez (edd07 at github)
"""

import reddit

class Page():
    def __init__(self, title, prompt, generator):
        self.title=title
        self.prompt=prompt
        self.prev=[] #sub-pages that come before the current one
        self.next=[] #sub-pages that come after the current one
        self.items=None
        self.items=next_page()
        
    def next_page(self):
        """Retrieve the next sub-page of items either from reddit, or the local copies
        if they've already been visited"""
        self.prev.append(self.items)  
        if(self.next):
            #local copies
            self.items=self.next.pop()
        else:
            #retrieve new stories
            self.items=[]
            for i in range(25):
                self.items.append(self.generator.next())
        
    
    def prev_page(self):
        """Retrieve previous sub-page of items from local copies"""
        if(self.prev[-1]):
            self.next.append(self.items)
            self.items=self.prev.pop()
        else:
            raise IndexError
    
        
    def format_count(self,count):
        """Abbreviates a number to 4 characters"""
        if(count>999999):
            return str("{:>3}".format(count/1000000))+"M"
        elif(count>1000):
            return str(count//1000)+"K"
        else:
            return count
        
    
    def __str__(self):
        out=[]
        out.append("{:<72} page {:>2}".format(
                                                 self.title,
                                                 len(self.prev)+1
                                                 ))
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
        
class My_Subreddits_Page(Page):
    def __init__(self,generator):
        super().__init__(
                         "Your suscribed Subreddits:",
                         "subreddits>",
                         generator
                         )
        
class Search_Page(Page):
    def __init__(self,terms,generator):
        super().__init__(
                         "Search results for: "+terms,
                         "search results>",
                         generator
                         )
        
class Subreddit_Search_Page(Search_Page):
    def __init__(self, terms, sub, generator):
        self.subreddit=sub
        super().__init__(
                         terms,
                         generator
                        )
        self.title="Subreddit search results for: '"+terms+"' in "+sub.display_name
        
class Subreddit_Page(Page):
    def __init__(self, sub, sort='hot', page=1):
        self.subreddit=sub
        generator = getattr(self.subreddit, 'get_'+sort)(limit=None)
        super().__init__(
                         "\033[1m{:<31}\033[0m /r/{:>28}".format(sub.title,sub.display_name),
                         "/r/"+sub.display_name+">",
                         generator
                                            )


        