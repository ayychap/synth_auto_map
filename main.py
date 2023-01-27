import librosa
import synth_mapping_helper.synth_format as sf

import numpy as np
import json
import matplotlib.pyplot as plt
import mplcyberpunk

class SoundFile:
    def __init__(self, filename, bpm=100, offset=0):
        '''

        :param filename: path to audio file
        :param bpm: beats per minute, default 100
        :param offset: offset in milliseconds
        '''
        self.y, self.samplingrate = librosa.load(filename)

        self.bpm = bpm
        self.increment = self.bpm * 64 / 60  #increments per sec
        self.offset = offset / 1000
        self.timestamps = None
        self.beats()

    def time_to_synthmap(self, time_elapsed):
        '''
        Convert the timestamps to beatmap timings
        z=(Position/64)(60/bpm)2*10, where Position is the ordinal count of 1/64 increments since the song start

        :time_elapsed: float or numpy array, actual time in audio file
        :return: z coordinate
        '''

        position = (time_elapsed - self.offset) * self.increment
        z = (time_elapsed - self.offset) * 2 * 10

        return z

    def beats(self):
        pulse_array = librosa.beat.plp(y=self.y, sr=self.samplingrate)
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse_array))

        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.samplingrate)
        times = librosa.times_like(onset_env, sr=self.samplingrate)

        # plt.style.use("cyberpunk")
        # plt.plot(times, librosa.util.normalize(pulse_array),
        #          label='Wavy')
        # plt.vlines(times[beats_plp], 0, 1, alpha=0.5,
        #            linestyle='--', label='Local Beats')
        # plt.legend()
        # plt.xlim([130, 140])
        # plt.show()

        self.timestamps = times[beats_plp] # should be timestamps in seconds

    def generate_beatmap(self, path):


        # format yoinked from synth_mapping_helper <3
        # https://github.com/adosikas/synth_mapping_helper/blob/main/src/synth_mapping_helper/synth_format.py
        beatmap = {
            "BPM": self.bpm,
            "startMeasure": 0,
            "startTime": 0,
            "lenght": 0,
            "notes": {},
            "effects": [],
            "jumps": [],
            "crouchs": [],
            "squares": [],
            "triangles": [],
            "slides": [],
            "lights": [],
        }

        # convert to z values for the beatmap
        z_vals = [self.time_to_synthmap(x) for x in self.timestamps]
        # this will generate a list of dicts with the correct note format
        notes = [sf.note_to_synth(self.bpm, 1, np.array([0,0,z]).reshape(1,3)) for z in z_vals]

        # again, adapted from synth_mapping_helper

        first = 99999
        last = -99999
        # wrong note storage format?
        for note in notes:
            beatmap["notes"][round(note['Position'][2] * 64)] = [note]

        json_string = json.dumps(beatmap)
        with open(path, "w") as outfile:
            outfile.write(json_string)



if __name__ == '__main__':

    winter = SoundFile("Vivaldi_L'inverno_Allegro_Non_Molto.ogg")
    winter.generate_beatmap("generated_beatmap.json")


    print()
