from bisect import bisect
import json
import math
import numpy as np
import argparse
from pathlib import Path

'''Functions for conversion from Audio Trip .ats files to Synth Riders compatible JSON.
    This will convert gems and ribbons ONLY.

    Audio Trip's beatmap editor is in VR and allows for live hand position editing, while the
    Synth Riders editor allows for easier fine tuning. Combined with beat_finder.py, this allows
    you to map beats somewhat automatically, and generate live hand positioning separately without
    requiring you to stay on beat in the Audio Trip editor. Make sure that your Audio Trip hand 
    positioning is completely converted to rails, modify as desired, and copy-paste the note
    JSON with snap-to-rail enabled. Voila! Your notes are snapped to hand positions.
    
    Trip Sitter (https://github.com/Blogshot/trip-sitter) allows for conversion back to Audio Trip 
    editor, giving you the ability to use automatic note finding and both beatmap editors to create 
    tracks for either game.'''


def xy_synth_to_ats(x, y):
    """ Convert Synth Riders x,y coords to Audio Trip
    Keep inside the comfort grid (unless it's really wild and wide)
    synth range currently going down to -1.86
    -0.953500032 < x < 0.9575001 half-width 0.9555000659999999
    -0.6813 < y < 0.6837 half-width 0.6825
    AT range
    -0.8 < x < 0.8
    0.2 < y < 1.8

    new: -1 < x < 1
    0 < y < 2"""

    # TODO: update functions, currently wrong
    xa = 0.84 * (x - 0.002)
    ya = 1.17 * (y - 0.0012) + 1

    return xa, ya


def xy_ats_to_synth(x, y):
    """Convert Audio Trip x, y coords to Synth Riders
    Inverse of above
    synth range
    -0.953500032 < x < 0.9575001 half-width 0.9555000659999999
    -0.6813 < y < 0.6837 half-width 0.6825
    AT range
    -1 < x < 1
    0 < y < 2"""

    xs = 0.9555 * x + 0.002
    ys = 0.6825 * (y - 1) + 0.0012

    return xs, ys


def interpolate_at_time(point1, point2, t):
    """find xyz position at time t given two points (x, y, t)"""
    scaled_vector = (point2[:2] - point1[:2]) * (t - point1[2]) / (point2[2] - point1[2])
    xy = (point1[:2] + scaled_vector).tolist()
    xy.append(t)
    return xy


def rail_format(rail_array, type):
    """Convert an array of positions to a rail dictionary"""
    return {"Position": rail_array[0], "Segments": rail_array[1:], "Type": type}


def all_rails(synth_json):
    """Connect all notes into rails"""

    notes = synth_json['notes']
    position_types = {k: {n['Type']: {'Position': n['Position'], 'Segments': n['Segments']} for n in notes[k]} for k in
                      notes.keys()}
    note_types = [0, 1, 2, 3]
    # for the new rail associated with each note type
    new_rails = {}
    # position keys for each note type
    first_positions = {}

    for type in note_types:
        # get keys for note type
        positions = [k for k in position_types.keys() if type in position_types[k].keys()]
        # get a list of all positions for each note type
        position_list = [[position_types[k][type]['Position']] + position_types[k][type]['Segments']
                         if position_types[k][type]['Segments'] is not None else [position_types[k][type]['Position']]
                         for k in positions]

        position_list = [n for p in position_list for n in p]
        if len(position_list) > 0:
            new_rails[type] = {'Position': position_list[0], 'Segments': None, 'Type': type}
            first_positions[type] = positions[0]

            if len(position_list) > 1:
                new_rails[type]['Segments'] = position_list[1:]

    # The note types we actually have
    final_types = list(new_rails.keys())
    new_json = synth_json.copy()

    # the first rail
    new_json['notes'] = {first_positions[final_types[0]]: [new_rails[final_types[0]]]}

    # if we actually have more rails...
    if len(final_types) > 1:
        for type in final_types[1:]:
            p = first_positions[type]
            if p in new_json['notes'].keys():
                new_json['notes'][p].append(new_rails[type])
            else:
                new_json['notes'][p].append(new_rails[type])

    # validate rails and split
    return validate_rails(new_json)


def validate_rails(synth_json):
    """Check all rails in the beatmap and split any that are longer than 10 seconds"""

    increment = synth_json['BPM'] * 64 / 60 / 20

    new_json = synth_json.copy()
    new_json['notes'] = {}

    for position in synth_json['notes'].keys():
        if position not in new_json['notes']:
            new_json['notes'][position] = []
        for type in synth_json['notes'][position]:
            # single notes
            if type['Segments'] is None:
                new_json['notes'][position].append(type)
            # rails
            else:
                length = type['Segments'][-1][2] - type['Position'][2]
                if length < 200:
                    # short rail
                    new_json['notes'][position].append(type)
                else:
                    # long rail
                    # get split time positions, use slightly larger value for safety
                    num_splits = math.ceil(length / 205)
                    split_times = np.linspace(type['Position'][2], type['Segments'][-1][2], num=num_splits + 2)[1:-1]
                    # Find insertion points: https://docs.python.org/3/library/bisect.html#bisect.bisect
                    segment_times = [n[2] for n in type['Segments']]
                    insertion_indices = np.array([bisect(segment_times, s) + 1 for s in split_times])

                    split_indices = []
                    old_segments = [type['Position']] + type['Segments']

                    for n in range(split_times.size):
                        idx = insertion_indices[n]
                        split_xyz = interpolate_at_time(np.array(old_segments[idx - 1]), np.array(old_segments[idx]),
                                                        split_times[n])
                        # insert the new point
                        old_segments.insert(idx, split_xyz)
                        # record the split location in the list
                        split_indices.append(idx)
                        # add 1 to remaining insertion indices
                        insertion_indices[n + 1:] += 1

                    # Now, actually split the thing
                    # The first one is pretty straightforward
                    new_json['notes'][position].append(rail_format(old_segments[:split_indices[0] + 1], type["Type"]))
                    # The others require some checks
                    for n in range(len(split_indices) - 1):
                        new_rail = rail_format(old_segments[split_indices[n]: split_indices[n + 1] + 1], type["Type"])
                        step = round(old_segments[split_indices[n]][2] * increment)
                        if step not in new_json['notes']:
                            new_json['notes'][step] = [new_rail]
                        else:
                            new_json['notes'][step].append(new_rail)
                    # and the last one...
                    last_rail = rail_format(old_segments[split_indices[-1]:], type["Type"])
                    step = round(old_segments[split_indices[-1]][2] * increment)
                    if step not in new_json['notes']:
                        new_json['notes'][step] = [last_rail]
                    else:
                        new_json['notes'][step].append(last_rail)

    return new_json


def ats_to_synth(path, choreo_name=None, convert_to_rails=False):
    '''
    Import an audio trip ats file to synth riders (basic gems/notes and ribbons/rails only)

    :path: path to .ats file containing Audio Trip choreography
    :choreo_number: index (starting at 0) of Audio Trip choreography to use, if known
    :convert_to_rails: boolean, set to True to join all notes into rails
    :return: dict of things ready to be converted to Synth Riders json
    '''
    f = open(path)
    data = json.load(f)

    bpm = data['metadata']['avgBPM']
    increment = bpm * 64 / 60

    # get time and increment offsets
    offset_list = [section['startTimeInSeconds'] for section in data['metadata']['tempoSections']
                   if section['doesStartNewMeasure']]
    offset = offset_list[0]
    offset_inc = round(offset * increment)

    synth_json = {
        "BPM": bpm,
        "startMeasure": 0,
        "startTime": 0,
        "lenght": data['metadata']['songEndTimeInSeconds'] * 1000,
        "notes": {},
        "effects": [],
        "jumps": [],
        "crouchs": [],
        "squares": [],
        "triangles": [],
        "slides": [],
        "lights": [],
    }

    '''Dictionary for mapping from gems (AT) to notes (SR)
            right gems type 2, right ribbons type 4
            left gems type 1, left ribbons type 3
            right notes type 0
            left notes type 1'''
    type_map = {2: 0, 1: 1, 3: 1, 4: 0}

    # extract the choreography map to use
    choreos = data['choreographies']['list']
    if isinstance(choreo_name, str):
        # find the index of the choreography name
        name_list = [c['header']['name'] for c in choreos]
        if choreo_name in name_list:
            choreo_num = name_list.index(choreo_name)
        else:
            choreo_size = [len(c['data']['events']) for c in choreos]
            choreo_num = choreo_size.index(max(choreo_size))
    else:
        # if the specific index wasn't specified, or wasn't valid, use the one with the most data
        choreo_size = [len(c['data']['events']) for c in choreos]
        choreo_num = choreo_size.index(max(choreo_size))

    choreo = choreos[choreo_num]['data']['events']

    for gem in choreo:
        b = gem['time']['beat']
        n = gem['time']['numerator']
        d = gem['time']['denominator']

        # SR position format: count of 1/64th increments
        s_position = round((b + n / d) * 64) + offset_inc
        # SR time format: seconds * 20
        z_val = 20 * s_position / increment + offset * 20
        x, y = xy_ats_to_synth(gem['position']['x'], gem['position']['y'])

        type = gem['type']
        if type == 3 or type == 4:
            # it's a rail!
            new_note = {"Position": [x, y, z_val], "Segments": [], "Type": type_map[type]}

            # time step between nodes in 20 * seconds
            # see var length_beatDivision for calculation:
            # https://github.com/Blogshot/trip-sitter/blob/master/SR_to_AT/conversion_elements.js
            step = 60 * 20 / (bpm * gem['beatDivision'])

            # now append all of those segments
            for node in gem['subPositions'][1:]:
                x_offset, y_offset = xy_ats_to_synth(gem['position']['x'] + node['x'], gem['position']['y'] + node['y'])
                z_val += step
                new_note["Segments"].append([x_offset, y_offset, z_val])

            # Add to an existing position if one already exists
            if s_position in synth_json['notes']:
                synth_json['notes'][s_position].append(new_note)
            else:
                synth_json['notes'][s_position] = [new_note]

        elif type == 1 or type == 2:
            # it's a note!
            new_note = {"Position": [x, y, z_val], "Segments": None, "Type": type_map[type]}

            # Add to an existing position if one already exists
            if s_position in synth_json['notes']:
                synth_json['notes'][s_position].append(new_note)
            else:
                synth_json['notes'][s_position] = [new_note]

    if convert_to_rails:
        return all_rails(synth_json)
    else:
        return validate_rails(synth_json)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Audiotrip to Synth Conversion',
        description='Convert .ats files to Synth Riders json format')

    parser.add_argument("ats", help="read folder with .ats files", type=Path)
    parser.add_argument("synth", help="write folder for converted files", type=Path)
    args = parser.parse_args()

    for file in args.ats.glob('*.ats'):
        filename = file.stem
        synthmap = ats_to_synth(file)
        json_string = json.dumps(synthmap)
        with open(args.synth / f"{filename}.json", "w") as outfile:
            outfile.write(json_string)
