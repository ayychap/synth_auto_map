# Synth Auto Map

Some tools for automating parts of the mapping process in the [Synth Riders Beatmap Editor](https://store.steampowered.com/app/1121930/Synth_Riders_Beatmap_Editor/).
It's a really fun VR rhythm game, [check it out](https://synthridersvr.com/)!

## Features

### Generate guide notes

`beat_finder.py` uses [Librosa](https://librosa.org/doc/latest/index.html) to automatically detect BPM and note positions 
in an audio track, and converts the timestamp output to the Synthriders JSON format for use with the editor. This will 
give you a rough map with note time positions.

You can specify:
*   Increment to round to, 1/64 (the maximum in the editor) is the default.
*   BPM and offset, if known.
*   Some decomposition preprocessing, currently percussive and harmonic element separation
*   [Spleeter](https://github.com/deezer/spleeter) preprocessing to generate 2, 4, or 5 split audio tracks and associated maps.

Since this works based on time positioning, you can use this with variable BPM tracks, though you may run into rounding 
limitations due to the editor format. Since this detects the most prominent beats in an audio track, you may want to do some 
preprocessing on your audio file to detect the notes you want to use.

TODOs: Improve onset detection algorithms using traditional signal processing and/or neural networks. These aren't currently 
available as standard libraries.

### Analyze BPM

`beat_finder.py` also contains utilities to automatically detect the most stable BPM, and return BPM information over time, 
including onset timing of each BPM change. This will give you a rough estimate of the BPM, which may require additional fine-tuning.

### Convert Audio Trip Maps

If you also have [Audio Trip](http://www.kinemotik.com/audiotrip/), you can map hand positioning in VR and port it over! 
`audio_trip_conversion.py` contains functions for converting Audio Trip maps (choreographies) to Synth Riders. This works 
with gems to notes and ribbons to rails only.

Check out [Trip Sitter](https://github.com/Blogshot/trip-sitter) if you'd like to convert a Synth Riders beatmap to Audio Trip.

TODOs: Round rail splitting notes so that they land on a beat (mod 64)

## Not Features

This will not generate a whole map for you! Only certain processes are automated. You'll still need to do the work of 
positioning notes, fine tuning timing, setting up hand colors, and placing walls. There are some [excellent helper tools](https://github.com/adosikas/synth_mapping_helper) 
that can help you with some processes, but you will still need to use the editor and test your maps.

## How to Use

### "Basic" Version

Sorry, no UI for this. However, self-contained, guided Google Colab demos are available for some features if you'd like 
to test things out without any extra work or aren't so comfortable with coding. Most input is set up in forms, so code 
modification is limited.

*   [Synth Beat Finder Demo](https://colab.research.google.com/drive/10ssrPt996BzRDTrVG2RHwYEEqyqulG9L?usp=sharing): demo for how to work with the code, does not include source separation.
*   [Guide Note Generation](https://colab.research.google.com/drive/1fly5HNQSCJHDBUEOIrv3R6LBGh0W1jdN?usp=sharing): a limited interface with form input, including source separation options, for rapidly creating and modifying beatmaps.
*   [Audio Trip to Synth Converter](https://colab.research.google.com/drive/1J_nkdsrI1pGqMmmCOKq3uTQv77HTCRsw?usp=sharing): convert Audio Trip choreography to Synth Riders maps.

### Advanced Users 

Clone this repository and play around with the Jupyter notebook demo files, add your own scripts, go wild. Pattern generation 
features are a work in progress and will require some math, sorry.
