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
    Main class for resh, the reddit command-line shell 
    @author: Luis E. Perez (edd07 at github)
"""

import cmd
import getpass
import reddit
from urllib.error import URLError
from pages import *

class resh(cmd.Cmd):
    history=[]
    page=None
    redditor=None
    
    def __init__(self):
        super(resh,self).__init__()
        self.prompt="resh>"
        self.reddit = reddit.Reddit(user_agent="resh")
        
        #shorthand
        self.do_EOF=self.do_exit
        self.do_sub=self.do_subreddit
        self.do_fp = self.do_frontpage
        self.do_u = self.do_user
        
    def load_page(self,page):
        self.history.append(self.page)
        self.page=page
        self.prompt=self.page.prompt
        print(self.page)
        
    def back(self):
        if(history):
            self.page=history.pop()
            self.prompt=self.page.prompt
            
    def do_back(self,list):
        """back: back [pages]
    Goes back the specified number of pages in the browsing history.
    If pages is left blank, it defaults to 1"""
        try:
            if(list==''): list='1'
            pages=int(list)
            for i in range(pages):
                back()
            print(self.page)
        except ValueError:
            print("Invalid argument ",line)
        
    def do_exit(self,line):
        """Exits resh"""
        return True

    def emptyline(self):
        print(self.page)
    
    def do_search(self,line):
        #TODO: add syntax to search for subreddit names
        #TODO: if line isn't specified, ask for search terms
        if(isinstance(self.page,Subreddit_Page)):
            #We're in a subreddit, so search inside it
            results=self.page.subreddit.search(line)
            if(results):
                self.load_page(Subreddit_Search_Page(line,self.page.subreddit,results))
            else:
                print("No posts match your search ",line)
        else:
            #search across the entire site
            results=self.reddit.search(line)
            if(results):
                self.load_page(Search_Page(line,results))
            else:
                print("No posts match your search ",line)            
            
    
    def do_subreddit(self,line):
        """subreddit: subreddit [subreddit]
    Goes to a subreddit. If subreddit isn't specified, the command 
    lists the user's suscribed subreddits."""
        if(line):
            self.load_page(Subreddit_Page(self.reddit.get_subreddit(line)))
            
        else:
            if(self.redditor is not None):
                #get subreddits
                self.load_page(My_Subreddits_Page(self.redditor.my_reddits()))
            else:
                print("You must login to view your subscribed subreddits")
    
    def do_frontpage(self,line):
        """Lists the posts on the user's frontpage"""
        pass
    
    def do_login(self,line):
        """login: login [user]
    Logs the user in."""
        try:
            if not line:
                self.reddit.login()
            else:
                self.reddit.login(username=line)
            self.redditor=self.reddit.user
        except reddit.errors.InvalidUserPass:
            print("Invalid user or password. Try again")
        except URLError:
            print("Network error, unable to login")
        
    def do_user(self,line):
        """user: user username
    Looks up the username and displays his or her overview"""
        
        

if __name__ == "__main__":
    resh().cmdloop("""
    Welcome to resh, the reddit command-line shell
    This program is free software, see COPYING for details
    
    Type a subreddit's name or 'frontpage' to show posts
    For a list of commands, type 'help'
    To exit type 'exit' (duh!) or press CTRL-D
    """)