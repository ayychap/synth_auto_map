import json


def xy_synth_to_ats(x, y):
    """ Convert Synth Riders x,y coords to Audio Trip
    Keep inside the comfort grid (unless it's really wild and wide)
    synth range
    -0.953500032 < x < 0.9575001 half-width 0.9555000659999999
    -0.6813 < y < 0.6837 half-width 0.6825
    AT range
    -0.8 < x < 0.8
    0.2 < y < 1.8"""

    xa = 0.84 * (x - 0.002)
    ya = 1.17 * (y - 0.0012) + 1

    return xa, ya


def xy_ats_to_synth(x, y):
    """Convert Audio Trip x, y coords to Synth Riders
    Inverse of above"""

    xs = 1.19 * x + 0.002
    ys = 0.85 * (y - 1) + 0.0012

    return xs, ys


def ats_to_synth(path, choreo_number=None):
    '''
    Import an audio trip ats file to synth riders (basic gems/notes and ribbons/rails only)

    :path: path to .ats file containing Audio Trip choreography
    :choreo_number: index (starting at 0) of Audio Trip choreography to use, if known
    :return: dict of things ready to be converted to Synth Riders json
    '''
    f = open(path)
    data = json.load(f)

    bpm = data['metadata']['avgBPM']
    increment = bpm * 64 / 60

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

    '''Dictionary for mapping from gems to notes
            right gems type 2, right ribbons type 4
            left gems type 1, left ribbons type 3
            right notes type 0
            left notes type 1'''
    type_map = {2: 0, 1: 1, 3: 1, 4: 0}

    # extract the choreography map to use
    choreos = data['choreographies']['list']
    if choreo_number is None:
        # if the specific index wasn't specified, use the one with the most data
        choreo_size = [len(c['data']['events']) for c in choreos]
        choreo_number = choreo_size.index(max(choreo_size))

    choreo = choreos[choreo_number]['data']['events']

    for gem in choreo:
        b = gem['time']['beat']
        n = gem['time']['numerator']
        d = gem['time']['denominator']

        s_position = round((b + n / d) * 64)
        z_val = 20 * s_position / increment
        x, y = xy_ats_to_synth(gem['position']['x'], gem['position']['y'])

        type = gem['type']
        if type == 3 or type == 4:
            # it's a rail!
            new_note = {"Position": [x, y, z_val], "Segments": [], "Type": type_map[type]}

            # time step in 20 * seconds
            # see var length_beatDivision for calculation:
            # https://github.com/Blogshot/trip-sitter/blob/master/SR_to_AT/conversion_elements.js
            step = 60 * 20 / (bpm * gem['beatDivision'])

            # now append all of those segments
            for node in gem['subPositions']:
                x, y = xy_ats_to_synth(node['x'], node['y'])
                z_val += step
                new_note["Segments"].append([x, y, z_val])

            if s_position in synth_json['notes']:
                synth_json['notes'][s_position].append(new_note)
            else:
                synth_json['notes'][s_position] = [new_note]

        elif type == 1 or type == 2:
            # it's a note!
            new_note = {"Position": [x, y, z_val], "Segments": None, "Type": type_map[type]}

            if s_position in synth_json['notes']:
                synth_json['notes'][s_position].append(new_note)
            else:
                synth_json['notes'][s_position] = [new_note]

    return synth_json
