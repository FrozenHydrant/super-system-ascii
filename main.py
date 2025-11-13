import sys
import getopt

# Our extra classes
import shadegen
import imagemod

def main():
    options = getopt.gnu_getopt(sys.argv[1:], "o:s:cIpb")
    output_name = "output"
    text_size = 16
    cheats = False
    inverted = False
    pretty = False
    bw = False
    
    for shortop in options[0]:
        if shortop[0] == '-o':
            output_name = shortop[1]
        elif shortop[0] == '-s':
            if shortop[1].isnumeric() and int(shortop[1]) > 0:
                text_size = int(shortop[1])
            else:
                print("Invalid size provided. (Must be a positive int)")
                return
        elif shortop[0] == '-c':
            cheats = True
        elif shortop[0] == '-I':
            inverted = True
        elif shortop[0] == '-p':
            pretty = True
        elif shortop[0] == '-b':
            bw = True

    if len(options[1]) != 2:
        print("Not enough arguments supplied! We need a path to the .tff file for the font, and the path to the picture file.")
        return
    
    text_file = options[1][0]
    picture_file = options[1][1]
    
    the_font_information = (text_file, text_size)

    my_shade = shadegen.ShadeGen(inverted, bw)
    my_shade.load_font(the_font_information)
    shaded_list, dimensions, dfont = my_shade.parse_font()

    my_image = imagemod.ImageMod(shaded_list, dimensions, dfont, inverted, pretty, bw)
    my_image.set_image(picture_file)

    my_image.churn(output_name, cheats)

if __name__ == "__main__":
    main()
