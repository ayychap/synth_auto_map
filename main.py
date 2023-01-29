import librosa

import numpy as np
from scipy import stats as st
import json
import matplotlib.pyplot as plt
import mplcyberpunk

class SoundFile:
    def __init__(self, filename, bpm=None, offset=0):
        '''

        :param filename: path to audio file
        :param bpm: beats per minute, default 100
        :param offset: offset in milliseconds
        '''
        self.y, self.samplingrate = librosa.load(filename)

        if bpm==None:
            self.bpm = self.tempos()
        else:
            self.bpm = bpm

        self.increment = self.bpm * 64 / 60  #1/64th increments per sec
        self.offset = offset / 1000
        self.timestamps = None
        self.beats()

    def time_to_synthmap(self, time_elapsed):
        '''
        Convert the timestamps to beatmap timings
        z=(Position/64)(60/bpm)2*10, where Position is the ordinal count of 1/64 increments since the song start
        From emikodo: The time is the measure * (60/bpm * 1000).  The start time is 60/bpm * 2 * 10 * startMeasure
        :time_elapsed: float or numpy array, actual time in audio file
        :return: positions in 1/64 increments, z coordinates
        '''

        # convert seconds to number of increments
        position = np.round((time_elapsed - self.offset) * self.increment).astype(int).astype(str) # convert seconds to number of increments
        # calculate the z's
        z = (time_elapsed - self.offset) * 2 * 10

        return position, z

    def tempos(self, chart=False):
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.samplingrate)
        # find the dynamic tempo
        dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.samplingrate, aggregate=None)

        if chart:
            plt.style.use("cyberpunk")
            plt.plot(np.linspace(0, librosa.get_duration(y=self.y, sr=self.samplingrate) / 60, dtempo.size), dtempo)
            plt.title("Detected BPM")
            plt.xlabel("Minutes")
            plt.ylabel("BPM")
            plt.show()

        # and return the mode
        return st.mode(dtempo).mode[0]

    def beats(self):
        pulse_array = librosa.beat.plp(y=self.y, sr=self.samplingrate)
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse_array))

        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.samplingrate)
        times = librosa.times_like(onset_env, sr=self.samplingrate)

        self.timestamps = times[beats_plp] # should be timestamps in seconds

    def generate_beatmap(self, path):
        positions, z_vals = self.time_to_synthmap(self.timestamps)
        notes = [[{"Position": [0, 0, z], "Segments": None, "Type": 0}] for z in z_vals]

        # format yoinked from synth_mapping_helper <3
        # https://github.com/adosikas/synth_mapping_helper/blob/main/src/synth_mapping_helper/synth_format.py
        beatmap = {
            "BPM": self.bpm,
            "startMeasure": 0,
            "startTime": 0,
            "lenght": self.timestamps[-1] * 1000,  # largest time value in milliseconds
            "notes": dict(zip(positions, notes)),
            "effects": [],
            "jumps": [],
            "crouchs": [],
            "squares": [],
            "triangles": [],
            "slides": [],
            "lights": [],
        }

        # Old stuff, bad math, do not use.
        # this will generate a list of dicts with the correct note format
        # notes = [sf.note_to_synth(self.bpm, 1, np.array([0,0,z]).reshape(1,3)) for z in z_vals]
        # again, adapted from synth_mapping_helper
        # wrong note storage format?
        # for note in notes:
        #     beatmap["notes"][round(note['Position'][2] * 64)] = [note]

        json_string = json.dumps(beatmap)
        with open(path, "w") as outfile:
            outfile.write(json_string)



if __name__ == '__main__':

    winter = SoundFile("Vivaldi_L'inverno_Allegro_Non_Molto.ogg")
    winter.generate_beatmap("generated_beatmap.json")

    print()
