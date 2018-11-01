#!/usr/bin/python3

#Resizes every image file in script's directory.
#Github: ...
#Video walkthrough: ...

#default parameters
out_format = '' #default keep original, specify to force 'jpg', 'png', etc  
height = 2160 #height in pixels, -1 keeps original aspect ratio
width = 3840 #width in pixels, -1 keeps original aspect ratio
fitbox = 1 #0 or 1. Whether to keep aspect ratio while neither height nor width can be more than specified
long_filename = True #whether to include dimensions etc in output file name
process_outputs = False #whether to use output files from previous times script was run as new inputs
delete_input_files = False
file_formats = ['JPG', 'JPEG', 'PNG', 'BMP', 'GIF', 'TIF', 'TIFF']


'''
Copyright (c) 2018 JP Janssen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import os
import glob
import sys
import argparse
import textwrap

#parse arguments (if any, else use default)
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
		description:
			Resizes every image file in script's directory, and optionally forces a new format, e.g. jpg or png.
			The script calls a ffmpeg command, 
				e.g.: ffmpeg -i image.jpg -vf scale=3840:-1 image-r.jpg
        '''))
parser.add_argument("-of", "--format", default=out_format, help='Default \''+out_format+'\'. Specify to force jpg, png, etc output file')
parser.add_argument("-pxh", "--height", default=height, help='Default '+str(height)+'. Height in pixels of output file. If not specified, keep input image\'s aspect ratio. If both -pxh and -pxw are -1, original dimensions are kept')
parser.add_argument("-pxw", "--width", default=width, help='Default '+str(width)+'. Width in pixels. If -1 or not specified, aspect ratio is kept')
parser.add_argument("-fit", "--fitbox", default=fitbox, help='Default '+str(fitbox)+'. Must be 0 or 1. If 1, keep aspect ratio, and neither width nor height can be larger than specified values')
parser.add_argument("-i", "-f", "--file", default='', help='name of input file, or substring to process any matching file name. If -1 or not specified, all image files in folder are processed.')
args = parser.parse_args()
out_format = args.format
height = args.height
width = args.width
fitbox = args.fitbox
process_file = args.file

#remove any leading . from file extension
out_format = out_format.strip('.')

#set current dir to same directory as this .py file
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


#find all image files
input_files_all = []
for x in range(len(file_formats)):
	for file in glob.glob('*.'+file_formats[x]):
		input_files_all.append(file)
input_files_all = sorted(input_files_all, key=str.lower)
print("Image files in folder:")
for input_file in input_files_all:
	print(' '+input_file)
	
	
#filter out files not to process
input_files = []
for input_file in input_files_all:
	if (process_outputs == False):
		if '-fit-' in input_file:
			continue
		if '-r-' in input_file:
			continue
		if '-r.' in input_file:
			continue
	if (process_file != ''):
		if process_file not in input_file:
			continue
	input_files.append(input_file)
print("Process these files:")
for input_file in input_files:
	print(' '+input_file)


#do this for each image file
for input_file in input_files:
	filename, file_extension = os.path.splitext(input_file)
	if out_format != '':
		file_extension = '.'+out_format 
	out_file = filename
	if (long_filename):
		if fitbox == 1:
			out_file += '-fit'
		else:
			out_file += '-r'
		if int(height) > -1 and int(width) > -1:
			out_file += '-'+str(width)+'x'+str(height)
		else:
			if int(height) > -1:
				out_file += '-'+str(height)+'h'	
			if int(width) > -1:
				out_file += '-'+str(width)+'w'
	else:
		out_file = filename+"-r"
	out_file += file_extension.lower()
	
	if fitbox == 1:
		command = "ffmpeg -i \""+input_file+"\" -vf scale=w="+str(width)+":h="+str(height)+":force_original_aspect_ratio=decrease \""+out_file+"\""	
	else:
		command = "ffmpeg -i \""+input_file+"\" -vf scale="+str(width)+":"+str(height)+" \""+out_file+"\""
	
	print('Run command:')	
	print(' ' + command)	
	os.system(command)	
	
	#delete input file?
	if delete_input_files:
		os.remove(input_file)
