from math import floor
from PIL import Image
import random
import sys
import PIL

if len(sys.argv) > 1:
    try:
        image = Image.open(sys.argv[1])
    except:
        print('[ERROR] Invalid image file')
else:
    print('[ERROR] No image provided')
    sys.exit()

#Following are globals that can be used
w, h = image.size[0], image.size[1]
pixels = image.load()
final_image = []
neighbours = ((1, 1), (-1, 1), (1, -1), (-1, -1),
                (0, 1), (-1, 0), (1, 0), (0, -1))

#Demonstration of performing an average
def average(pixel):
    Sum = 0
    for pix in pixel:
        Sum += pix
    avg = int(round(Sum / len(pixel)))
    return avg

#Sequence generator for pixel data
def seq_image():
    global pixels
    for x in range(h):
        for y in range(w):
            yield pixels[y, x]

#Function for enabling the reuse of the output of another function
def prepare_reiterate():
    global pixels, final_image
    tmp = Image.new('RGB', (w, h))
    tmp.putdata(final_image)
    pixels = tmp.load()
    final_image = []

def greyscale():
    global w, h, pixels, final_image
    for x in range(h):
        for y in range(w):
            pixel = pixels[y, x]
            avg = average(pixel)
            final_image.append((avg, avg, avg))

def edge_jumbler():
    global w, h, pixels, final_image
    ratio = (w * h) / 256
    final_image = list(seq_image())
    for i, pix in enumerate(seq_image()):
        swp_target = int(floor(average(pix) * ratio))
        tmp = final_image[i]
        final_image[i] = final_image[swp_target]

def incremental_brightness():
    global w, h, pixels, final_image
    bright = 0
    for x in range(h):
        for y in range(w):
            pixel = list(pixels[y, x])
            bright += 1
            if bright > 255:
                bright -= 255
            for i in range(3):
                pixel[i] += pixel[i] + bright
                if pixel[i] > 255:
                    pixel[i] -= 256
            final_image.append(tuple(pixel))

def random_brightness():
    global w, h, pixels, final_image
    for x in range(h):
        for y in range(w):
            pixel = list(pixels[y, x])
            bright = random.uniform(0, 1)
            for i in range(3):
                pixel[i] += int(pixel[i] * bright)
                if pixel[i] > 255:
                    pixel[i] -= 256
            final_image.append(tuple(pixel))

def random_displacer(thresh):
    global w, h, pixels, final_image, neighbours
    for x in range(h):
        for y in range(w):
            pixel = pixels[y, x]
            for neighbour in neighbours:
                if random.uniform(0, 1) < thresh:
                    tmp = pixel
                    try:
                        pixels[y, x] = pixels[y + neighbour[0], x + neighbour[1]]
                        pixels[y + neighbour[0], x + neighbour[1]] = tmp
                    except:
                        pass
                    break
            final_image.append(pixel)

def scratches(thresh, prop_length):
    propagation = 0
    prev = None
    for x in range(h):
        for y in range(w):
            pixel = pixels[y, x]
            if propagation > 0:
                pixel = prev
                propagation -= 1
            elif random.uniform(0, 1) < thresh:
                prev = pixel
                propagation = random.randint(0, prop_length)
            final_image.append(pixel)

def worms(amount, minP, thresh):
    global w, h, pixels, final_image, neighbours
    for spawn in range(amount):
        y, x = random.randint(0, w-1), random.randint(0, h-1)
        init = minP
        original = pixels[y, x]
        cutneighbours = neighbours[4:]
        choice = random.randint(1, 4)
        if choice == 1:
            chosen_neighbours = cutneighbours[0:3]
        elif choice == 2:
            chosen_neighbours = cutneighbours[1:4]
        elif choice == 3:
            chosen_neighbours = [cutneighbours[0], cutneighbours[2], cutneighbours[3]]
        else:
            chosen_neighbours = [cutneighbours[0], cutneighbours[1], cutneighbours[3]]
        while (random.uniform(0, 1) < thresh) or (init > 0):
            newy, newx = -1, -1
            while not ((0 <= newy < w) and (0 <= newx < h)):
                nextpix = chosen_neighbours[random.randint(0, 2)]
                newy, newx = y + nextpix[0], x + nextpix[1]
            y, x = newy, newx
            pixels[y, x] = original
            init -= 1
    for x in range(h):
        for y in range(w):
            final_image.append(pixels[y, x])

def compress(thresh):
    global w, h, pixels, final_image
    final_image = list(seq_image())
    start, stop = 0, 0
    avgstart = average(final_image[0])
    avglist = []
    for i, pixel in enumerate(seq_image()):
        pixavg = average(pixel)
        if ((-thresh * avgstart) <= pixavg <= (thresh * avgstart)) or len(avglist) < 1:
            avglist.append(pixavg)
            stop = i
        else:
            colour = average(avglist)
            for i in range(start, stop):
                final_image[i] = (colour, colour, colour)
            start = stop + 1
            avglist = []
            avgstart = average(final_image[start])

outimage = Image.new('RGB', (w, h))
outimage.putdata(final_image)
outimage.save('/home/mark/prog/outimage.png')
