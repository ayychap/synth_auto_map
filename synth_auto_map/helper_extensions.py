import synth_mapping_helper as smh
from synth_mapping_helper.synth_format import *


# variants for manipulating files, allows use of functions on more than one json file simultaneously.
def import_file(path) -> DataContainer:
    f = open(path)
    original_json = json.load(f)
    data = original_json

    bpm = data["BPM"]
    startMeasure = data["startMeasure"]
    # r, l, s, b
    notes: list[SINGLE_COLOR_NOTES] = [{} for _ in range(4)]
    for time_index, time_notes in data["notes"].items():
        for note in time_notes:
            note_type, nodes = note_from_synth(bpm, startMeasure, note)
            notes[note_type][nodes[0, 2]] = nodes

    walls: dict[float, list["numpy array (1, 5)"]] = {}
    # slides (right, left, angle_right, center, angle_right)
    for wall_dict in data["slides"]:
        wall = wall_from_synth(bpm, startMeasure, wall_dict, wall_dict["slideType"])
        walls[wall[0, 2]] = wall
    # other (crouch, square, triangle)
    for wall_type in ("crouch", "square", "triangle"):
        for wall_dict in data[wall_type + "s"]:
            wall = wall_from_synth(bpm, startMeasure, wall_dict, WALL_TYPES[wall_type][0])
            walls[wall[0, 2]] = wall

    return DataContainer(original_json, bpm, *notes, walls)


def export_file(data: DataContainer, path, realign_start: bool = True):
    output_json = {
        "BPM": data.bpm,
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
        "original_json": data.original_json,
    }
    first = 99999
    last = -99999
    for note_type, notes in enumerate((data.right, data.left, data.single, data.both)):
        for time_index, nodes in notes.items():
            output_json["notes"].setdefault(round(time_index * 64), []).append(
                note_to_synth(data.bpm, note_type, nodes))
            if nodes[0, 2] < first:
                first = nodes[0, 2]
            if nodes[-1, 2] > last:
                last = nodes[-1, 2]
    for _, wall in data.walls.items():
        if wall[0, 2] < first:
            first = wall[0, 2]
        if wall[0, 2] > last:
            last = wall[0, 2]
        dest_list, wall_dict = wall_to_synth(data.bpm, wall)
        output_json[dest_list].append(wall_dict)

    if realign_start:
        # position of selection start in beats*64
        output_json["startMeasure"] = round(first * 64)
        # position of selection start in ms
        output_json["startTime"] = first * MS_PER_MIN / data.bpm
        # length of the selection in milliseconds
        # and yes, the editor has a typo, so we need to missspell it too
        output_json["lenght"] = last * MS_PER_MIN / data.bpm
    # always update length
    output_json["lenght"] = (last - first) * MS_PER_MIN / data.bpm

    final_output = json.dumps(output_json)
    with open(path, "w") as outfile:
        outfile.write(final_output)


# Additional movement functions allowing arbitrary position reassignment
def arbitrary_xy(data: "numpy array (1, 3)", new_locs: dict) -> "numpy array (1, 3)":
    '''
    Makes snap-to rail work. Reposition to a set of xy coordinates given in a dictionary.
    Dictionary keys correspond to the time coordinate
    '''
    data[0, :2] = new_locs[data[0, 2]]
    return data


def snap_to_rail(beats, rail_patterns):
    '''snap existing notes to a rail of the same color'''

    categories = ["both", "left", "right", "single"]

    for c in categories:
        times = getattr(beats, c)
        repositioning_map = {n: (smh.rails.get_position_at(getattr(rail_patterns, c), n)
                                 if smh.rails.get_position_at(getattr(rail_patterns, c), n) is not None
                                 else np.array([0, 0])) for n in times.keys()}
        beats.apply_for_notes(arbitrary_xy, repositioning_map, types=[c])
