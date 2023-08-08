import re
import json
import argparse
from pathlib import Path


# Covert note timings from Stepmania (.sm) format to Synth Riders
# timings only, no positioning
# left and down arrows are mapped to left, right and up arrows are mapped to right
# https://step-mania.fandom.com/wiki/.sm#:~:text=sm%20is%20one%20of%20the,chart%20data%20in%20the%20file
# https://github-wiki-see.page/m/stepmania/stepmania/wiki/sm

def content_capture(choreo):
    # regex to capture portions
    metadata_capture = r"OFFSET:(?P<offset>[0-9.]*)(.|\n)*BPMS:(.|\n)*=(?P<bpm>[0-9.]*)"
    levels_capture = r"(?:// measure 0[\n\s,/0-9a-zA-Z]*)"
    measure_capture = r"// measure (?P<no>[0-9]*)\n(?P<steps>(\s|[0-9A-Z])*)"

    metadata = re.search(metadata_capture, choreo)
    # in seconds
    offset = float(metadata.group("offset"))
    bpm = float(metadata.group("bpm"))

    levels_split = re.findall(levels_capture, choreo)

    # extract measure data
    level_measures_split = [re.findall(measure_capture, level) for level in levels_split]
    levels = [{int(m[0]): [s.strip() for s in m[1].splitlines() if len(s.strip()) > 0] for m in l} for l in
              level_measures_split]
    return bpm, offset, levels


def get_timing(b, n, d, increment, offset):
    offset_inc = round(offset * increment)
    # SR position format: count of 1/64th increments
    s_position = round((b + n / d) * 64 * 4) + offset_inc
    # SR time format: seconds * 20
    z_val = 20 * s_position / increment + offset * 20
    return s_position, z_val


def get_notes(measures, bpm, offset):
    increment = bpm * 64 / 60
    synth_notes = {}

    # placeholders for hold starts
    l_hold = None
    r_hold = None
    # b is beat
    for b in measures.keys():
        # denominator
        d = len(measures[b])
        # numerator
        for n in range(len(measures[b])):
            s_position, z_val = get_timing(b, n, d, increment, offset)
            notes = []
            # check for note content
            # 1 - Tap note
            # 2 - Hold head - rail start
            # 3 - Hold/roll end - add a segment for rail
            # 4 - Roll head - rail start

            # check for left notes
            if any(i in measures[b][n][:2] for i in ['1', '2', '4']):
                notes.append({"Position": [-0.108, 0, z_val], "Segments": None, "Type": 1})
            if any(i in measures[b][n][:2] for i in ['2', '4']):
                l_hold = s_position

            # handle hold ends
            if '3' in measures[b][n][:2]:
                # find the note with the correct type
                for i in range(len(synth_notes[l_hold])):
                    if synth_notes[l_hold][i]['Type'] == 1:
                        # add to the previous segment
                        synth_notes[l_hold][i]["Segments"] = [[-0.108, 0, z_val]]

            # check for right notes
            if any(i in measures[b][n][2:] for i in ['1', '2', '4']):
                notes.append({"Position": [0.202, 0, z_val], "Segments": None, "Type": 0})
            if any(i in measures[b][n][2:] for i in ['2', '4']):
                r_hold = s_position

            # handle hold ends
            if '3' in measures[b][n][2:]:
                # find the note with the correct type
                for i in range(len(synth_notes[r_hold])):
                    if synth_notes[r_hold][i]['Type'] == 0:
                        # add to the previous segment
                        synth_notes[r_hold][i]["Segments"] = [[0.202, 0, z_val]]

            # add notes if we found any
            if len(notes) > 0:
                synth_notes[s_position] = notes

    return synth_notes


def sm_to_synth(choreo, choreo_num=0):
    bpm, offset, levels = content_capture(choreo)

    synth_json = {
        "BPM": bpm,
        "startMeasure": 0,
        "startTime": 0,
        "lenght": list(levels[choreo_num].keys())[-1] * 60000 * 4 / bpm,
        "notes": get_notes(levels[choreo_num], bpm, offset),
        "effects": [],
        "jumps": [],
        "crouchs": [],
        "squares": [],
        "triangles": [],
        "slides": [],
        "lights": [],
    }
    return synth_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Stepmania to Synth Conversion',
        description='Convert .sm files to Synth Riders json format')

    parser.add_argument("sm", help="read folder with .sm files", type=Path)
    parser.add_argument("synth", help="write folder for converted files", type=Path)
    args = parser.parse_args()

    for file in args.sm.glob('*.sm'):
        filename = file.stem
        with open(file, "r") as f:
            choreo = f.read()
        synthmap = sm_to_synth(choreo)
        json_string = json.dumps(synthmap)
        with open(args.synth / f"{filename}.json", "w") as outfile:
            outfile.write(json_string)