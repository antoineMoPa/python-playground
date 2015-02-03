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

    if(notes == []):
        return np.zeros(0, np.float)
    
    for note in notes:
        # begining time + length
        time = note[2] + note[1]
        if(time > max_time):
            max_time = time
        
    track_data = np.zeros(max_time * SECOND + 1, np.float)

    
    for note in notes:
        f = note_func(note[0])
        note_sound = create_note(f,int(note[1] * SECOND))
        for i in range(0,len(note_sound)):
            track_data[i + note[2] * SECOND] += note_sound[i]

    max = np.max(track_data)
    min = np.min(track_data)
    if -min > max:
        max = -min
        
    track_data /= max
    return track_data

song = []

background = []
background += [7,8,9,7, 8,9,10,8]
background += [7,8,9,7, 8,9,10,8]



notes = []

for i in range(0,len(song)):
    notes.append((song[i],0.1,i*0.16))

def ta_tata_ta(i):
    i %= 8
    if(i < 3):
        return i/4*0.5
    if(i == 3):
        return 0
    if(i == 4):
        return 0.33
    if(i == 5):
        return 0.66
    if(i == 6):
        return 1
    
period_notes_num = 7
for i in range(0,len(background)):
    period = int(i / period_notes_num)
    in_period = i % period_notes_num
    period_time = 0.8
    note_offset = 0.9 * period_time * ta_tata_ta(in_period)
    time = period_time * period
    time += note_offset
    base_note = 22
    note = background[i]
    notes.append((minorScale(note,base_note),0.1,time))

    
#notes.append((7,1,len(song)*0.06))
    
# notes: [(note, length, time), ...]
track = {
    'basenote': 40,
    'notes': notes,
    'note_func': lambda note: (
        getFrequencyFromNote(
            note
        )
    )
}

song_data = track_to_array(track)

data = np_array_to_sound(song_data)
    
sound.writeframes(data)
sound.close()
system("aplay sound.wav")

