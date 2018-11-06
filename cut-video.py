#!/usr/bin/python3

#Cuts a video at specified start and end time(s) and saves copy(ies) to new file(s)
#Github: ...
#Video walkthrough: ...

#default parameters
ffmpeg_loglevel = 31 #see https://ffmpeg.org/ffmpeg.html#Generic-options
delete_input_file = False #DANGEROUS, use only if you have BACKUP of input file
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
import math

#parse arguments (if any, else use default)
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
		description:
			Cuts a video at specified start and end time(s) and saves copy(ies) to new file(s)
			First argument is file name, then pairs of start and end times, as many as you like, e.g.: 
				
				cut-video.py myvid.mp4   4.5-2:14   5:13.7-10:00
					
			Be aware that FFmpeg seeks for the nearest keyframe. Therefore the cut may not be at the exact timestamp.			
			FFmpeg copies the bitrstream, and the new file is a lossless copy.
        '''))
parser.add_argument('arguments', metavar='args', type=str, nargs='+', help='file start-end [start-end ...]')
args = parser.parse_args()
inputs = args.arguments


try_file = inputs[0]
clip_start = []
clip_end = []


#function converts timestamp to seconds  
#allow two input formats; HOURS:MM:SS or HHMMSS
# e.g. '1:02' = '102' = 62s or '1:01:02.5' = '010102.5' = 3662.5s   
def tsToSec(ts):
	parts = str(ts).split(':')
	if len(parts) == 1:
		x = float(parts[0])
		hr = math.floor(x / 10000)
		min = math.floor((x - hr * 10000) / 100)
		sec = x - hr * 10000 - min * 100
		return float(hr*3600 + min*60 + sec)
	if len(parts) == 2:
		return int(parts[0]) * 60 + float(parts[1])
	if len(parts) == 3:
		return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
	return -1
	
#function converts seconds to HOURS:MM:SS timestamp 
def secToTs(sec):
	hr = math.floor(sec / 3600)
	min = math.floor((sec - hr * 3600) / 60)
	sec = sec - hr * 3600 - min * 60
	if hr>0:
		return '%02d'%hr +':'+ '%02d'%min +':'+ '%04.1f'%sec
	if min>0:
		return '%02d'%min +':'+ '%04.1f'%sec
	return '%04.1f'%sec
	
	
#function returns shortened timestamp for file name, e.g. 12:34.5 => 1234  
def filenameTime(sec):
	#input is time in sec
	hr, sec = divmod(sec,3600)
	min, sec = divmod(sec,60)
	if hr == 0:
		return '%02d'%min + '%02d'%math.floor(sec)
	return '%02d'%hr +'%02d'%min + '%02d'%math.floor(sec)
	
#prepare list of start and end times
for i, input in enumerate(inputs):
	if i == 0:
		continue
	times = input.split('-')
	clip_start.append(tsToSec(times[0]))
	clip_end.append(tsToSec(times[1]))

	
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
#print("Video files in folder:")
#for input_file in input_files_all:
	#print(' '+input_file)
	
	
#find the file to process
file_found = False
for input_file in input_files_all:
	if try_file in input_file:
		file_found = True
		selected_file = input_file
		continue
print("Process this file:")
if file_found == False:	
	print(" File not found!")
	sys.exit(" Exit")
print(' '+selected_file)


#do this for each pair of start and end times
for i, j in enumerate(clip_start):
	filename, file_extension = os.path.splitext(selected_file)
	out_file = filename +  '-'
	clip_duration = clip_end[i] - clip_start[i]
	if clip_start[i] >= 3600:
		out_file += 'x' #special case if t>1h, x ensures alphabetical sorting
	out_file += filenameTime(clip_start[i])
	out_file += '-' + filenameTime(clip_end[i])
	out_file += file_extension
	out_file = out_file.lower()
	
	command = 'ffmpeg -loglevel '+ str(ffmpeg_loglevel) +' -ss '+ '%.3f'%clip_start[i] +' -i \"'+ selected_file +'\" -t '+ '%.3f'%clip_duration +' -c copy \"'+ out_file +'\"'
	
	print('Clip ' + str(i+1))
	print(' Start:    ' + secToTs(clip_start[i]) + ' (' + '%.1f'%clip_start[i] + 's)')	
	print(' End:      ' + secToTs(clip_end[i]) + ' (' + '%.1f'%clip_end[i] + 's)')
	if clip_duration >= 60:
		print(' Duration: ' + secToTs(clip_duration) + ' (' + '%.1f'%clip_duration + 's)')	
	else:
		print(' Duration: ' + '%.1f'%clip_duration + 's')	
	print(' Command:  ' + command)	
	os.system(command)	
	
#delete input file?
if delete_input_file:
	os.remove(selected_file)
