import librosa
import numpy as np
from scipy import stats as st
import pandas as pd
import json
import matplotlib.pyplot as plt
# Thematic! (This is just for ambiance in plots)
import mplcyberpunk


class SoundConversion:
    def __init__(self, filename, bpm=None, offset=None, decomposition=None):
        '''
        Initialize an object to extract and manipulate waveform data from an audio file. Everything is calculated in
        seconds, so processing doesn't depend on a stable bpm.
        EXTREMELY EXPERIMENTAL

        Key features:
        Identifying "typical" bpm assuming a variable bpm with tempo()
        Identifying time values corresponding to beats stored in .timestamps
        Exporting a JSON file with notes positioned on the identified beats with generate_beatmap()

        :param filename: path to audio file
        :param bpm: beats per minute, if known, will be detected otherwise
        :param offset: offset in milliseconds
        :param decomposition: defaults to using the standard file, options are "harmonic" or "percussive"
        '''
        self.y, self.samplingrate = librosa.load(filename)

        if bpm is None:
            self.bpm = self.tempos()
        else:
            self.bpm = bpm

        self.increment = self.bpm * 64 / 60  # 1/64th increments per sec

        if offset is None:
            # TODO: get autodetection working
            self.offset = 0
        else:
            self.offset = offset / 1000

        self.timestamps = None

        D = librosa.stft(self.y)
        H, P = librosa.decompose.hpss(D)
        self.harmonic = librosa.istft(H)
        self.percussive = librosa.istft(P)

        self.use_decomp(decomposition)

    def update_bpm(self, new_bpm):
        if new_bpm is None:
            self.bpm = self.tempos()
        else:
            self.bpm = new_bpm
            self.increment = self.bpm * 64 / 60

    def time_to_synthmap(self, time_elapsed, rounding=None):
        '''
        Convert timestamps to beatmap timings. If working with a known fixed bpm and maximum note separation,
        use rounding to snap notes to nearest beat.

        :time_elapsed: float or numpy array, actual time in audio file
        :rounding: int 2, 4, 8, etc. Instead of rounding to 1/64, snap notes to nearest 1/4, 1/8, etc.
        :return: positions in 1/64 increments as np array of strings, z coordinates as np array
        '''

        # convert seconds to number of increments
        position = np.round((time_elapsed + self.offset) * self.increment).astype(int)

        if rounding is None:
            # z's do not need to be modified, these are seconds * 20
            z = (time_elapsed + self.offset) * 2 * 10
        else:
            # round the positions to the required step, and calculate the corrected z timing
            rounding = 64 / rounding
            position = (rounding * np.round(position / rounding)).astype(int)
            z = position * 20 / self.increment

        position = position.astype(str)  # string labels
        return position, z

    def tempos(self, chart=False):
        '''
        Detect tempo (bpm) in track, assuming dynamic. Returns the most typical bpm.

        :chart: if True, generates a chart of bpm over the course of the track
        :return: mode of bpm values as float
        '''

        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.samplingrate)
        # find the dynamic tempo
        dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.samplingrate, aggregate=None)

        if chart:
            plt.style.use("cyberpunk")
            plt.plot(np.linspace(0, librosa.get_duration(y=self.y, sr=self.samplingrate) / 60, dtempo.size), dtempo)
            plt.title("Detected BPM")
            plt.xlabel("Minutes")
            plt.ylabel("BPM")
            mplcyberpunk.add_glow_effects()
            plt.show()

        # and return the mode
        return st.mode(dtempo, keepdims=True).mode[0]

    def tempo_breakdown(self):
        '''Find chunks of common tempo and return them with estimated time windows'''
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.samplingrate)
        # find the dynamic tempo
        dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.samplingrate, aggregate=None)
        timings = librosa.times_like(dtempo)

        # this should get the starting indices for each tempo sequence
        start_idx = np.nonzero(np.r_[1, np.diff(dtempo)[:-1]])

        data = np.array([dtempo[start_idx], timings[start_idx]]).T

        return pd.DataFrame(data, columns=["BPM", "Time"])

    def notes(self, audio_series):
        '''
        Detect note positions and extract timestamps
        '''

        self.timestamps = librosa.onset.onset_detect(y=audio_series, sr=self.samplingrate, units="time")

    def use_decomp(self, decomp):
        if decomp == "harmonic":
            self.notes(self.harmonic)
        elif decomp == "percussive":
            self.notes(self.percussive)
        else:
            self.notes(self.y)

    def generate_beatmap(self, path, rounding=None):
        '''
        Convert timestamp data to beatmap notes and generate json output file
        Round to nearest 1/n beat (optional) using an integer increment in rounding, e.g. 2 for 1/2 increments,
        4 for 1/4 increments, etc.

        Note: You MUST manually set the bpm in the editor before pasting the json

        :path: path to json file
        :rounding: integer increment to round to, otherwise everything will be to the nearest 64th
        '''
        positions, z_vals = self.time_to_synthmap(self.timestamps, rounding=rounding)
        notes = [[{"Position": [0, 0, z], "Segments": None, "Type": 0}] for z in z_vals]

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

        json_string = json.dumps(beatmap)
        with open(path, "w") as outfile:
            outfile.write(json_string)