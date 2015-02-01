import wave
import math
from os import system

SECOND = 44100
sound = wave.open('sound.wav', 'w')
sound.setparams((1, 1, SECOND, 0, 'NONE', 'not compressed'))
data = bytearray()

baseNotes = [
    16.352,
    17.324,
    18.354,
    19.445,
    20.602,
    21.827,
    23.125,
    24.500,
    25.957,
    27.500,
    29.135,
    30.868
]

def abs(num):
    if num > 0:
        return num
    else:
        return -num

def noteToScale(i,baseNote,scale):
    if(i < 0):
        return -1
    octaveOffset = baseNote + math.floor( i / len(scale)) * 12
    return scale[abs(i) % len(scale)] + octaveOffset

def majorScale(i,baseNote):
    return noteToScale(i,baseNote,[0,2,4,5,7,9,11])

def minorScale(i,baseNote):
    return noteToScale(i,baseNote,[0,2,3,5,7,8,11])

def getFrequencyFromNote(note):
    currentNote = note % 12;
    currentOctave = int(note / 12) + 1;
    baseFrequency = baseNotes[currentNote];
    octaveMultiplier = math.pow(2,currentOctave);
    
    return baseFrequency * octaveMultiplier;

song = []

song += [0,2,4,6,7,2,0]
song += [0,2,4,6,8,2,0]
song += [0,2,4,6,9,2,0]
song += [0,2,4,6,7,2,0]

song += [0,2,4,6,7,2,0]
song += [0,2,4,6,8,2,0]
song += [0,2,4,6,9,2,0]
song += [0,2,4,6,7,2,0]

song += [0,2,3,4,5,1,0]
song += [0,2,3,4,6,1,0]
song += [0,2,3,4,7,1,0]
song += [0,2,3,4,5,1,0]

song += [0,2,3,4,5,1,0]
song += [0,2,3,4,6,1,0]
song += [0,2,3,4,7,1,0]
song += [0,2,3,4,5,1,0]

song = song + song

song += [0,2,4,6,7,7,7]




length = SECOND * 11

note_length = length / len(song)
envelope = lambda i: 1-(2 * (i/note_length % 1) - 1) ** 2

for i in range (0,length):
    note_num = song[int(i/length * len(song))]
    note_num = majorScale(note_num,40)
    f = getFrequencyFromNote(note_num)
    d = math.sin(2 * math.pi * f * i / SECOND)
    d *= envelope(i)
    s = int(127*d+127)
    data.append(s)
        
sound.writeframes(data)
sound.close()
system("aplay sound.wav")

