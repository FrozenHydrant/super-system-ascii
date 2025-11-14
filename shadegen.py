from PIL import ImageFont, Image, ImageDraw
import numpy as np


class ShadeGen:
    def __init__(self, inverted, bw):
        self.font = None
        self.inverted = inverted
        self.image_mode = "L"
        if bw:
            self.image_mode = "1"
        ordinary_characters = [i for i in range(32,127)]
        #extraordinary_characters = [i for i in range(128,256)]

        self.characters = [] # https://www.geeksforgeeks.org/python/python-ways-to-concatenate-two-lists/
        self.characters += ordinary_characters
        #self.characters += extraordinary_characters

    def load_font(self, the_font_information):
        self.font = ImageFont.truetype(the_font_information[0], the_font_information[1])

    def parse_font(self):
        # https://www.geeksforgeeks.org/python/python-pil-image-new-method/
        # https://www.geeksforgeeks.org/python/adding-text-on-image-using-python-pil/

        # Each character in ASCII gets an image
        # Then we decide how "dark" that symbol is
        # We'll first get the "width" and "height" of each symbol (most common occuring)
        i = 0
        widths = {}

        # Count all "widths" and heights of characters
        while i < len(self.characters):
            my_text = str(bytes([self.characters[i]]), encoding='ascii')

            my_text_size = self.font.getbbox(my_text)
            tw = my_text_size[2] - my_text_size[0]

            if tw in widths:
                widths[tw] += 1
            else:
                widths[tw] = 0
            
            i += 1

        # Then decide what appears the most frequently
        # Some characters have a weird width and are anomalies
        # So we only consider characters with the (most common) width
        max_width_count = max(widths.values())
        width_keys = list(widths.keys())
        most_common_width = 0
        i = 0
        while i < len(widths):
            item = width_keys[i]
            if widths[item] == max_width_count:
                most_common_width = item
                break
            i += 1
            

        # Get the max "printed height" across all valid characters
        i = 0
        max_height = 0
        while i < len(self.characters):
            my_text = str(bytes(self.characters[i]), encoding='ascii')

            my_text_size = self.font.getbbox(my_text)

            # Max printed height is the "bottom" value of the bounding box
            # -> when our text is printed, it takes space from the top to the bottom of the bounding box = effective printed height, even if it starts offset from the top a bit
            max_printed_height = my_text_size[3] 

            max_height = max(max_height, max_printed_height)
            i += 1

        # Now associate each symbol with a shade
        symbol_shade = {}
        
        for i in self.characters:
            my_text = str(bytes([i]), encoding='ascii')

            my_text_size = self.font.getbbox(my_text)
            tw = my_text_size[2] - my_text_size[0]
            if tw == most_common_width:

                img = Image.new(self.image_mode, (most_common_width, max_height), (255))
                img_draw = ImageDraw.Draw(img)
                img_draw.text((-my_text_size[0], -my_text_size[1]), text=my_text, font=self.font)

                img_array = np.array(img.getdata())
                shade = float(np.average(img_array))

                if self.inverted:
                    symbol_shade[my_text] = 255-shade
                else:
                    symbol_shade[my_text] = shade
                #img.save(str(i) + ".png")

        # Then partition the space 0-255 to each symbol
        shade_list = sorted(list(symbol_shade.items()), key=lambda x: x[1])
        new_shade_list = []
        i = 0
        while i < len(shade_list)-1:
            high_value = (shade_list[i][1] + shade_list[i+1][1]) / 2
            new_shade_list.append((shade_list[i][0], high_value))
            i += 1
        # And the last value of the list
        new_shade_list.append((shade_list[i][0], 256))

        print("Got the characters to use and the shade values")
        return new_shade_list, (most_common_width, max_height), self.font
