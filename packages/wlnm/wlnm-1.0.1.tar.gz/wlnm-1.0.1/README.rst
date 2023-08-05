wlnm 1.0.1 (Weblogic Node Master)
======================

.. contents::

Changes
-------
**1.0.1**: Add web access function, user can access wlnm via browser.

**1.0.0**: Redesign wlnm as server based multi-user tool . add server & agent function .

**0.2.0**: Add remote contol ablitity , which can be used multi-machine weblogic admin

**0.1.0**: Initial drop

Requirements
-------------
1. Weblogic Server 9,10,11 installed . Weblogic domain and nodemanager server configued 

2. Python 2.6 + installed if run from source

3. pip if run from source


Screen shot & Tutorials 
-------------

http://weblogicnodemaster.blogspot.com.au/


Installation
------------

1. Install through pip.

    $ sudo pip install wlnm

2. Install from source.

    $ wget --no-check-certificate https://pypi.python.org/packages/source/w/wlnm/wlnm-1.0.1.tar.gz
    
    $ tar xvf wlnm-<version>.tar.gz
    
    $ sudo python setup.py install	

3. Install from RPM (build on Centos 64bit)
    
    $ wget --no-check-certificate https://pypi.python.org/packages/2.6/w/wlnm/wlnm-1.0.1-1.noarch.rpm
    
    $ sudo rpm -Uvh wlnm-<version>.noarch.rpm  

4. Run directly from git source if you don't have sudo access
    
    $ git clone https://github.com/yikaus/wlnm
    
    $ ./wlnm/wlnm/wlnm.py


issues with install psutil

As wlnm require psutil and when psutil install from source it will having gcc compile issue when you don't have python-dev installed.

If you don't want to install python dev enviroment ,  the walkaournd way for centos and redhat user is to install psutil as rpm.

    $ sudo yum install python-psutil

For windows user , you can download exe of python-psutil from it's website

https://code.google.com/p/psutil/downloads/list


Terminology
------------

1.wlnm server :

Server process is a daemon process which maintain central metadata store , it is a CLI server and allows wlnm client tool to connect.

2.wlnm webserver :

wlnm webserver is standalone web server based on bottle micro web framework which handle wlnm web console request , it is similar with wlnm server and can be used independently .


3.wlnm agent :

wlnm agent is a process started on target machine . server or webserver process will control agent to run command against the machine.

4.wlnm client:

wlnm client is a client connect to wlnm server to run command against target machine on which wlnm agent is running . 


Quick Start
------------

Let 's say we have 2 machine (machine1 & 2) running weblogic and one machine (machine 3) use to manage weblogic. 


1. Start webserver of wlnm by

	[user@machine1]$ wlnws start

default port 9100 , or use -p option set port


2. Run wlnm server and agent

	[user@machine1]$ wlns start

run wlnm server on default port 9099 , or use -p option set port

	[user@machine1]$ wlna start

	[user@machine2]$ wlna start

run wlnm agent listen default port 9098 on  both machine1 &2 , or use -p option set port

3.1 Run wlnm client connect to server

	[user@machine3]$ wlnm -s machine1

connect wlnm server with default port 9099 and coming to interactive mode.

	Weblogic Node Master

	Type help to load help page .

	wlnm>>

3.2 access http://serverhost:9100/ to enter web console . 

* Please note server and webserver you can start both or just start one of them if you only need cli or web access.

4. Command examples

First initialize two machines into server data store . 

	wlnm>> init machine1 9098

	wlnm>> init machine2 9098

when done list all register machine

	wlnm>> lsm

choose machine1 to operate

	wlnm>> use machine1

	wlnm(machine1)>>

list weblogic processes on this machine  

	wlnm(machine1)>>lsp

list weblogics installed on this machine

	wlnm(machine1)>>lswls

list domains configured on this machine

	wlnm(machine1)>>ls

disconnect machine1

	wlnm(machine1)>>disconnect

use machine2

	wlnm>> use machine2

	wlnm(machine2)>>

quit	

	wlnm(machine2)>>quit



5.stop server ,webserver and agent

	[user@machine1]$ wlns stop

	[user@machine1]$ wlnws stop

	[user@machine1]$ wlna stop

*tips 

You can use  option restart instead of option start when start server ,webserver and agent . It will first check running process.

Summary
-------

wlnm (Weblogic node master) is command tool to manage local weblogic installation and server instance ,node manager . It is based on metadata searching from config.xml and nodemanager.properties . You can use this tool directly without any configuration or enviroment setup . The tool itself will gathering all weblogic metadata infomations by go through all weblogic directories. It provides the function like list all domains , installation , servers and nodemanager information , start/kill local server instance also remote managedserver which through buildin WLST script. Welcome to test /use in your dev and test enviroment . As it is still in early version better not to use in production enviroment .

Usage Examples::

1. Run/Stop wlnm server process

    $ wlns start|stop|restart -p <port>

    *default port is 9099 .

    $ wlns start	# start wlnm server on localhost port 9099

    $ wlns start -p 19009 # start wlnm server on localhost port 19009

    $ wlns stop  # stop wlnm server

    *port is no need provided when stop server

2. Run/Stop wlnm web server

    $ wlnws start|stop|restart -p <port>

    *default port is 9100 .

    $ wlnws start	# start wlnm server on localhost port 9100

    $ wlnws start -p 19100 # start wlnm server on localhost port 19100

    $ wlnws stop  # stop wlnm server

    *port is no need provided when stop server

3. Run/Stop wlnm agent on target machine
    
    $ wlna start|stop|restart -p <port>

    *default port is 9098 .

    $ wlna start	# start wlnm agent on localhost port 9098

    $ wlna start -p 19008 # start wlnm agent on localhost port 19008

    $ wlna stop  # stop wlnm agent

    *port is no need provided when stop agent

4. Web console access

    http://serverhost:port/

5. Run wlnm client

The tool is used as interactive command mode , you need to enter wlnm prompt then use below command 

    
    wlnm -s <hostname> -p <serverport>

    *default server hostname is localhost , default server port is 9099

    Example:

    $ wlnm		#Connect to localhost 9099

    $ wlnm -s machine1 19980	#Connect to machine1 9099

6. Commands

    wlnm>> use <hostname> 

	 choose target machine to operate ,agent need to be started at the machine

    wlnm>> disconnect

	 Disconnect remote wlnm daemon connection

    wlnm>> init [agentHost] [agentPort]

	 initialise and register a agent and also fetch all related weblogic information from that machine . 

    wlnm>> lsm

	 list all registered machine .
    
    wlnm(<targethost>)>> ls
         List all weblogic domains with servers belong to it.

    wlnm(<targethost>)>> ls [domainName]
         List weblogic domain by domain name .

    wlnm(<targethost>)>> lsd 
          List weblogic all domains , not include servers  
         
    wlnm(<targethost>)>> lswls
         List all version weblogic installation as well as nodemnager informations

    wlnm(<targethost>)>> lsp
         List all running weblogic instances

    wlnm(<targethost>)>> init
         This tool will search all weblogic domain at frist time use , once domain configure changed you can research weblogic 
	 informations and update local store
    
    wlnm(<targethost>)>> startadmin [domainname]  
         Start admin server by domain name  . 

    wlnm(<targethost>)>> start [managedserverName] 
        start managed server by servername ,including remote server .

    wlnm(<targethost>)>> stop [managedserverName] 
        stop managed server by servername ,including remote server .

    wlnm(<targethost>)>> kill  [port|servername] 
        kill process of server by port or servername  
	* sometimes managed server is not able to be killed as autostart configured in weblogic domain.
    
    wlnm(<targethost>)>> nmstart [port] 
        start node manager by port. 

    wlnm>> help
        Show help page .

    wlnm>> quit
        quit weblogic node master. ( not avaliable from web console)







