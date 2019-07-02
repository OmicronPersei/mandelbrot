#! /usr/bin/python3
from PIL import Image, ImageDraw
import random, time
import multiprocessing
from multiprocessing.pool import ThreadPool
from concurrent.futures import ProcessPoolExecutor
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
# width = 1920*3
# height = 1080*3
width=10000
height=10000

# #reduce render time for debugging
# width = 600
# height = 400

# Our plane on which we plot the points
realNeg = -1.5
realPos = -1.00
imagiNeg = 0
imagiPos = 0.5

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

max_workers = multiprocessing.cpu_count() - 1
amount_chunks = 200

width_chunks = []
chunk_size = width // amount_chunks
for i in range(amount_chunks):
	if i == (amount_chunks- 1):
		width_chunks.append(range(i*chunk_size, width))
	else:
		width_chunks.append(range(i*chunk_size, (i+1)*chunk_size))

def process_chunk(chunk_range):
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
			result = (([i,j]), (color, color, color))
			chunk_results.append(result)
	return chunk_results

def main():
	with ProcessPoolExecutor(max_workers) as executor:
		result_chunks = executor.map(process_chunk, width_chunks)
		for i,result_chunk in enumerate(result_chunks, 1):
			print("result chunk {}/{}".format(str(i), str(amount_chunks)))
			for result in result_chunk:
				draw.point(result[0], result[1])

	print("writing image...")
	im.save('output.png', 'PNG')
	print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
	main()
