import wave
import math
from os import system
import numpy as np

SECOND = 44100
sound = wave.open('sound.wav', 'w')
sound.setparams((1, 1, SECOND, 0, 'NONE', 'not compressed'))

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

simple_envelope = lambda i,length: (
    1-(2 * (i/length % 1) - 1) ** 2
)
f_to_sin = lambda f,i: (
    math.sin(2 * math.pi * f * i / SECOND)
)


#song = []
#
#song += [0,2,4,6,7,2,0]
#song += [0,2,4,6,8,2,0]
#song += [0,2,4,6,9,2,0]
#song += [0,2,4,6,7,2,0]
#song += [0,2,4,6,7,2,0]
#song += [0,2,4,6,8,2,0]
#song += [0,2,4,6,9,2,0]
#song += [0,2,4,6,7,2,0]
#song += [0,2,3,4,5,1,0]
#song += [0,2,3,4,6,1,0]
#song += [0,2,3,4,7,1,0]
#song += [0,2,3,4,5,1,0]
#song += [0,2,3,4,5,1,0]
#song += [0,2,3,4,6,1,0]
#song += [0,2,3,4,7,1,0]
#song += [0,2,3,4,5,1,0]
#
#song = song + song
#
#background = []
#background += [7,8,9,7]
#background += [7,8,9,7]
#background += [5,6,7,5]
#background += [5,6,7,5]
#
#background = background + background

#length = SECOND * 11

#tracks = [song,background]
#
#for i in range (0,length):
#    d = 0
#    for track in tracks:
#        note_length = length / len(track)
#        note_index = int(i/length * len(track))
#        note_index = int(note_index)
#        note_num = track[note_index]
#        note_scaled = majorScale(note_num,40)
#        f = getFrequencyFromNote(note_scaled)        
#        d += simple_envelope(i,note_length) * f_to_sin(f,i)
#    
#    d /= len(track) + 1
#    
#    s = int(127*d+127)
#    data.append(s)

def create_note(f,length):
    arr = []
    for i in range(0,int(length)):
        arr.append(simple_envelope(i,length) * f_to_sin(f,i))
    return np.array(arr)

def np_array_to_sound(song_data):
    data = bytearray()
    for i in range (0,len(song_data)):
        d = int(127 * song_data[i] + 127)
        data.append(d)

    return data

def track_to_array(track):
    notes = track['notes']
    note_func = track['note_func']

    # find max time
    max_time = 0
    for note in notes:
        # begining time + length
        time = note[2] + note[1]
        if(time > max_time):
            max_time = time
        
    track_data = np.zeros(max_time * SECOND, np.float)

    for note in notes:
        f = note_func(note[0])
        note_sound = create_note(f,int(note[1] * SECOND))
        for i in range(0,len(note_sound)):
            track_data[i + note[2] * SECOND] += note_sound[i]

    max = np.max(track_data)
    track_data /= max
    return track_data

track = {
    'basenote': 40,
    'notes': [
        # note, length, time
        (6,1/3,0),
        (7,1,2)     
    ],
    'note_func': lambda note: (
        getFrequencyFromNote(
            majorScale(note,40)
        )
    )
}

song_data = track_to_array(track)

data = np_array_to_sound(song_data)


    
sound.writeframes(data)
sound.close()
system("aplay sound.wav")

