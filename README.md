# super-system-ascii
Convert images into ASCII art on command line


# How to use
1. Make sure you have the required libraries in `requirements.txt`.
2. Navigate to the root directory
3. Do `python main.py <path-to-.ttf> <path-to-img>`, which creates an output image and a text file with the characters (in the same directory as main.py)
`<path-to-.ttf>`: Path to a .ttf file (representing the font to use). We would highly recommend a monospaced font (but see below)
`<path-to-img>`: Path to the image file to convert. .png, whatever works probably, not tested thoroughly.

# Additional options
`-o <NAME>`: specifies the output name. DO NOT include a file extension, we create a .txt and a .png file
`-s <SIZE>`: specifies the font size to use. Defaults to 16. Smaller font size = more details can be captured.
`-I`: Use inverted mode: draws white text on black background instead. Useful if your image is too dark ...
`-c`: Use cheats: draws each character monospaced. Useful if you specify a font that is not monospaced. 
`-p`: Use pretty mode: Adds colors to the image. Work in progress.
`-b`: Use black-white mode: Makes the image black-and-white (instead of monochrome). 
