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
from listings import *
import sys
import os
from inspect import getmembers #for the py command

class resh(cmd.Cmd):
    #TODO: 
    #submit command
    #reply command
    #friend command
    #upvote & downvote commands
    #document scriptable features
    #save command
    #saved links
    #suscribe/unsuscribe commands
    
    def __init__(self):
        super(resh,self).__init__()
        self.prompt="resh>"
        self.reddit = reddit.Reddit(user_agent="resh (github.com/edd07/resh)")
        self.history=[]
        self.listing=None
        self.redditor=None
        
        #undocumented shorthand commands
        self.do_EOF=self.do_exit
        self.do_r=self.do_subreddit
        self.do_fp = self.do_frontpage
        self.do_u = self.do_user
    
    def clear(self):
        if sys.platform=='win32':
            os.system('cls')
        else:
            os.system('clear')
        
    def load_Listing(self,listing):
        self.clear()
            
        self.history.append(self.listing)
        self.listing=listing
        self.prompt=self.listing.prompt
        print(self.listing)
        
    def back(self):
        if self.history:
            self.listing=self.history.pop()
            if self.listing:
                self.prompt=self.listing.prompt
            else:
                self.prompt="resh>"
                
    def multiline_input(self):
        flag=True
        out=[]
        while flag:
            line=input()
            out.append(line)
            flag= line.strip()==''
        return "\n\n".join(out)
        
            
    def do_back(self,line):
        """usage: back [num]
    Goes to the previous listing in the browsing history
    If num is specified, it goes that many listings back."""
        try:
            if line=='': line='1'
            pages=int(line)
            for i in range(pages):
                self.back()
            if self.listing: 
                self.clear()
                print(self.listing)
        except ValueError:
            print("Invalid argument ",line)
            
    def do_next(self,line):
        """usage: next
    Displays the next items in the current listing"""

        self.listing.next_Page()
        self.clear()
        print(self.listing)
            
            
    def do_prev(self,line):
        """usage: prev
    Displays the previous items in the current listing"""
        try:
            self.listing.prev_Page()
            self.clear()
            print(self.listing)
        except IndexError:
            print("These are the first posts in this listing")
        
    def do_exit(self,line):
        """Exits resh"""
        return True

    def emptyline(self):
        self.clear()
        print(self.listing)
    
    def do_search(self,line):
        """usage: search [pattern]
    Search posts with a pattern. If used inside a subreddit, the results
    are restricted to the current subreddit. Otherwise, the search 
    returns result from the whole site"""
        #TODO: add syntax to search for subreddit names
        
        if not line:
            line=input("Search for: ")
        if isinstance(self.listing,Subreddit_Listing):
            #We're in a subreddit, so search inside it
            results=self.listing.subreddit.search(line,limit=None)
            if results:
                self.load_Listing(Subreddit_Search_Listing(line,self.listing.subreddit,results))
            else:
                print("No posts match your search ",line)
        else:
            #search across the entire site
            results=self.reddit.search(line,limit=None)
            if results:
                self.load_Listing(Search_Listing(line,results))
            else:
                print("No posts match your search ",line)            
            
    
    def do_subreddit(self,line):
        """usage: subreddit [subreddit]
    Goes to a subreddit. If subreddit isn't specified, the command 
    lists the user's suscribed subreddits."""
        if line:
            try:
                self.load_Listing(Subreddit_Listing(self.reddit.get_subreddit(line)))
            except:
                print("The subreddit "+line+" does not exist")
        else:
            if self.redditor is not None:
                #get subreddits
                self.load_Listing(My_Subreddits_Listing(self.redditor.my_reddits(limit=None)))
            else:
                print("You must log in to view your subscribed subreddits. \nTo log in, type login <user>")
    
    def do_frontpage(self,line):
        """usage: frontpage
    Lists the posts on the user's frontpage if he or she is logged in, 
    and the default front page otherwise"""
        self.load_Listing(Frontpage_Listing(self.reddit.get_front_page(limit=None)))
    
    def do_login(self,line):
        """usage: login [user]
    Logs the user in."""
        try:
            if not line:
                self.reddit.login()
            else:
                self.reddit.login(username=line)
            self.redditor=self.reddit.user
            print("Welcome, ",self.redditor.name,"!")
            
            unread=list(self.redditor.get_unread())
            if unread:
                print("You have ",len(unread)," unread messages.")
            else:
                print("You don't have any unread messages.")
            
        except reddit.errors.InvalidUserPass:
            print("Invalid user or password. Try again")
        
    def do_user(self,line):
        """usage: user username
    Looks up the username and displays his or her overview"""
        if not line:
            line=input("Display overview for user ")
        #try:
        self.load_Listing(User_Listing(self.reddit.get_redditor(line)))
        #except:
            #print("The user "+line+" does not exist")

    def do_go(self,line):
        """usage: go number
    Goes to the specified item in the current page. Numbers are printed
    on the left of each item in every listing"""
        try:
            if(self.listing):
                goto=self.listing.go(int(line))

                if isinstance(goto,reddit.objects.Subreddit):
                    self.load_Listing(Subreddit_Listing(goto))
                elif isinstance(goto,reddit.objects.Submission):
                    self.load_Listing(Submission_Listing(goto))
                elif isinstance(goto,reddit.objects.Comment):
                    self.load_Listing(Comment_Listing(goto))
                else:
                    print("Can't go to a "+goto.__class__.__name__)
            else:
                print("There are no items to go to. Type 'frontpage' to see its items.")
            
        except ValueError:
            print("Invalid argument. For help, type 'help go' ")
            
    def do_open(self,line):
        #TODO: Special treatment for non-html urls
        try:
            if not line:
                obj=self.listing.reddit_object
            else:
                obj=self.listing.go(int(line))
                
            if isinstance(obj,reddit.objects.Subreddit):
                url="http://reddit.com"+obj.url
            elif isinstance(obj,reddit.objects.Comment):
                url=obj.permalink
            else:
                url=obj.url  
                       
            if sys.platform=='win32':
                os.system('start '+url);
            elif sys.platform=='darwin':
                os.system('open '+url)
            else: #hope it's posix compliant!
                os.system('xdg-open '+url)
                
        except ValueError:
            print("Invalid argument. For help, type 'help open'")
        except AttributeError:
            print("Can't open this")
            
    def do_inbox(self,line):
        """usage: inbox [filter]
    Displays the logged-in user's messages. If no filter is specified,
    all mesages are displayed
    
    filter    
        unread:
            Displays only unread messages and replies
        all:
            Displays all messages and replies
        sent:
            Displays messages sent by the user"""
    
        try:
            if not line or line=='all':
                line='all'
                filter='inbox' 
            else:
                filter=line
            generator=getattr(self.redditor,'get_'+filter)()
            self.load_Listing(Inbox_Listing(line,generator))
        except AttributeError:
            print("Invalid argument. For help, type 'help inbox'")
        
        
            
    def do_py(self,line):
        """usage: py expression
    Evaluates a python expression and prints its value. It's useful
    mostly for debugging"""
        try:
            print(eval(line))
        except Exception as e:
            print(e)

    def onecmd(self,command):
        try:
            return super().onecmd(command)
        except URLError:
            print("Can't reach reddit. There may be a problem with your connection or reddit may be down.")
    
        
        

if __name__ == "__main__":
    resh().cmdloop("""
                   MMMMM MMMMMM.     
                  MM   ?MM    MM     
                 MM     OM$   MM     
                 MM       MMMM7   
            MMMMMMMMMMM           
  NMMMM.MMMMM         MMMMM.MMMMN 
 MM   MMM                 MMM   MM
 MM  MM                     MM  MM  Welcome to resh,
 OMNMM     MMM       MMM     MMMMO  the reddit command-line shell.
   MM      MMM       MMM      MM    
   MM                         MM    This program is free software,  
   NM                         M     see COPYING for details.
    MM     MMM       MMM     MM   
     MNN     MMMMMMMMM     MMM    
       MMMM             MMMM      
          MMMMMMMMMMMMMMM        
       
Type 'frontpage' or 'subreddit <name>' to show posts
For a list of commands, type 'help'
To exit, type 'exit' (duh!) or press {}
""".format("CTRL-Z then Enter" if sys.platform=='win32' else "CTRL-D"  ))