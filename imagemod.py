from PIL import Image, ImageDraw, ImageFont
import numpy as np



class ImageMod:
    def __init__(self, symbol_list, dimensions, dfont, inverted, colormation, bw):
        self.symbol_list = symbol_list
        self.symbol_dimensions = dimensions
        self.font = dfont
        self.colormation = False
        self.bw = False
        self.image_mode = "L"

        if inverted:
            self.bg_colors = 0
            self.colors = 255
        else:
            self.bg_colors = 255
            self.colors = 0

        # Colormation will override invertedness option and cheats
        if colormation and not bw:
            self.colormation = True
            self.bg_colors = (255,255,255)
            self.colors = (0,0,0)
            self.image_mode = "RGB"

        # Bw will modify all other color options
        if bw:
            self.bw = True
            self.image_mode = "1"
            

    def set_image(self, image_path):
        self.image = Image.open(image_path)

    def draw_all_lines(self, drawing, lines):
        i = 0
        y = 0
        c_red = None
        c_blue = None
        c_green = None

        if self.colormation:
            color_img_data = np.array(self.image.getdata()).reshape((self.image.size[1], self.image.size[0], -1)).astype(np.float64)

            # Don't need transparency if it exists
            if color_img_data.shape[2] > 3:
                color_img_data = color_img_data[:, :, 0:3]

            # Split into channels
            c_red = color_img_data[:, :, 0] 
            c_blue = color_img_data[:, :, 1]
            c_green = color_img_data[:, :, 2]

            # Shrink them and scale them
            c_red = self.shrink_image(c_red) / 255
            c_blue = self.shrink_image(c_blue) / 255
            c_green = self.shrink_image(c_green) / 255

            # Get rid of the luminance component
            # TODO
            
            c_red = (c_red * 255).astype(np.uint8)
            c_blue = (c_blue * 255).astype(np.uint8)
            c_green = (c_green * 255).astype(np.uint8)
        
        while i < len(lines):
            line = lines[i]
            self.draw_line(drawing, line, y, c_red, c_blue, c_green) # Last 3 arguments used for pretty mode
            y += self.symbol_dimensions[1]
            i += 1
            
    def draw_line(self, drawing, line, y, c_red, c_blue, c_green):
        i = 0
        if self.colormation:
            while i < len(line):
                drawing.text((i*self.symbol_dimensions[0], y), line[i], font=self.font, fill=(c_red[int(y/self.symbol_dimensions[1]), i], c_blue[int(y/self.symbol_dimensions[1]), i], c_green[int(y/self.symbol_dimensions[1]), i]))
                i += 1
        else:
            while i < len(line):
                drawing.text((i*self.symbol_dimensions[0], y), line[i], font=self.font, fill=self.colors)
                i += 1

    def shrink_image(self, img_data):
        # Crunch the image
        # If the symbol is 3x6, we need 1/6 the rows and 1/3 the columns,
        # Each pixel a in the new image represents 18 pixels on the original, averaged across all

        # We first crunch the rows
        i = 0
        symbol_h = self.symbol_dimensions[1]
        while i < int(img_data.shape[0]/symbol_h):
            # Current (ith) row value becomes (1/symbol_h)
            img_data[i * symbol_h, :] = img_data[i * symbol_h, :] * (1.0/symbol_h)

            j = 1
            while j < symbol_h:
                # Then add the next (symbol_h - 1) rows to the ith row, each multiplied by (1/symbol_h)
                location = i * symbol_h + j
                img_data[i * symbol_h, :] += img_data[location, :] * (1.0/symbol_h)
                
                j += 1

            # Overall effect: each row becomes the average of the ith symbol_h rows after it (and the image size is reduced by symbol_h times)
            i += 1
            

        # Then grab every (symbol_hth) row to get the shrunken version
        # https://stackoverflow.com/questions/10198747/how-can-i-simultaneously-select-all-odd-rows-and-all-even-columns-of-an-array
        img_data = img_data[::symbol_h, :]

        # Column crunch too
        i = 0
        symbol_w = self.symbol_dimensions[0]
        while i < int(img_data.shape[1]/symbol_w):
            img_data[:, i * symbol_w] = img_data[:, i * symbol_w] * (1.0 / symbol_w)

            j = 1
            while j < symbol_w:
                img_data[:, i * symbol_w] += img_data[:, i * symbol_w + j] * (1.0 / symbol_w)

                j += 1
            i += 1

        # Then grab every (symbol_wth) column to get the shrunken version
        img_data = img_data[:, ::symbol_w]
        return img_data
        
    def churn(self, out_name, cheating):
        print("Processing image data")
        image_dimensions = self.image.size
        # Source - https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
        # Posted by unutbu, modified by community. See post 'Timeline' for change history
        # Retrieved 2025-11-12, License - CC BY-SA 4.0
        gray_img = self.image.convert('L')

        # Turn to data and reshaped in the way the array would be
        # It's listed rows and then columns, so rows = height (we autofill it) and columns = width
        img_data = np.array(gray_img.getdata()).reshape(-1, image_dimensions[0]).astype(np.float64)
        img_data = self.shrink_image(img_data)

        # Debug print
        i = 0
        while i < img_data.shape[0]:
        #    print(img_data[i, :])
            i += 1

        # Change each value out to the one specified in the symbol table
        my_chars = np.zeros(shape=img_data.shape).astype(np.str_)
        i = 0
        while i < len(self.symbol_list):
            item, threshold = self.symbol_list[i]
            # https://stackoverflow.com/questions/16343752/numpy-where-function-multiple-conditions
            my_chars[(img_data <= threshold) & (my_chars == '0.0')] = item
            i += 1

        # Add the newlines on the end of each row
        my_chars = np.concat((my_chars, np.full(shape=(my_chars.shape[0], 1), fill_value='\n')), axis=1)

        
        # Turn to a disgustingly long string
        # Go through all the lists and concatenate them into a big string
        l = my_chars.tolist()
        
        i = 0
        my_string = ""
        while i < len(l):

            c_line = "".join(l[i])
            my_string += c_line
            i += 1

        print("Image now generating...")
        # Image gen
        img = Image.new(self.image_mode, image_dimensions, color=self.bg_colors)
        draw_img = ImageDraw.Draw(img)

        # We want all characters placed uniformly according to their size specification (cheating)
        if cheating or self.colormation:
            print("Cheats are on: (each character is placed monospace), the image will look nice but viewing the text in a text editor probably won't.")
            self.draw_all_lines(draw_img, my_string.split("\n"))
        else:
            print("Cheats are off: each character in the image is drawn as would appear in a texteditor / other text viewing medium")
            draw_img.multiline_text((0,0), text=my_string, spacing=0, font=self.font, fill=self.colors)
        img.save(out_name + ".png")

        try:
            with open(out_name + ".txt", "w") as w:
                w.write(my_string)
        except:
            with open(out_name + ".txt", "x") as w:
                w.write(my_string)
