#! /usr/bin/python3
from PIL import Image, ImageDraw
import random, time
import multiprocessing
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
import threading

start_time=time.time()

''' In order to understand the following code, first look up the Mandlebrot Set
You will soon come across lots of foreign terms like complex numbers and the complex plane
Learn what those mean. Example of a complex number: (-1.9890625000000006 + 0.45624999999995547j) '''
def mandelbrot(c):
	# We do this 80 times to make sure a certain complex number is indeed part of the Mandlebrot Set
	z=[None] * 80
	z[0]=0
	
	for n in range(1,80):
		z[n] = z[n-1]**2 + c
		# If it's distance is greater than 2 from (0,0) NOT part of set
		if abs(z[n]) > 3:
			return n
	# If n reaches 80, it's distance is less than 2 from (0,0) it IS part of the set and n = 80
	return n

# Image size (pixels)
width = 1920
height = 1080 

# #reduce render time for debugging
# width = 600
# height = 400

# Our plane on which we plot the points
realNeg = -2.15
realPos = 1.15
imagiNeg = -1.15
imagiPos = 1.15

# Divide our plane into the number of pixels
realIncrement = (realPos - realNeg) / width
imagiIncrement = (imagiPos - imagiNeg) / height

# Store all complex numbers and their corresponding pixels into a list
realPlots = [None] * width
imagiPlots = [None] * height
for i in range(width):
	realNeg += realIncrement
	realPlots[i] = realNeg
for i in range(height):
	imagiNeg += imagiIncrement
	imagiPlots[i] = imagiNeg

''' Standard use of PIL to create a canvas/image object. 
Right now it is set to 0,0,0 ~ a black canvas '''
im = Image.new('RGB', (width, height), (0, 0, 0))
# Assign draw function to a variable for consolidation
draw = ImageDraw.Draw(im)

max_workers = multiprocessing.cpu_count()
print(str(max_workers) + " max workers")

# def chunks(list, chunk_size):
# 	chunks = []
# 	for i in range(0, len(list), chunk_size):
# 		chunks.append(list[i:i+chunk_size])
# 	return chunks

# width_chunks = chunks(range(width), max_workers)

width_chunks = []
chunk_size = width // max_workers
for i in range(max_workers):
	if i == (max_workers - 1):
		width_chunks.append(range(i*chunk_size, width))
	else:
		width_chunks.append(range(i*chunk_size, (i+1)*chunk_size))

def process_chunk(chunk_range):
	print("thread " + str(threading.get_ident()))
	chunk_results = []
	for i in chunk_range:
		for j in range(height):
			c = complex(realPlots[i],imagiPlots[j])
			# n is returned from the mandelbrot function and assigned to varaible
			n = mandelbrot(c)

			# If n is 80, do nothing and the pixel remains black(Our canvas value). Otherwise do the following
			if n != 80:
				''' Depending on n, if it is a HIGH VALUE (like 60) color will be darker(255 = white) (0 = black)
				if n is LOW (like 5), color will be lighter.'''
				color = (255 - int(n * 3.1875))
			# draw.point(([i,j]), (color, color, color-random.randint(50,70)))
			result = (([i,j]), (color, color, color-random.randint(50,70)))
			chunk_results.append(result)
	return chunk_results

executor = ThreadPoolExecutor(max_workers)
result_chunks = executor.map(process_chunk, width_chunks)
for result_chunk in result_chunks:
	for result in result_chunk:
		draw.point(result[0], result[1])

im.save('output.png', 'PNG')
print("--- %s seconds ---" % (time.time() - start_time))
