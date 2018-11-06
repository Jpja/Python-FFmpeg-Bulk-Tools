# Python FFmpeg Bulk Tools  

Python FFmpeg Bulk Tools (PFBT) is a collection of python scripts that run FFmpeg commands on one, several or all files in a directory.

PFBT is intended to automate routine tasks.
- `detect-motion.py` finds start and end points of motion events
- `cut-video.py` splits a video into new, separate files based on start and end points
- `resize-video.py` resizes and re-encodes video file(s)
- `resize-image.py` resizes and re-encodes image file(s)

FFmpeg and Python 3 are required.

Tested on Windows 10.

### Usage

`detect-motion.py`, `resize-video.py` and `resize-image.py` can be run by double-clicking the files. The defult settings are applied to every video/image file in the same directory, and new files are created.

Open the script files to change default parameters.

Alternatvely, run script in command. `[script].py -h` for help.

### Detect Motion
`detect-motion.py` is suitable for videos with a static background, and where the foreground object periodically enters and leaves the frame. The script finds none, one or multiple pairs of start and end motion points. By default it then calls `cut-video.py` to extract any motion events as new files.
##### Example
* A video, `bird.mp4`, shows a bird feeding station continuously for 30 minutes. The script detects a bird entering the frame at 0:44 and leaving at 1:22, and then again from 12:42 to 12:59. Two new files are created; `bird-0044-0122.mp4` and `bird-1242-1259.mp4`

### Cut Video
`cut-video.py` must be run with arguments in command line. It requires a file name and at least one time argument. The outputs are lossless copies of the video bitstream. FFmpeg seeks near keyframes, so the cuts may not be exactly at the specified times. 
##### Example
* From a skate film, `skate.mp4`, you're interested in the events from 0:12 to 0:25, 8:13 to 12:24, and 57:12 to 1:03:12. Run command `cut-video.py skate.mp4 12-25 813-1224 5712-10312`to output three new files with these cuts.

### Resize Video
`resize-video.py` by default re-encodes video to x264 with CRF=24. Set height and/or width to force new resolution. A new frame rate can also be forced.  
##### Examples
1) Video camera generates excesive video file sizes. Import all videos to script's folder, run it to make smaller copies of each file. (My test with default settings, x264/CRF=24, on a Sony a6300 video (mp4, 60fps, 1080p) gives 75% reduced file size with no visible loss in quality.)
2) Downsize videos to email attachment size with command `resize-video.py --height 480 --crf 26 --fps 20`. (Tested on same input file, reduced by 96%)

### Resize Image
`resize-image.py` by default re-encodes image. Set height and/or width to force new resolution. Optional can set `fitbox=1` to keep aspect ratio while neither height nor width can be more than specified.  
##### Examples
1) For a website you want all images to be exactly 600x400 pixels. Run command `resize-image.py --width 600 --height 400 --fitbox 0`.
2) The same above, but you want this only applied to files ending with x.jpg. Run command `resize-image.py --file x.jpg --width 600 --height 400 --fitbox 0`

### MIT License

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


