import subprocess
import os

print("----------------------\nChoose file\n----------------------\n ")
demo_folder = "/Users/shaesaert/Documents/GitHub/SCA/Demo_CommWindow_TuLiP"
abspath = os.path.dirname(os.path.abspath(__file__))

print("1. Demo file \n2. Reduced demo file \n3. Give string" )
demo = raw_input('Use Demo file : [1]/2/3')
if demo == "3":
    name_window = raw_input('Name of xml file:')
    XMLfile = name_window
elif (demo == "2"):
    XMLfile = "Demo_CommWindow_red"
else:
    XMLfile = "Demo_CommWindow"




print("----------------------\nRemove content autocode folder\n----------------------\n")
subprocess.check_call(["make", "autoclean"], cwd=demo_folder)

print("----------------------\nAutocode\n----------------------\n")
subprocess.check_call(["make", "auto", 'CLASSNAME = ' + XMLfile], cwd=demo_folder)

print("----------------------\nExecute make clean all\n----------------------\n")
subprocess.check_call(["make", "clean"], cwd=demo_folder)
subprocess.check_call(["make", "all"], cwd=demo_folder)

print("----------------------\nShow demo? Wait for user input\n----------------------\n ")
demo = raw_input('Simulate demo: y/[n] ')
if demo == "y":
    subprocess.check_call(["./setup.py"],cwd=demo_folder)
