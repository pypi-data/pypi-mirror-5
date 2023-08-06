======
cstyle
======
Use c-style braces instead of indentation. This is an encoding, you can also import this module in sites.py, it will register the encoding on import.

to use this, add the magic encoding comment to your source file::

    # coding: cstyle
    
Then you can import it to run it. or if you added the encoding to your sites.py, you can use idle to view the decoded file.
Use notepad++ or the editor of your choice.
Do not use this. DO NOT USE THIS. and do not use this. this works, but this is not a good idea.

Currently just works for "if|elif|else|for|while|def|with" statements. do not mix indentation and braces. you can do that, but it is not recommended.
Treat this module just as a toy, or if you have any special purpose to use it. This program is open source, lgpl, you can edit or use it for free.

One usage for this module can be reducing source code size (compressing).

You can also decode cstyle literals::

    import cstyle
	a = b'cstyle code'
	a.decode('cstyle')
	
To know how to code with cstyle examine the examples provided here. This is not an alpha release, this is not a beta release, this is not a release at all. this is not a real program, at least at this point. use for educational purposes or whatever. There's no warranty. There might be parsing errors, it is tested on the code provided in the examples here.
	
What this can do?
=================
This will convert::

    if(1 in {1,2,3}){
        print(5)
        for(x in c){
            print(c)
        }
    }
	
To this::

    if(1 in {1,2,3}):
        print(5)
        for x in c:
            print(c)
		
it works for messy code too. see how this can work on this long oneline code::

    import time;while(1){while(3){break}if(999>x){time.sleep(1);if(2){print("This is a BAD idea.");print("Or a good one?");print("For me, this is just for fun.");print("C-Style Coding");if(1){def xyz(a,b,c){"""this is a stupid function""";print("if(2){print(\\"hi\\")}");if(a>b){return c}elif(a>c){return b}else{return a}}}with(open("file") as f){pass}}}if(1 in {1,2,3}){print(5);for(x in c){print(c)}}}
	
The result from the previous is::

    import time
    while(1):
        while(3):
            break
        if(999>x):
            time.sleep(1)
            if(2):
                print("This is a BAD idea.")
                print("Or a good one?")
                print("For me, this is just for fun.")
                print("C-Style Coding")
                if(1):
                    def xyz(a,b,c):
                        """this is a stupid function"""
                        print("if(2){print(\"hi\")}")
                        if(a>b):
                            return c
                        elif(a>c):
                            return b
                        else:
                            return a
                with open("file") as f:
                    pass
        if(1 in {1,2,3}):
            print(5)
            for x in c:
                print(c)



Project Info
============

Github project page: https://github.com/pooya-eghbali/cstyle
Mail me at: persian.writer [at] Gmail.com
