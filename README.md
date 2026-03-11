# ClipMerge

## Description
CLipMerge is a simple python command line tool allowing a folder of clips to be quickly merged into a single video file, allowing montages to be created quickly and easily. 

## Basic Usage
The most basic usage involves running the following command, in which "clips" is a folder full of video files. The final product will be outputted as "output.mp4" in the home directory of the script.
```python clip_merge.py clips/```

### Ordering Clips
In order to control the order of the clips, the user has two options. Firstly, within the clips directory the user can create an order.txt file in which they list the desired order of the clips, for example

```1.mp4
2.mp4
3.mp4```

would result in an output where "1.mp4" is played first and "3.mp4" is played last. 

Alternatively, the user can forgo the creation of order.txt, and the clips will be played in alphabetical order. 

### Audio 
An audio file can be added to provide background music using the "--audio" flag, for example, the following command with result in the output montage playing "music.mp3" in the background:

```python clip_merge.py clips/ --audio music.mp3```

Additionally, the volume of the clip and music audio can be adjusted using the "--music-volume" and "--video-volume" flags. For example: 

```python clip_merge.py clips/ --audio music.mp3 --music-volume 0.2 --video-volume 1.0```