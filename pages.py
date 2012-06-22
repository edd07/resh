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
        self.items=items
    
    def __str__(self):
        print(self.title)
        for i in self.items:
            print(str(i))
        
class Search_Page():
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
    def __init__(self, sub, sort='hot'):
        self.subreddit=sub
        items = getattr(self.subreddit, 'get_'+sort)()
        super().__init__(
                         sub.display_name,
                         sub.display_name+">",
                         items
                                            )


        