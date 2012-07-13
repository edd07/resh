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
    #friend command
    #document scriptable features
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
        #self.do_+ = self.do_upvote   : implemented in resh.onecmd (+ and - not allowed in names)
        #self.do_- = self.do_downvote : 

        
    
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
                
    def multiline_input(self,message):
        print(message)
        flag=True
        out=[]
        while flag:
            line=input()
            out.append(line)
            flag= line!=''
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
            #get subreddits
            self.load_Listing(My_Subreddits_Listing(self.redditor.my_reddits(limit=None)))
    
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
                print(Listing.ORANGERED,"You have ",len(unread)," unread messages.",Listing.RESET)
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
        """usage: open [number]
    Opens an item in a browser. If number isn't specified,
    the current listing is opened"""
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
        #TODO: Marking messages as read            
        if self.redditor:
            try:
                if not line or line=='all':
                    line='all'
                    filter='inbox' 
                else:
                    filter=line
                generator=getattr(self.redditor,'get_'+filter)(limit=None)
                self.load_Listing(Inbox_Listing(line,generator))
            except AttributeError:
                print("Invalid argument. For help, type 'help inbox'")
        else:
            raise reddit.errors.LoginRequired('')
        
    def do_reply(self,line):
        """usage: reply [number]
    Replies to a message, post or comment. If number isn't specified,
    the reply is posted to the current listing."""      
        try:
            if not line:
                f=self.listing.reddit_object.reply
            else:
                f=self.listing.go(int(line)).reply
            
            f(self.multiline_input("Write your reply below. When it's finished,\nleave a line blank and press Enter."))
        except ValueError:
            print("Invalid argument. For help, type 'help reply'")
        except AttributeError:
            print("Can't reply to this")
            
    def do_message(self,line):
        """usage: message [recipient]
    Send a private message to a user or a subreddit. If the recipient
    is a subreddit, prefix the name with '/r/'"""
        if self.redditor:
            try:
                if not line:
                    recipient=input("Send a message to: ")
                else:
                    recipient=line
                subject=input("Subject: ")
                message=self.multiline_input("Write your message below. When it's finished,\nleave a line blank and press Enter.")         
                self.reddit.compose_message(recipient, subject, message)
                print("Message sent.")
            except:
                print("There was a problem sending the message")
        else:
            raise reddit.errors.LoginRequired("")
            
    def do_upvote(self,line):
        """usage: upvote [number]
    Upvotes a comment or submission. If number isn't specified,
    the current listing is upvoted"""
        try:
            if not line:
                self.listing.reddit_object.upvote()
            else:
                self.listing.go(int(line)).upvote()
            
            print("Upvoted")
        except ValueError:
            print("Invalid argument. For help, type 'help upvote'")
        except AttributeError:
            print("Can't vote on this")
            
    def do_downvote(self,line):
        """usage: downvote [number]
    Downvotes a comment or submission. If number isn't specified,
    the current listing is downvoted"""
        try:
            if not line:
                self.listing.reddit_object.downvote()
            else:
                self.listing.go(int(line)).downvote()
            
            print("Downvoted")
        except ValueError:
            print("Invalid argument. For help, type 'help downvote'")
        except AttributeError:
            print("Can't vote on this")
    
    def do_save(self,line):
        """usage: save [number]
    Saves a submission. If number isn't specified,
    the current submission is saved"""
        try:
            if not line:
                self.listing.reddit_object.save()
            else:
                self.listing.go(int(line)).save()
            
            print("Saved")
        except ValueError:
            print("Invalid argument. For help, type 'help save'")
        except AttributeError:
            print("Can't save this")
    
    def do_unsave(self,line):
        """usage: unsave [number]
    Un-saves a submission. If number isn't specified,
    the current submission is un-saved"""
        try:
            if not line:
                self.listing.reddit_object.unsave()
            else:
                self.listing.go(int(line)).unsave()
            
            print("Unsaved")
        except ValueError:
            print("Invalid argument. For help, type 'help unsave'")
        except AttributeError:
            print("Can't unsave this")
            
    def do_saved(self,line):
        """usage: saved
    Displays the logged-in user's saved links"""
        self.load_Listing(Saved_Listing(self.reddit.get_saved_links(limit=None)))
            
            
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
             # +/- shorthand commands for voting
            if command=='+':
                return super().onecmd('upvote')
            elif command=='-':
                return super().onecmd('downvote')
            else:
                return super().onecmd(command)
        except URLError:
            print("Can't reach reddit. There may be a problem with your connection or reddit may be down.")
        except reddit.errors.LoginRequired:
            print("Login is required. To log in, type 'login <username>'")
    
        
        

if __name__ == "__main__":
    resh().cmdloop("""
                   ##### ######.     
                  ##   ?##    ##     
                 ##      #$   ##     
                 ##       ####7   
            ###########           
  N####.####         #####.####N 
 ##   ###                 ###   ##
 ##  ##                     ##  ##  Welcome to resh,
  ####     ###       ###     ####   the reddit command-line shell.
   ##      ###       ###      ##    
   ##                         ##    This program is free software,  
   ##                         #     see COPYING for details.
    ##     ###       ###     ##   
     ###     #########     ###    
       ####             ####      
          ###############        
       
Type 'frontpage' or 'subreddit <name>' to show posts
For a list of commands, type 'help'
To exit, type 'exit' (duh!) or press {}
""".format("CTRL-Z then Enter" if sys.platform=='win32' else "CTRL-D"  ))