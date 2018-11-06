#!/usr/bin/python3

#Resizes and re-encodes every video file in script's directory.
#Github: ...
#Video walkthrough: ...

#default parameters
codec = "libx264" #alternatives libx265 libvpx-vp9 libaom-av1  
height = -2 #height in pixels, e.g. 1080 or 720. -2 keeps original aspect ratio
width = -2 #width in pixels. -2 keeps original aspect ratio
fps = -1 #fps of output file, -1 keeps original fps
crf = 24 #range 1-51, 18-24 recommended. Lower value = better quality but larger file size
preset = 'faster' #ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, or veryslow. Veryslow results in a smaller file size for the same quality
long_filename = True #whether to include codec and crf value in output file name
process_outputs = False #whether to use output files from previous times script was run as new inputs
delete_input_files = False
file_formats = ['MP4', 'M4P', 'M4B', 'M4R', 'M4V', 'M4A', 'DIVX', 'EVO', 'F4V', 'FLV', 'AVI', 'QT', 'MXF', 'MOV', 'MTS', 'M2TS', 'MPG', 'MPEG', 'VOB', 'IFO', 'WEBM']


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
			Resizes and re-encodes every video file in script's directory.
			Default codec is x264 with a Constant Rate Factor (CRF) of 24.
				For most videos from cameras this will reduce the file size with no or little noticeable loss in quality.
			The script calls a ffmpeg command, 
				e.g.: ffmpeg -i video.mov -vf scale=-1:-1 -c:v libx264 -crf 24 video-r.mp4
			See https://unix.stackexchange.com/questions/28803/how-can-i-reduce-a-videos-size-with-ffmpeg
        '''))
parser.add_argument("-c", "--codec", default=codec, help='Default '+codec+'. libx264 is the fastest and most widely used. For better quality and compression, consider libx265. An alternative is libvpx-vp9. The new format libaom-av1 is experimental.')
parser.add_argument("-r", "--fps", default=fps, help='Default '+str(fps)+'. Frame rate (fps). -1 keeps original fps')
parser.add_argument("-crf", "--crf", default=crf, help='Default '+str(crf)+'. Range 1-51. Lower value means better quality but larger file size')
parser.add_argument("-pxh", "--height", default=height, help='Default '+str(height)+'. Height in pixels of output video, e.g. 720 or 1080. If not specified, keep input video\'s aspect ratio. If both -pxh and -pxw are -2, original dimensions are kept')
parser.add_argument("-pxw", "--width", default=width, help='Default '+str(width)+'. Width in pixels. If -2 or not specified, aspect ratio is kept')
parser.add_argument("-i", "-f", "--file", default='', help='name of input file, or substring to process any matching file name. If -1 or not specified, all video files in folder are processed.')
args = parser.parse_args()
codec = args.codec
fps = args.fps
crf = args.crf
height = args.height
width = args.width
process_file = args.file


#allow shortened codec argument
codec = codec.lower()
if ('264' in codec):
	codec = 'libx264'
if ('265' in codec):
	codec = 'libx265'
if ('hevc' in codec):
	codec = 'libx265'
if ('vp9' in codec):
	codec = 'libvpx-vp9'
if ('av1' in codec):
	codec = 'libaom-av1'


#set current dir to same directory as this .py file
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


#find all video files
input_files_all = []
for x in range(len(file_formats)):
	for file in glob.glob('*.'+file_formats[x]):
		input_files_all.append(file)
input_files_all = sorted(input_files_all, key=str.lower)
print("Video files in folder:")
for input_file in input_files_all:
	print(' '+input_file)
	
	
#filter out files not to process
input_files = []
for input_file in input_files_all:
	if (process_outputs == False):
		if '-x264-' in input_file:
			continue
		if '-x265-' in input_file:
			continue
		if '-vp9' in input_file:
			continue
		if '-av1-' in input_file:
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


#do this for each video file
for input_file in input_files:
	filename, file_extension = os.path.splitext(input_file)
	codec_info = ''
	codec_short = codec[-4:]
	out_file = filename
	file_type = 'mp4'
	if (codec == 'libvpx-vp9'):
		codec_info = ' -b:v 0'
		codec_short = 'vp9'
		file_type = 'webm'
	elif (codec == 'libaom-av1'):
		codec_info = ' -b:v 0 -strict experimental'
		codec_short = 'av1'
		file_type = 'mkv'
	elif (codec == 'libx264'):
		codec_short = 'x264'
	elif (codec == 'libx265'):
		codec_short = 'x265'
	
	if int(height) > -1 and int(width) > -1:
		out_file += '-'+str(width)+'x'+str(height)
	else:
		if int(height) > -1:
			out_file += '-'+str(height)+'h'	
		if int(width) > -1:
			out_file += '-'+str(width)+'w'
	if int(fps) > -1:
		out_file += "-"+str(fps)+"fps"
	if long_filename:
		out_file += "-"+codec_short+"-"+str(crf)+'.'+file_type
	else:
		out_file = filename+"-r."+file_type
	
	command = "ffmpeg -i \""+input_file+"\"" 
	if int(fps) > -1:
		command += " -r "+str(fps)
	command += " -vf scale="+str(width)+":"+str(height)
	command += " -c:v "+codec+" -crf "+str(crf)+codec_info
	command += " -preset "+preset
	command += " \""+out_file+"\""
	
	print('Run command:')	
	print(' ' + command)	
	os.system(command)	
	
	#delete input file?
	if delete_input_files:
		os.remove(input_file)
