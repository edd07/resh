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
    def __init__(self, title, prompt, items):
        self.title=title
        self.prompt=prompt
        self.items=list(items)
        
    def format_count(self,count):
        if(count>999999):
            return str(count//1000000)+"M"
        elif(count>1000):
            return str(count//1000)+"K"
        else:
            return count
        
    
    def __str__(self):
        out=[]
        out.append(self.title)
        for i in self.items:
            try:
                out.append(getattr(self,"str_"+i.__class__.__name__)(self.items.index(i)+1,i))
            except AttributeError:
                out.append("Object of type "+i.__class__.__name__)
        return "\n".join(out)
    
    def str_Submission(self, number, submission):
        return "Submission OK"
    
    def str_Subreddit(self,number,subreddit):
        return "{:<3} {:<71} {:>4} readers".format(
                                                   number,
                                                   "\033[1m"+subreddit.display_name+"\033[0m",
                                                   self.format_count(subreddit.subscribers)
                                                  )
        
class My_Subreddits_Page(Page):
    def __init__(self,items):
        super().__init__(
                         "Your suscribed Subreddits:",
                         "subreddits>",
                         items
                         )
        
class Search_Page(Page):
    def __init__(self,terms,items):
        super().__init__(
                         "Search results for: "+terms,
                         "search results>",
                         items
                         )
        
class Subreddit_Search_Page(Search_Page):
    def __init__(self, terms, sub, items):
        self.subreddit=sub
        super().__init__(
                         terms,
                         items
                        )
        self.title="Subreddit search results for: '"+terms+"' in "+sub.display_name
        
class Subreddit_Page(Page):
    def __init__(self, sub, sort='hot', page=1):
        self.subreddit=sub
        items = getattr(self.subreddit, 'get_'+sort)(limit=25)
        super().__init__(
                         sub.display_name,
                         sub.display_name+">",
                         items
                                            )


        