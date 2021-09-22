#!/usr/bin/python3

import argparse, os, re;

# a feh caption reparsing utility for use as an external command for quick caption block editing in feh
# supports style, font, color changes through external feh commands

argparser = argparse.ArgumentParser(description='reparses caption markup by block/type');
argparser.add_argument('-s', '--source', required=True, dest='source', help='source file');
argparser.add_argument('-b', '--block', required=True, dest='block', help='block position tag');
argparser.add_argument('-o', '--output', required=True, dest='output', help='output file');
argparser.add_argument('-m', '--mode',  required=True, dest='mode', help='change mode');
argparser.add_argument('-n', '--new',  required=True, dest='new', help='new value to use');
argparser.add_argument('-d', '--debug', required=False, default=False, dest='debug', help='verbose debug logging');
args = argparser.parse_args();

# read in the input source file
f = open(args.source);
source = f.readlines();
f.close();

# value definitions
colors = [
    'black',
    'blue',
    'red',
    'white',
    'pink',
    'green',
];

styles = [
    'plain',
    'outline',
    'bubble',
    'box',
];

fonts = [
    'blambot',
    'backissues',
    'grunge',
];

# status vars
last = {
    'color': 0,
    'style': 0,
    'font': 'blambot',
    'size': 18,
    'found': False,
};
lasts = [last.copy(),];
blocks = [[]];
targetblock = blocks[-1] if args.block == '' else None;

# patterns
position_pattern =  re.compile(r"#\d+,\d+");
colors_pattern =    re.compile(r"#(" + "|".join(colors) +  ")");
styles_pattern =    re.compile(r"#(" + "|".join(styles) +  ")");
fonts_pattern =     re.compile(r"#font:(\w+)/(\d+)");

for line in source:

    match = {
        'position': position_pattern.match(line),
        'color':    colors_pattern.match(line),
        'style':    styles_pattern.match(line),
        'font':     fonts_pattern.match(line),
    };

    if(match['position']):
        blocks.append([]);
        lasts.append(last.copy());
        #print('position: ', line);
        if(match['position'][0] == '#' + args.block):
            targetblock = blocks[-1];

    elif(match['color']):
        last['color'] = colors.index(match['color'][1]);
        #print('color: ', line, last['color']);
        if(args.mode == 'color' and targetblock == blocks[-1]):
            lasts[-1]['found'] = True;
            blocks[-1].append("#%s\n" % (colors[(last['color'] + eval("0%s" % args.new)) % len(colors)]));
            continue;
        elif(args.mode == 'clean'):
            continue;

    elif(match['style']):
        last['style'] = styles.index(match['style'][1])
        #print('style: ', line, last['style']);
        if(args.mode == 'style' and targetblock == blocks[-1]):
            lasts[-1]['found'] = True;
            blocks[-1].append("#%s\n" % (styles[(last['style'] + eval("0%s" % args.new)) % len(styles)]));
            continue;
        elif(args.mode == 'clean'):
            continue;

    elif(match['font']):
        last['font'] = match['font'][1];
        last['size'] = int(match['font'][2]);
        #print('font: ', line, last['font'], last['size']);
        if(args.mode == 'fontsize' and targetblock == blocks[-1]):
            lasts[-1]['found'] = True;
            blocks[-1].append("#font:%s/%s\n" % (last['font'], (last['size'] + eval("0%s" % args.new))));
            continue;
        elif(args.mode == 'font' and targetblock == blocks[-1]):
            lasts[-1]['found'] = True;
            blocks[-1].append("#font:%s/%s\n" % (fonts[(fonts.index(last['font']) + eval("0%s" % args.new)) % len(fonts)], last['size']));
            continue;
        elif(args.mode == 'clean'):
            continue;

    # add it to the blocks array
    blocks[-1].append(line);

# check if it was found and replaced, if not, wedge it in
index = blocks.index(targetblock);
last = lasts[index];
if(not last['found']):
    if(args.mode == "color"):
        targetblock.insert(min(1, index), "#%s\n" % (colors[(last['color'] + eval("0%s" % args.new)) % len(colors)]));
    elif(args.mode == "style"):
        targetblock.insert(min(1, index), "#%s\n" % (styles[(last['style'] + eval("0%s" % args.new)) % len(styles)]));
    elif(args.mode == "font"):
        targetblock.insert(min(1, index), "#font:%s/%s\n" % (fonts[(fonts.index(last['font']) + eval("0%s" % args.new)) % len(fonts)], last['size']));
    elif(args.mode == "fontsize"):
        targetblock.insert(min(1, index), "#font:%s/%s\n" % (last['font'], (last['size'] + eval("0%s" % args.new))));

if(args.debug):
    import pprint;
    pprint.pprint(targetblock);
    print('-------');
    pprint.pprint(blocks);

# output the contents back to file
outf = open(args.output, 'w');
outf.writelines([line for block in blocks for line in block]);
outf.close();

