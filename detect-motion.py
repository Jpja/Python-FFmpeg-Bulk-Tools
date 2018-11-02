#!/usr/bin/python3

#Github: 
#Video walkthrough: 

#basic parameters
generate_ouput_files = 1 #set to 0 if you only want to read logs
ts_dec = 0 #decimals after seconds in timestamps. Zero is recommended for manual editing
before_s = 2.5 #set start point N seconds before motion is triggered  
after_s = 2 #set end point N seconds after motion has ended
min_copy_break_s = 4.9 #dont stop copying if next motion trigger sooner than this
ignore_start_s = 2 #seconds dont search for motion in beginning of input file
ignore_end_s = 2 #seconds dont search for motion at end of input file
print_scores = False #whether to print frame info (including scene scores)
ffmpeg_loglevel = 31 #see https://ffmpeg.org/ffmpeg.html#Generic-optionsgenerate_ouput_files 
delete_input_files = False #DANGEROUS, use only if you have BACKUP of input files
file_formats = ['MP4', 'M4P', 'M4B', 'M4R', 'M4V', 'M4A', 'DIVX', 'EVO', 'F4V', 'FLV', 'AVI', 'QT', 'MXF', 'MOV', 'MTS', 'M2TS', 'MPEG', 'VOB', 'IFO']


#advanced filter parameters
step_len_f = 20 #compare every n frame
min_threshold_score = 0.0095 #default threshold. a score above indicates motion
test_duration_s = 7 #seek for a (motionless'ish) segment this long. threshold automatically adjusts up if necessary (and possible)
max_threshold_score = 0.04
segments_smooth = 0 #assign median score from n segments before and after to smooth out scores
segments_to_start = 2 #this many segments in a row above threshold triggers motion start
segments_to_end = 10 #this many segments in a row below threshold triggers motion end


'''
MIT License

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
'''


import os
import glob
import random
import statistics	
import math	
import time
import sys
import argparse
import textwrap


#parse arguments (if any, else use default)
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
		description:
			Detects motion in video files, and outputs start and end times for motion events.
			Optionally, the script will either call cut-video.py to make copies to new files, or it will only print the command which you can then manually edit. Example:
			
				cut-video.py myvid.mp4   4-2:14   5:13-12:42
				
        '''))
parser.add_argument("-i", "-f", "--file", default='', help='name of input file, or substring to process any matching file name. If not specified, all video files in folder are processed.')
parser.add_argument("-c", "--copy", default=generate_ouput_files, help='Default '+str(generate_ouput_files)+'. Must be 0 or 1. If 0, only read logs (you can copy commands to copy clips). If set to 1, new, separate files are created automatically')
args = parser.parse_args()
process_file = args.file
generate_ouput_files = args.copy


#function converts seconds to HOURS:MM:SS timestamp
# format as easy to read as possible (meant to be edited manually) 
def secToTs(sec):
	hr = math.floor(sec / 3600)
	min = math.floor((sec - hr * 3600) / 60)
	sec = sec - hr * 3600 - min * 60
	if ts_dec == 0:
		sec_format = "%" + str(2).zfill(2) + "." + str(ts_dec) + "f"
	else:
		sec_format = "%" + str(ts_dec+3).zfill(2) + "." + str(ts_dec) + "f"
	if hr>0:
		ts = '%02d'%hr +':'+ '%02d'%min +':'+ sec_format%sec
	elif min>0:
		ts = '%02d'%min +':'+ sec_format%sec
	else:
		ts = sec_format%sec
	if ts[0] == '0' and len(ts) > 0:
		ts = ts[1:]
	return ts


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
	
	
#filter out files not to process
input_files = []
for input_file in input_files_all:
	if (process_file != ''):
		if process_file not in input_file:
			continue
	input_files.append(input_file)
print("Process these files:")
for input_file in input_files:
	print(' '+input_file)


#prepare list with commands for cutting each file
commands = []


#do this for each video file
for input_file in input_files:
	t0 = time.time()
	print(" ")
	print("*")
	print("**")
	print("***")
	print("Processing "+input_file)
	
	#get scenescores from ffmpeg
	# ffmpeg's scene change detection algo: https://www.luckydinosaur.com/u/ffmpeg-scene-change-detector
	# writes to a txt file, parse it into lists, then delete file
	randint = random.randint(10000,99999)
	temp_file = "temp-scenescores-" + str(randint) + ".txt"
	if os.path.isfile(temp_file):
		os.remove(temp_file)
	command = "ffmpeg -loglevel "+str(ffmpeg_loglevel)+ " -i \""+input_file+"\" -vf select='not(mod(n\,"+str(step_len_f)+"))',select='gte(scene,0)',metadata=print:file="+temp_file+" -an -f null -"
	print(' Run command: ' + command)	
	os.system(command)

	f = []
	f_pts = []
	f_pts_time = []
	f_scene_score = []
	pts=0
	pts_time=0
	scene_score=0
	with open(temp_file) as file:
		text = file.read()	
	i = -1
	while True:
		i = text.find('frame', i+1)
		if i == -1:
			break
		i = text.find(':', i) + 1
		j = text.find(' ', i)
		f.append(int(text[i:j]))
		i = text.find('pts', i+1)
		i = text.find(':', i) + 1
		j = text.find(' ', i)
		f_pts.append(int(text[i:j]))
		i = text.find('pts_time', i+1)
		i = text.find(':', i) + 1
		j = text.find('\n', i)
		f_pts_time.append(float(text[i:j]))
		i = text.find('scene_score', i+1)
		i = text.find('=', i) + 1
		j = text.find('\n', i)
		f_scene_score.append(float(text[i:j]))
	os.remove(temp_file)
	
	
	#give each frame a median score from +/- N frames
	f_median_score = []
	for x in f:
		f_median_score.append(statistics.median(f_scene_score[max(0,x-segments_smooth):x+segments_smooth+1]))
	
	
	#try to increase threshold if no motionless period found 
	file_threshold_score = min_threshold_score
	while True:
		longest_motionless_s = 0
		last_change_s = 0
		run_s = 0
		for x in f:
			if f_median_score[x] < file_threshold_score:
				run_s = f_pts_time[x] - last_change_s
			else:
				if longest_motionless_s < run_s:
					longest_motionless_s = run_s
				last_change_s = f_pts_time[x]
		if longest_motionless_s <= test_duration_s:
			file_threshold_score += min_threshold_score
			if file_threshold_score > max_threshold_score:
				file_threshold_score = min_threshold_score
				break
		else:
			break
		

	#frame's score indicates CHANGE or not [0,1]
	f_change = []
	for x in f:
		if f_median_score[x] >= file_threshold_score:
			f_change.append(1)
		else:
			f_change.append(0)
	
	
	#frame's TRIGGER score [-1,0,+1]
	f_trigger = []
	x_max = len(f) - max(segments_to_start,segments_to_end)
	for x in f:
		if x >= x_max:
			f_trigger.append(0)
			continue
		run_above = 0
		for y in range(segments_to_start):
			if f_median_score[x+y] > file_threshold_score:
				run_above += 1
		if run_above == segments_to_start:
			f_trigger.append(1)
		else:
			run_above = 0
			for y in range(segments_to_end):
				if f_median_score[x+y] > file_threshold_score:
					run_above += 1
			if run_above == 0:
				f_trigger.append(-1)
			else:
				f_trigger.append(0)
	
	
	#based on trigger scores, select "smart" COPY start and end points [-1,0,+1]
	f_copy = []
	is_copying = 0
	last_start_s = 0
	last_end_s = 0
	end_time_s = f_pts_time[len(f)-1]
	for x in f:
		f_copy.append(0)
		if f_pts_time[x] < ignore_start_s:
			continue
		if x >= x_max or f_pts_time[x] > end_time_s - ignore_end_s:
			if is_copying == 1:
				#copy_end_s.append(f_pts_time[x])
				f_copy[x] = -1
			continue
			
		#start copy?
		if is_copying == 0:
			if f_pts_time[x] > end_time_s - ignore_end_s: #near end, don't make new starting point
				continue
			if f_trigger[x] == 1:
				#copy_start_s.append(f_pts_time[x])
				f_copy[x] = 1
				last_start_s = f_pts_time[x]
				is_copying = 1
				continue
				
		#end copy?
		if is_copying == 1:
			if f_trigger[x] == -1:
				can_end = 1
				y = x
				while True:
					y += 1
					if y >= x_max:
						break
					if f_trigger[y] == 1:
						can_end = 0
						break
					if f_pts_time[y] - f_pts_time[x] > min_copy_break_s:
						break
				if can_end == 1:
					#copy_end_s.append(f_pts_time[x])
					f_copy[x] = -1
					last_end_s = f_pts_time[x]
					is_copying = 0
				continue
			
	
	#set copy start and end times
	copy_start_s = []
	copy_end_s = []
	for x in f:
		if f_copy[x] == 1:
			copy_start_s.append(f_pts_time[x])
		if f_copy[x] == -1:
			copy_end_s.append(f_pts_time[x])	
		
		
	#adjust start and end times
	for x in range(len(copy_start_s)):
		copy_start_s[x] = max(copy_start_s[x] - before_s, 0)
		copy_end_s[x] = min(copy_end_s[x] + after_s, end_time_s)

	
	#print output values
	if print_scores:
		print("Frame;Time;Score;Median;Change;Trigger;Copy")
		for x in f:
			print(str(f[x]) + ";" + '%.4f'%(f_pts_time[x]) + ";" + '%.4f'%(f_scene_score[x]) + ";" + '%.4f'%(f_median_score[x]) + ";" + str(f_change[x]) + ";" + str(f_trigger[x]) + ';' + str(f_copy[x]))
	print("Threshold: " + str(file_threshold_score))
	print('Clips: ' + str(len(copy_start_s)))
	if len(copy_start_s) > 0:
		print('Nr      Start       End  Duration')	
		for x in range(len(copy_start_s)):
			line = str(x+1).ljust(3)
			line += secToTs(copy_start_s[x]).rjust(10)
			line += secToTs(copy_end_s[x]).rjust(10)
			line += secToTs(copy_end_s[x]-copy_start_s[x]).rjust(10)
			print(line)
	else:
		print(' No motion segment found')
		continue	
	
	#prepare command for cutting with cut-video.py
	command = 'cut-video.py ' + input_file
	for x in range(len(copy_start_s)):
		command += '   ' + secToTs(copy_start_s[x]) + '-' + secToTs(copy_end_s[x])
	commands.append(command)
	if generate_ouput_files == 1:
		print(' Run command: ' + command)
		os.system(command)
	
	
	#delete input file?
	if delete_input_files:
		os.remove(input_file)
	
	
	#print time it took to process file
	t1 = time.time()
	process_s = t1-t0
	times_faster = end_time_s / process_s
	print(input_file + ' processed in ' + '%.1f'%(process_s) + 's (' + '%.1f'%(times_faster) + 'x)')
	

print(" ")
print("Commands for each input file:")
for command in commands:
	print(' '+command)
