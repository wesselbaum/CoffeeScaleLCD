def fillUpLine(text, length=16):
    return text.ljust(length)


def generateRatioStrenthLine(ratioWater, length=16):
    ratio = '1:' + str(ratioWater);
    paddedRatio = fillUpLine(ratio, 4);

    stengthBar = "{0xFF}{0xFF}{0xFF}{0xD0}{0xD0}";
    if(ratioWater < 12):
        stengthBar = "{0xFF}{0xFF}{0xFF}{0xFF}{0xFF}";
    elif(ratioWater < 15):
        stengthBar = "{0xFF}{0xFF}{0xFF}{0xFF}{0xD0}";
    elif(ratioWater < 18):
        stengthBar = "{0xFF}{0xFF}{0xFF}{0xD0}{0xD0}";
    elif(ratioWater < 21):
        stengthBar = "{0xFF}{0xFF}{0xD0}{0xD0}{0xD0}";
    elif(ratioWater < 24):
        stengthBar = "{0xFF}{0xD0}{0xD0}{0xD0}{0xD0}";
    else:
        stengthBar = "{0xD0}{0xD0}{0xD0}{0xD0}{0xD0}";
    return paddedRatio + "  |  " + stengthBar + "  "
        

        