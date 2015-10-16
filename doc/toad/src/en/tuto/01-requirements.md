# Before you start

## Account on the UNF server
In order to use TOAD at CRIUGM, you need to create an account on the UNF’s server. 
This account could either be an individual or a team account.

To obtain an account, or for all account-related inquiries, please contact the system administrator at the UNF [Mathieu Desrosiers](mailto:mathieu.desrosiers@criugm.qc.ca).

## Command line
TOAD toolbox is command-line-based that requires entries on a terminal.
Introduction to the use of command line and terminal is beyond the purpose of this tutorial.
However, there are plenty of resources available for those who need to become familiar with this requirement. 

For instance:

- [A generic tutorial](http://www.davidbaumgold.com/tutorials/command-line/)
- [Life hacker tutorial](http://lifehacker.com/5633909/who-needs-a-mouse-learn-to-use-the-command-line-for-almost-anything)

## SSH communication
The use of TOAD requires a remote connection between your computer and the UNF servers (even if you are working from the CRIUGM’s analysis room). To do so, it is strongly recommended to use the SSH protocol, which has been installed by default on all Apple and GNU/Linux based computers. For Windows, please refer to the various external documentation listed below:

- [Tutorial on Gamexe.net](http://www.gamexe.net/other/beginner-guide-ssh/)
- [Youtube video demo](https://www.youtube.com/watch?v=9CZphjhQxIQ)

## Add TOAD to your session

### Verify if TOAD is available
In order to use TOAD, you need to source the TOAD script when you open a session. 
To do so, open a terminal and establish a session by connecting to one of the UNF’s servers (via SSH)

~~~bash
# Replace 'username' by your UNF user ID
ssh -Y username@stark.criugm.qc.ca
~~~

To check the availability of TOAD, type the following command:

~~~bash
which toad
~~~

If the command returns a path such as `/usr/local/toad/...`, you are all set. 
If the command does not return anything, it means TOAD is not available for your session and you will need to add it.

### Add TOAD
If you are using TOAD on an occasional basis, you can source TOAD *each time* you connect to the server, by typing the following command line:

~~~bash
source  /usr/local/toad/etc/unf-toad-config.sh
~~~

Alternatively, you can add this line to your session’s profile if you want TOAD to be automatically sourced upon each connection:

1. Open/create the file .bash_profile’ using a text editor:

~~~bash
vi ~/.bash_profile
~~~

2. Switch to `edit` mode by pressing the **`i`** key to add text

3. Copy and paste this line to the end of the document (without the quotation marks): 'source  /usr/local/toad/etc/unf-toad-config.sh'

4. Save and quit the editor by first pressing the ESC’ key and then type **`:wq`** (do not forget to type the colon!)

5. To allow this change to take place, refresh the computer’s memory:

~~~bash
source ~/.bash_profile
~~~
 
