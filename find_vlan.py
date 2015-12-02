#!/usr/bin/env python
'''
find_vlans.py
Created on Feb 11, 2015
Updated on March 9, 2015
Python 2.7.x only
connects to APIC and gets the entire fabric worth of VLANs and maps them to paths
'''
__appname__ = 'find_vlans'
__version__ = '1.0.1'
__license__ = '?'

import operator
import sys
from cobra.model.fabric import Inst
from cobra.model.fabric import Topology
from cobra.mit.session import LoginSession
from cobra.mit.access import MoDirectory
from cobra.model.fv import AttEntityPathAtt
import getpass
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings() 
import re
import csv
import Tkinter
from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import logging

# Make a global logging object.
x = logging.getLogger("logfun")
x.setLevel(logging.INFO)                                           # CRITICAL FATAL ERROR WARNING WARN INFO DEBUG NOTSET  
h = logging.StreamHandler()
f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
h.setFormatter(f)
x.addHandler(h)

## Global Variable(s)
skipMoClasses = ('fvConnDef','fvEpPCont','polUni')

def login_gui():
    root =Tk()
    root.minsize(700,400)
    root.title("Cisco APIC Login")
    ment_1 = StringVar()
    ment_2 = StringVar()
    ment_3 = StringVar()
    label_1 = Label(root, text = "ip address").pack()
    mentry = Entry(root,textvariable = ment_1 ).pack()
    label_2 = Label(root, text = "username").pack()
    mentry_2 = Entry(root,textvariable = ment_2 ).pack()
    label_3 = Label(root, text = "password").pack()
    mentry_3 = Entry(root, show="*", width=20, bg = "gray",textvariable = ment_3 ).pack()
    frame = Frame(root)
    frame.pack()    
    button = Button(frame,text = "ok", command = lambda: close_device(root), bg = "gray",fg = "black")
    button.pack()
    root.mainloop()    
    apicIP = ment_1.get()
    user = ment_2.get()
    pw = ment_3.get()
    
    try:
        ## login to APIC
        apicUrl = 'https://'+apicIP                                                         # defaulting to https
        loginSession = LoginSession(apicUrl, user, pw,secure=False)
        moDir = MoDirectory(loginSession)
        moDir.login()
    except:
        print "the username and/or password you entered is incorrect"
                
    return apicUrl,moDir

def close_device(root):
    root.destroy()

def login_cli(apicIP,userID,pw):
    try:
        ## login to APIC
        if apicIP == False:
            apicIP = raw_input("\nWhat is the APIC IP ? Format xxx.xxx.xxx.xxx\n")
            userID = raw_input("\nUser ID: ")
            pw = getpass.getpass().strip("/\r")
        apicUrl = 'https://'+apicIP                                                        # defaulting to https
        loginSession = LoginSession(apicUrl, userID, pw,secure=False)
        moDir = MoDirectory(loginSession)
        moDir.login()
    except:
        print "the username and/or password you entered is incorrect"
                
    return apicUrl,moDir
    
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def sort_it(onkey1,rev, origin_list):
    """Return text sorted by line, remove empty lines and strip trailing whitespace."""
    retFileContent1 = []
    try: 
#         print "\n>> %s sort >>" % onkey1
        for foo in sorted(origin_list, cmp=None, key=operator.itemgetter(onkey1),reverse=rev):
            retFileContent1.append(foo) 
    except:
        print sys.exc_info()[0]
        
    return retFileContent1

def find_vlans(moDir):
    endpoints = []    
    count = 0
    i = 0
    try:
        fvIfConnV = moDir.lookupByClass('fvIfConn')
        for i in range(0,2000):
            fvIfConn = fvIfConnV[i]
            temp = {'encap':"",'tn':"",'epg':"",'node':"",'path':"",'pathtype':""}                
            for fvIfConni in list(fvIfConnV[i].dn.rns)[::-1]:
#                 print '== i =>',i, fvIfConni.meta.moClassName   
                pass                                           
            for fvIfConnii in list(fvIfConnV[i].dn.rns)[::-1]:
#                 print '============> 2', fvIfConnii.meta.moClassName       
#                 print tuple(fvIfConnii.namingVals)
                pass                
                if (len(fvIfConnii.meta.namingProps) != 0):
                    if fvIfConnii.meta.moClassName  in skipMoClasses: 
                        pass                    
                    if fvIfConnii.meta.moClassName == 'fvIfConn':
                        temp['encap'] = fvIfConnii._Rn__namingVals[0]                                                                             
                    if fvIfConnii.meta.moClassName == 'fvStPathAtt':                # EPG to Path Attachment
                        temp['pathtype'] = 's'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]
                        if 'stpathatt-' in fvIfConnii._Rn__namingVals[0]:
                            st1 = fvIfConnii._Rn__namingVals[0]
                            st2 = (re.findall("stpathatt-(.+)", str(st1)))
                            st3 = str(st2).strip("[']")
                            temp['path'] = str(st3)                                            
                    if fvIfConnii.meta.moClassName == 'fvDyPathAtt':                # EPG to Path Attachment
                        temp['pathtype'] = 'd'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]
                        if 'pathep-' in fvIfConnii._Rn__namingVals[0]:
                            dy1 = fvIfConnii._Rn__namingVals[0]
                            dy2 = (re.findall("pathep-(.+)", str(dy1))) 
                            dy3 = str(dy2).strip("[']")
                            temp['path'] = str(dy3)
                        if 'lsnode-' in fvIfConnii._Rn__namingVals[0]:
                            dy1 = fvIfConnii._Rn__namingVals[0]
                            dy2 = (re.findall("lsnode-(.+)", str(dy1))) 
                            dy3 = str(dy2).strip("[']")
                            temp['path'] = str(dy3)
                        if 'dyatt-' in fvIfConnii._Rn__namingVals[0]:
                            dy1 = fvIfConnii._Rn__namingVals[0]
                            dy2 = (re.findall("pathep-\(.+)", str(dy1))) 
                            dy3 = str(dy2).strip("[']")
                            temp['path'] = str(dy3)                                      
                    if fvIfConnii.meta.moClassName == 'fvAttEntityPathAtt':         # EPG to Path Attachment
                        temp['pathtype'] = 'a'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]                        
                    if fvIfConnii.meta.moClassName == 'fvExtStPathAtt':             # EPG to Path Attachment
                        temp['pathtype'] = 'e'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]                    
                    if fvIfConnii.meta.moClassName == 'fvRsDyPathAtt':               #network path endpoint
                        temp['pathtype'] = 'r'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]
                    if fvIfConnii.meta.moClassName == 'fvRsPathAtt':                 #network path endpoint
                        temp['pathtype'] = 'rp'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]
                    if fvIfConnii.meta.moClassName == 'fvRsStPathAtt':               #network path endpoint
                        temp['pathtype'] = 'rs'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]
                    if fvIfConnii.meta.moClassName == 'fvAPathAtt':                 #network path endpoint
                        temp['pathtype'] = 'ap'
                        temp['path'] = fvIfConnii._Rn__namingVals[0]                                                                           
                    if fvIfConnii.meta.moClassName == 'fvLocale':
                        temp['node'] = 'Node-' + fvIfConnii._Rn__namingVals[0]                                                             
                    if (fvIfConnii.meta.moClassName == 'fvRtdEpP') or (fvIfConnii.meta.moClassName =='fvEpP'):
                        temp['tn'] = fvIfConnii._Rn__namingVals[0]
                        if 'tn-' in fvIfConnii._Rn__namingVals[0]:
                            tn1 = fvIfConnii._Rn__namingVals[0]
                            tn2 = (re.findall("tn-(.+)/ap", str(tn1)))
                            tn3 = str(tn2).strip("[']")
                            temp['tn'] = str(tn3)                        
                        if 'epg-' in fvIfConnii._Rn__namingVals[0]:                        
                            EpP1 = fvIfConnii._Rn__namingVals[0]
                            EpP2 = (re.findall("epg-(.+)", str(EpP1)))
                            EpP3 = str(EpP2).strip("[']")
                            temp['epg'] = str(EpP3)
                        else:
                            temp['epg'] = 'N/A'                                                   
                    count += 1
            endpoints.append(temp)            
    except:
        pass
             
    return endpoints

def dic_0_Term(apicUrl,ep):
    headerz =   "{:12s}{:20s}\n".format('APIC Url > ',apicUrl)
    print ' ', headerz
    headerz =   "{:<12s}{:<15s}{:<20s}{:<9s}/{:<20s}{:<10s}\n".format("Encap","Tenant","EPG","NODE","PATH","PATH_TYPE")
    print ' ', headerz
    print '========================================================================================'    
    for i in ep:
        if 'vlan-' in i["encap"]:
            linez = "{:<12s}{:<15s}{:<20s}{:<9s}/{:<15s}{:>10s}" .format(i["encap"],i["tn"],i["epg"],i["node"],i["path"],i["pathtype"])
            print ' ',linez
    print '========================================================================================\n'
    headerz0 =       "{:<10s}".format("Path Type:")
    print ' ', headerz0
    headerz1 =       "           {:<95s}".format("s =Static, d =Dynamic, a =Attached Entity, e =External Static")
    print ' ', headerz1
    headerz2 =       "           {:<95s}\n".format("rd =fvRsDyPathAtt, rp =fvRsPathAtt, rt =fvRsStPathAtt, ap =fvAPathAtt")
    print ' ', headerz2

def dic_1_GUI(apicUrl,ep):
    
    def new_command():
        """clear the text area so you can start new text"""         
        answer = tkMessageBox.askyesnocancel("New", "Do you want to save this file?")
        if answer == False:
            textbox.delete(0.0, 'end')
        elif answer == True:
            save_command()
            textbox.delete(0.0, 'end')
        else:
            pass
    
    def open_command():
        fout = tkFileDialog.askopenfile(parent=root,mode='rb',title='Select a file')
        if fout != None:
            new_command()
            contents = fout.read()
            textbox.insert('1.0',contents)
            fout.close()
     
    def save_command():
        """get a fileOpen and save your text to it"""
        # default extension is optional, will add .txt if missing
        fout = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        text2save = str(textbox.get(0.0, 'end'))
        fout.write(text2save)
        fout.close()
    
    def save_as_command():
        """get a filename and save your text to it"""
        # default extension is optional, will add .txt if missing
        fout = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        text2save = str(textbox.get(0.0, 'end'))
        fout.write(text2save)
        fout.close()
    
    def print_command():
        """print this page"""
        # default extension is optional, will add .txt if missing
        pass
    
    def exit_command():
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
            root.destroy()
               
    def view_help_command():  
        help =Tk()
        help.minsize(700,400)
        help.title("Find_vlans Help Doc")
        scrollbar = Scrollbar(help, orient = None, command = None)
        scrollbar.pack(expand=FALSE,side=RIGHT, fill=BOTH)                
        textbox = Text(help,  xscrollcommand=scrollbar.set,  yscrollcommand=scrollbar.set)
        textbox.insert(END, str('  \n'))
        textbox.insert(END, str('  \n'))    
        headerz =       "{:<60s}\n".format("                 This is View Help command for find_vlans script ")
        textbox.insert(END, headerz)
        textbox.insert(END, str('  ==========================================================================\n'))        
        textbox.insert(END, str('  find_vlans script finds all the vlans of a Fabric\n'))
        textbox.insert(END, str('  The options value will select which output to create \n'))
        textbox.insert(END, str('  The default is to generate GUI output\n'))
        textbox.insert(END, str('  # python find_vlans -t \n'))
        textbox.insert(END, str('  \n'))
        textbox.insert(END, str('  -l\', \'--login\', Login with GUI\',         example: # python find_vlans -l \n'))
        textbox.insert(END, str('  -t\', \'--term\',  Display in Terminal\',    example: # python find_vlans -t \n'))
        textbox.insert(END, str('  -c\', \'--cli\',   Display in CLI\',         example: # python find_vlans -c \n'))
        textbox.insert(END, str('  -g\', \'--gui\',   Display in GUI\',         example: # python find_vlans -g \n'))
        textbox.insert(END, str('  -e\', \'--excel\', Display in Excel file\',  example: # python find_vlans -e \n'))
        textbox.insert(END, str('  -a\', \'--all\',   Display in Term,CLI,GUI and Excel file\',                  \n'))
        textbox.insert(END, str('                                           example: # python find_vlans -a \n'))
        textbox.insert(END, str('                                           example: # python find_vlans -t -e \n'))
        textbox.insert(END, str('  \n'))
        textbox.insert(END, str('  Path Types are: \n'))
        textbox.insert(END, str('  s =Static,d =Dynamic,a =Attached Entity,e =External Static \n'))
        textbox.insert(END, str('  rd =fvRsDyPathAtt, rp =fvRsPathAtt, rt =fvRsStPathAtt, ap =fvAPathAtt \n'))
        scrollbar.config(command=textbox.xview)
        scrollbar.config(command=textbox.yview)    
        textbox.pack(expand=Y, side=LEFT, fill=BOTH) 
        help.mainloop()

    def about_command():
        label = tkMessageBox.showinfo("About", "  ACI  find_vlans  tool \n (c) Cisco Systems, Inc. 2015 Copyright \n Credits: Ninous William Bebla \n Mike Timm \n Shae Eastman")       
    
    def dummy():
        print "I am a Dummy Command, I will be removed in the next step"
    
    ## widget creation
    root = Tkinter.Tk(className=" ACI find_vlans tool ")
    textPad = ScrolledText(root, width=100, height=35)
    root.minsize(900,600)
    root.resizable(100,35)
    root.title("Cisco APIC vlan")
    menu = Menu(root)
    root.config(menu=menu)    
    # File options    
    filemenu = Menu(menu)
    menu.add_cascade(label="File ", menu=filemenu)
    filemenu.add_command(label="New ", command=new_command)
    filemenu.add_command(label="Open... ", command=open_command)
    filemenu.add_command(label="Save ", command=save_command)
    filemenu.add_command(label="Save As ", command=save_as_command)
    filemenu.add_separator()
    filemenu.add_command(label="Print... ", command=print_command)
    filemenu.add_command(label="Page Setup... ", command=dummy)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=exit_command) 
    # Help Options
    helpmenu = Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label='View Help', command=view_help_command)
    helpmenu.add_separator()
    helpmenu.add_command(label='About This Script', command=about_command)           
    scrollbar = Scrollbar(root, orient = None, command = None)
    scrollbar.pack(expand=FALSE,side=RIGHT, fill=BOTH)            
    textbox = Text(root,  xscrollcommand=scrollbar.set,  yscrollcommand=scrollbar.set)
    headerz =       "{:12s}{:<20s}\n".format('APIC Url > ',apicUrl)
    textbox.insert(END, headerz)    
    headerz =       "{:<12s}{:<15s}{:<20s}{:<9s}/{:<20s}{:<10s}\n".format("Encap","Tenant","EPG","NODE","PATH","PATH_TYPE")
    textbox.insert(END, headerz)
    textbox.insert(END, str('===========================================================================================\n'))   
    for i in ep:
        if 'vlan-' in i["encap"]:
            linez = "{:<12s}{:<15s}{:<20s}{:<9s}/{:<15s}{:>10s}\n" .format(i["encap"],i["tn"],i["epg"],i["node"],i["path"],i["pathtype"])
            textbox.insert(END, str(linez))
    textbox.insert(END, str('  \n'))
    textbox.insert(END, str('  \n'))
    textbox.insert(END, str('===========================================================================================\n'))
    textbox.insert(END, str('  Path Type: \n'))        
    headerz1 =       "            {:<12s}\n".format("s =Static, d =Dynamic, a =Attached Entity, e =External Static")
    textbox.insert(END, headerz1)
    headerz2 =       "            {:<12s}\n".format("rd =fvRsDyPathAtt, rp =fvRsPathAtt, rt =fvRsStPathAtt, ap =fvAPathAtt")
    textbox.insert(END, headerz2) 
    scrollbar.config(command=textbox.xview)
    scrollbar.config(command=textbox.yview)    
    textbox.pack(expand=Y, side=LEFT, fill=BOTH) 
    root.mainloop()

def dic_2_excel(apicUrl,ep):
    count = 0   
    result = open("newfile_1.csv",'wb')
    fieldnames = ['APIC Url > ',apicUrl]
    writer = csv.DictWriter(result, fieldnames=fieldnames, dialect='excel')
    writer.writeheader()
    fieldnames = ['Encap','Tenant','EPG','NODE','PATH','PATH_TYPE']
    writer = csv.DictWriter(result, fieldnames=fieldnames, dialect='excel')
    writer.writeheader()
    for i in ep:
        if 'vlan-' in i["encap"]:
            writer.writerow({'Encap': i["encap"],'Tenant':i["tn"],'EPG': i["epg"],'NODE': i["node"],'PATH': i["path"],'PATH_TYPE': i["pathtype"]})
    writer.writerow({'Encap':""})
    fieldnames = ['Path Types:','s =Static, d =Dynamic, a =Attached Entity, e =External Static']
    writer = csv.DictWriter(result, fieldnames=fieldnames, dialect='excel')
    writer.writeheader()
    fieldnames = ['','rd =fvRsDyPathAtt, rp =fvRsPathAtt, rt =fvRsStPathAtt, ap =fvAPathAtt']
    writer = csv.DictWriter(result, fieldnames=fieldnames, dialect='excel')
    writer.writeheader()
    result.close

def main(args):
    ##
    try:
        onkey1 = 'encap'
        rev = False
        if args.sort_key:
            onkey1 = args.sort_key 
            rev = False
        if args.sort_key_reverse:
            onkey1 = args.sort_key
            rev =True    
        if (args.userID != False):
            apicUrl,moDir = login_cli(args.ip,args.userID,args.password.strip("/\r"))
            eps = find_vlans(moDir)
            ep  = sort_it(onkey1,rev, eps)
        else:            
            if (args.login == True):
                apicUrl,moDir = login_gui()
                eps = find_vlans(moDir)
                ep  = sort_it(onkey1,rev, eps)
            else:
                apicUrl,moDir = login_cli(args.ip,args.userID,args.password)
                eps = find_vlans(moDir)
                ep  = sort_it(onkey1,rev, eps)
        print
        print
        print
        if (args.term  == False):
            dic_0_Term(apicUrl,ep)    
        if (args.excel == True):   
            dic_2_excel(apicUrl,ep)
        if args.cli    == True: 
            print ep
        if (args.gui   == True):     
            dic_1_GUI(apicUrl,ep)
        if (args.all   == True):
            # print ep
            dic_2_excel(apicUrl,ep)
            dic_1_GUI(apicUrl,ep)    
        print '\nDone'
    except:
        print sys.exc_info()[0]

##
if __name__ == '__main__':
    try:
        import argparse
        parser = argparse.ArgumentParser(description='Find all the vlans for this Fabric', argument_default=False)
        parser.add_argument('-l', '--login', help='Use GUI to login', action = 'store_true', default= False,required=False)
        parser.add_argument('-t', '--term', help='Display in Terminal', action = 'store_true', default= False,required=False)
        parser.add_argument('-c', '--cli', help='Display in CLI', action = 'store_true', default= False, required=False)
        parser.add_argument('-g', '--gui', help='Display in GUI',action = 'store_true',default= False, required=False)
        parser.add_argument('-e', '--excel', help='Display in Excel file',action = 'store_true', default= False, required=False)        
        parser.add_argument('-i', '--ip', help='Enter server IP address', default= False, required=False)
        parser.add_argument('-u', '--userID', help='Enter user ID', default= False, required=False)
        parser.add_argument('-p', '--password', help='Enter password', default= False, required=False)
        parser.add_argument('-s', '--sort_key', help='sort on heading. for example: -s encap or tn or epg or node or path or pathtype', default= False, required=False)
        parser.add_argument('-rs', '--sort_key_reverse', help='sort on heading. for example: -s encap or tn or epg or node or path or pathtype. Default is encap.', default= False, required=False)         
        parser.add_argument('-a', '--all', help='Display in Term,CLI,GUI and Excel file', action = 'store_true',default= False, required=False)        
        args = parser.parse_args()
        main(args)        
    except:
        print sys.exc_info()[0]
