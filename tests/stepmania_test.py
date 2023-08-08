import unittest
from synth_auto_map import stepmania_conversion as sc

# load test choreography
choreo = r"""#TITLE:Absolutely Smitten;
    #SUBTITLE:;
    #ARTIST:Unknown artist;
    #TITLETRANSLIT:;
    #SUBTITLETRANSLIT:;
    #ARTISTTRANSLIT:;
    #GENRE:;
    #CREDIT:;
    #BANNER:;
    #BACKGROUND:;
    #LYRICSPATH:;
    #CDTITLE:;
    #MUSIC:Absoultely Smitten.ogg;
    #OFFSET:0.000000;
    #SAMPLESTART:100.000000;
    #SAMPLELENGTH:12.000000;
    #SELECTABLE:YES;
    #BPMS:0.000000=118.959999
    ;
    #STOPS:
    ;
    #BGCHANGES:;
    #KEYSOUNDS:;
    #ATTACKS:;

    //---------------dance-single - ----------------
    #NOTES:
         dance-single:
         :
         Hard:
         1:
         0.297427,0.413648,0.117849,0.188558,0.000000,265.000000,250.000000,15.000000,24.000000,0.000000,0.000000,0.297427,0.413648,0.117849,0.188558,0.000000,265.000000,250.000000,15.000000,24.000000,0.000000,0.000000:
      // measure 0
    0000
    0000
    0000
    0000
    ,  // measure 1
    0000
    0000
    0000
    0000
    ,  // measure 2
    0000
    0000
    0000
    0000
    ,  // measure 3
    0000
    0000
    0000
    0000
    ,  // measure 4
    0000
    0000
    0000
    0000
    0000
    1000
    0001
    1000
    ,  // measure 5
    0001
    1000
    0100
    0010
    0002
    0003
    0000
    0000
    ,  // measure 6
    0000
    0000
    0000
    0000
    0000
    0001
    0100
    0001
    ,  // measure 7
    0100
    0001
    0010
    0100
    2000
    3000
    0000
    0000
    ,  // measure 8
    0000
    0000
    0000
    0000
    1000
    1000
    1000
    0001
    ,  // measure 9
    0001
    0001
    0100
    0100
    0100
    0010
    0010
    0010
    ,  // measure 10
    0000
    0000
    0020
    0000
    0000
    0130
    0010
    0110
    ,  // measure 11
    0000
    0000
    0000
    0000
    ,  // measure 12
    0000
    0000
    0000
    0000
    1001
    0010
    0100
    1000
    ,  // measure 13
    0100
    0010
    0001
    0010
    0100
    1000
    0100
    0000
    ,  // measure 14
    0010
    0000
    0001
    0000
    1001
    0010
    0100
    0001
    ,  // measure 15
    1000
    0010
    0100
    0010
    0001
    0010
    0001
    0000
    ,  // measure 16
    0000
    0000
    0000
    0000
    1001
    0100
    0010
    0100
    ,  // measure 17
    0010
    0100
    0001
    1000
    0002
    2000
    0000
    0000
    ,  // measure 18
    3003
    0000
    0010
    0100
    1001
    0100
    0010
    0000
    ,  // measure 19
    0000
    0000
    0000
    0000
    ,  // measure 20
    0000
    0000
    1001
    0000
    ,  // measure 21
    0000
    0010
    0100
    0100
    0010
    0000
    0000
    0000
    ,  // measure 22
    0000
    0000
    0000
    0000
    1001
    0000
    0000
    0002
    ,  // measure 23
    0000
    0003
    0000
    1000
    1000
    0001
    1000
    0000
    ,  // measure 24
    0000
    0000
    0000
    0000
    1001
    0000
    0000
    0010
    ,  // measure 25
    0010
    0010
    0100
    0100
    0100
    0000
    0000
    2000
    ,  // measure 26
    0001
    0000
    0000
    0001
    0000
    0000
    0001
    0000
    3000
    1000
    0000
    0000
    1001
    0000
    0000
    0200
    0000
    0000
    0000
    0000
    0000
    0000
    0000
    0000
    ,  // measure 27
    0000
    0300
    0020
    0000
    0030
    2000
    0000
    0000
    ,  // measure 28
    3002
    0000
    0000
    0203
    0320
    0030
    0200
    0000
    ,  // measure 29
    0320
    0000
    0030
    0000
    0002
    0000
    0003
    2000
    ,  // measure 30
    0000
    3000
    0000
    0110
    1001
    1000
    0100
    0010
    ,  // measure 31
    0001
    1001
    0100
    0010
    0001
    0000
    0000
    0000
    ,  // measure 32
    0000
    0000
    0000
    0000
    0000
    1000
    0010
    1000
    ,  // measure 33
    0010
    1000
    0100
    1000
    0100
    0000
    0000
    0000
    ,  // measure 34
    0000
    0000
    0000
    0000
    1000
    1000
    1000
    0001
    ,  // measure 35
    0001
    0001
    0100
    0100
    0100
    0010
    0010
    0010
    ,  // measure 36
    0000
    1000
    0200
    0310
    0001
    0010
    0001
    0010
    ,  // measure 37
    0000
    0000
    0000
    0000
    ,  // measure 38
    0000
    0000
    0000
    0000
    0000
    1000
    0001
    0001
    ,  // measure 39
    1000
    1000
    0001
    0001
    2000
    3000
    0000
    0000
    ,  // measure 40
    0000
    0000
    0000
    0000
    0000
    0020
    0000
    0030
    ,  // measure 41
    0100
    0100
    0010
    0010
    0100
    0000
    0000
    0000
    ,  // measure 42
    0000
    0000
    0000
    0000
    1000
    0100
    0010
    0001
    ,  // measure 43
    0010
    0100
    1000
    0100
    0001
    0100
    1000
    0000
    ,  // measure 44
    0000
    0000
    0000
    0000
    ,  // measure 45
    0000
    0010
    0200
    0320
    0230
    0320
    0000
    0030
    ,  // measure 46
    0000
    0000
    0000
    0000
    ,  // measure 47
    0000
    1000
    1000
    1000
    0001
    0001
    0001
    0010
    ,  // measure 48
    0100
    1000
    0100
    0010
    0001
    0100
    0010
    1000
    ,  // measure 49
    0010
    0100
    0001
    0010
    0100
    1000
    0100
    0010
    ,  // measure 50
    0001
    0010
    0100
    1000
    0100
    0100
    0010
    0010
    ,  // measure 51
    0001
    0001
    1000
    1000
    0001
    0001
    0010
    0010
    ,  // measure 52
    0100
    0100
    1000
    0100
    0010
    1001
    0000
    0000
    ,  // measure 53
    0000
    0000
    0000
    0000
    ,  // measure 54
    0000
    0000
    0000
    0000
    1001
    1000
    0100
    0010
    ,  // measure 55
    0001
    0010
    0100
    1000
    0100
    0010
    0001
    0010
    ,  // measure 56
    0100
    1000
    0010
    0100
    0001
    0100
    0010
    1000
    ,  // measure 57
    0010
    0100
    0001
    0100
    0010
    1000
    0001
    1000
    ,  // measure 58
    0001
    1000
    0001
    1000
    1001
    0000
    0000
    0000
    ;
    // measure 0
    0000
    0000
    0000
    0000
    ,  // measure 1
    0000
    0000
    0000
    0000
    ,  // measure 2
    0000
    0000
    0000
    0000
    ,  // measure 3"""