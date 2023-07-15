import os

file_dir = input ("Write here the location of your file: ")

name = input ("Name the file: ")

save_it = input ("Where do you want to save it? ")

command = "curl -X POST -H \"Name: " + name + "\" -F \"file=@" + file_dir +   "\" \"192.168.1.18:8000/upload/" + save_it + "\""
os.system(command)

