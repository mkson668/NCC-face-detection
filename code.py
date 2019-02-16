from PIL import Image, ImageDraw
import numpy as np
import math
from scipy import signal
import ncc

def MakePyramid(image, minsize):
    scaledim = image
    imlist = []
    # append original image to list
    imlist.append(scaledim)
    # if scaled image height or width is larger than minsize add to list and keep scaling down 
    while scaledim.size[0] > minsize or scaledim.size[1] > minsize:
        scaledim = scaledim.resize((int(scaledim.size[0] * 0.75), int(scaledim.size[1] * 0.75)), Image.BICUBIC)
        imlist.append(scaledim)
    return imlist


def ShowPyramid(pyramid):
    offset_x = 0
    width = 0
    # use largest image for height
    height = pyramid[0].size[1]
    # get total width for all images
    for im in pyramid:
        width += im.size[0]
    image = Image.new("RGBA", (width,height), (255,255,255,0))
    # paste all images in pyramid
    for im in pyramid:
        image.paste(im, (offset_x,0))
        offset_x += im.size[0]
    return image

def FindTemplate(pyramid, template, threshold):
    template_maxdim = 15
    template_resize = template
    ncc_results = []
    level = 0
    all_loc = []
    scale = 0.75
    # resize template to 15 pixel width or height
    while template_resize.size[0] > template_maxdim or template_resize.size[1] > template_maxdim:
        template_resize = template_resize.resize((int(template_resize.size[0] * scale), int(template_resize.size[1] * scale)), Image.BICUBIC)
    # convert all PIL images in pyramid using ncc and store
    for im in pyramid:
        ncc_results.append(ncc.normxcorr2D(im, template_resize))
    # for each ncc result store coordinates and scale that exceed threshold
    for a in ncc_results:
        for row in range(a.shape[0]):
            for col in range(a.shape[1]):
                if a[row, col] > threshold:                    
                    all_loc.append([a[row, col], row, col, level])
        level += 1
    # helper to draw boxes
    return_im = MakeBox(all_loc, pyramid[0], scale)
    return return_im

# draws all the boxes on the given image given an array of coordinates at specific scales
def MakeBox(array, image, scale):
    im = image.convert('RGB')
    draw = ImageDraw.Draw(im)
    for a in array:
        x = a[2]
        y = a[1]
        lvl = a[3]
        draw.line(((x-5)/(scale**lvl),(y-8)/(scale**lvl),(x+8)/(scale**lvl),(y-8)/(scale**lvl)),fill="blue",width=2)
        draw.line(((x-5)/(scale**lvl),(y-8)/(scale**lvl),(x-5)/(scale**lvl),(y+8)/(scale**lvl)),fill="blue",width=2)
        draw.line(((x+8)/(scale**lvl),(y+8)/(scale**lvl),(x+8)/(scale**lvl),(y-8)/(scale**lvl)),fill="blue",width=2)
        draw.line(((x+8)/(scale**lvl),(y+8)/(scale**lvl),(x-5)/(scale**lvl),(y+8)/(scale**lvl)),fill="blue",width=2)
    im.show()
    del draw
    return im

