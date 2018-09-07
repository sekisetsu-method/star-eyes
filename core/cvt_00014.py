#!/usr/bin/env python
# -*- coding: utf8 -*-
print(unicode("積雪メソッド","UTF-8"))

__author__ = "Arlo Emerson <arlo.emerson@sekisetsumethod.com>"
__status__  = "production"
__version__ = "14.0"
__date__    = "17 August 2018"

#--- LICENSE ------------------------------------------------------------------
# This code cvt_[version number].py and all software created by Sekisetsu Method and or Arlo Emerson or other designated authors covered by the MIT License.

# MIT License

# Copyright (c) 2017, 2018 Arlo Emerson, Sekisetsu Method

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#--- THE SEKISETSU METHOD EXPLAINED -------------------------------------------
'''
WHAT IT IS
Sekisetsu is a Japanese word for snowfall accumulation. The Sekisetsu Method (積雪メソッド) is a technical analysis tool combining price action geometry (candlesticks) with fluid dynamics to reveal otherwise hidden structure and market participant intention, and displays this information on a price chart. The method can also be termed "Price Action Fluid Dynamics". Many terms and ideas from fluid dynamics and chaotic systems are borrowed and used both in the code and as allegory in the training material. Regardless of terminology, the goal of the method is to empower the user to align trades with larger players. 

HOW IT WORKS
OHLC price action data (in the form of a modified candlestick chart) creates the surfaces and boundaries within a control volume tank (CVT). The tank is filled with both heavy and light particles. The particles accumulate in the cavities and recesses of the price action surfaces. The pooling of particles results in three patterns: top-heavy, bottom-heavy and stagnant accumulations. These differences can be viewed directly on the chart, and are further expressed as an "imbalance ratio histogram". A standard deviation method is employed to locate relatively stagnant periods of price action. It is these periods of lower volotility coinciding with imbalances in particle accumulation where major entry signals emerge, revealing both the location and trading direction of large players, i.e. market makers. 

The software is open source, highly configurable, and easily lends itself to integration with existing trading systems.
'''

#--- USAGE --------------------------------------------------------------------
# • CSV files need to live in the "csv" folder at project root. 
# • Histograms are created in the "histograms" folder at project root.
# • Simulations (frame by frame PNGs of the simulation) are created in the "simulations" folder at project root.

# To run the program: 
# • Use PIP to install all requirements (see requirements.txt).
# • Add CSV files to the "csv" folder at project root.
# • If running native linux, comment out os.environ['SDL_VIDEODRIVER']='dummy'
# 	(this is a Windows workaround when running the Ubuntu shell on Windows)
# • from a shell, run:
# 	$ python cvt_[version_number].py
#------------------------------------------------------------------------------

#--- NOTES --------------------------------------------------------------------
# Project website with how-to and trading ideas: http://www.sekisetsumethod.com

# See the README file for detailed information on usage.
# See http://www.sekisetsumethod.com for charts, signals and training.

# Thanks to Maarten Baert's excellent physics engine (licensed under LGPL).
# More info: http://www.maartenbaert.be/extremephysics/
#------------------------------------------------------------------------------

import os as os
os.environ['SDL_VIDEODRIVER']='dummy' # Use this if running the Ubuntu bash on windows
import pygame, sys, math, random, csv, glob, subprocess, shutil, heapq, argparse, textwrap
import lib.standard_deviation_function as sdef
import lib.TextColors as TextColors
from lib.extremephysics import *
from numpy import interp
from PIL import Image, ImageDraw

target_dir = "../csv/"
file_type = '.csv'
particle_birth_count = 1280 # should match window width


# Particle/fluid simulations occur within a Control Volume Tank. 
# The current settings in this version are tuned to USDJPY 15 and 30 minute chart data.
class ControlVolumeTank():

	def __init__(self):
		print(self.__class__.__name__, __version__)
		print("Running " + TextColors.HEADERLEFT3 + TextColors.INVERTED + self.__class__.__name__ + " " + \
			TextColors.ENDC + " version " + __version__ + " of Sekisetsu Method Star Eyes fork.")

		self.dataset_file = '' # overridden
		self.save_sequences = True
		self.particles_birth_count = 0 # overridden
		self.FRAME_LIMIT = 200 # 200 for production
		self.render_frames_directory = "../simulations/"
		self.render_histogram_directory = "../histograms/"
		self.code_name = "star_eyes"
		self.permutation_name = __version__
		self.histogram_animation_directory = self.code_name + "_" + __version__ + "/" 
		self.PARTICLE_SHAPE_MODE = "CIRCLE"
		self.PARTICLE_DIAMETER = .1
		self.COEFFICIENT_RESTITUTION = 0.1 #0.01
		self.FRICTION = 0.1
		self.DATASET_HIGHEST_INDEX = 0
		self.DATASET_LOWEST_INDEX = 0
		self.draw = ImageDraw.Draw

		self.previous_sdev_x = 0
		self.previous_sdev_y = 900
		self.standard_dev_start_y = 900 # these should match

		self.previous_sdev_vol_x = 0
		self.previous_sdev_vol_y = 850
		self.standard_dev_vol_start_y = 850

		self.FRAME_RATE = 24 
		self.CANDLESTICK_WIDTH = 1
		self.new_x_default_value = 10
		self.CONTAINER_WALLS_WIDTH = 2
		self.CANDLE_GUTTER = 3
		self.run = True
		self.DATASET_LOWEST = 107 # overridden, used for scaling the chart into this game window
		self.DATASET_HIGHEST = 111  # overridden
		self.offset_index = 0 # used for cycling through the T axis
		self.truncated_dataset_file_name = ""
		self.PAINTABLE_LIMIT = 1268 # used as a canvas limit so there are some venting gaps on L and R side of chart
		self.HEIGHT_SCALING_FACTOR = 1.1 # set to 1.2 initially. if things are getting truncated, lower this number to fit more into the screen
		# note: set to negative number to do interesting head-on particle collisions.

		random.seed()
		pygame.display.init()
		pygame.font.init()
		self.fpsclock = pygame.time.Clock()
		self.WINDOW_WIDTH = 1280
		self.WINDOW_HEIGHT = 720
		self.surf_window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
		self.font = pygame.font.SysFont("Sans", 12)	
		self.font_large = pygame.font.SysFont("Sans", 24)	
		self.cx = self.WINDOW_WIDTH / 2
		self.cy = self.WINDOW_HEIGHT / 2
		self.mouse_x = 0
		self.mouse_y = 0
		self.color_static = pygame.Color(52, 30, 162)
		self.COLOR_STANDARD_DEVIATION = pygame.Color("yellow")		
		self.COLOR_STANDARD_DEVIATION_VOL = pygame.Color("blue")		
		self.COLOR_HEAVY_PARTICLES = pygame.Color(0, 146, 255)
		self.COLOR_LIGHT_PARTICLES = pygame.Color(255, 0, 255)
		self.COLOR_HISTOGRAM_UP = (0, 146, 255)
		self.COLOR_HISTOGRAM_DOWN = (255, 0, 255)
		self.COLOR_ENTRY_SIGNAL = (0, 255, 100)
		self.MOUSE_HINGE_JOINT = -1.0
		self.edge_boxes = []
		self.candlestick_boxes = []
		self.heavy_particles = []
		self.light_particles = []
		self.standard_dev_list = []
		self.standard_dev_list_vol = []
		self.new_x = self.new_x_default_value
		self.index_counter = 0
		self.verbose = False
		self.debug = False
		self.candleIndex = 0
		self.highlight_sigma = True # can be overridden by passing in -highlight_sigma argument
		self.sigma_period = 17 # can be overridden by passing in -sigma_period argument
		self.show_histogram_ratio = True
		self.show_histogram_standard_dev = False
		self.histogram_standard_dev_period = 7
		self.show_histogram_simple_average = False
		self.histogram_simple_average_period = 9
		self.sigma_sort_low = 40 # the number of sigma lines to draw
		self.offset_index_override = 0 # the index of the candle to begin a simulation
		self.sample_period_size = 0 # override this to e.g. 10, and set the offset_index_override to e.g. 55 
		self.permutation_index = 0 # the outer loop index, this will be appended to file name, and is useful for running multiple simulations on one dataset in order to observe variances in particle distribution

		helpMessage = 'See README.md and setup_instructions.md for specifics. Here are some commands to try: \n' + \
			"• Standard deviation of price (SD, yellow line) + Volume SD (blue line) + 100 lowest sigma values highlighted in green: " + TextColors.OKGREEN + 'python cvt_00014.py --sigma_period 17 -hrat 1 -v -ssl 100' + TextColors.ENDC + "\n" + \
			"• Price SD + lowest sigma values highlighted in green: " + TextColors.OKGREEN + 'python cvt_00014.py --sigma_period 23 --highlight_sigma True -v ' + TextColors.ENDC + "\n" + \
			"• Price SD + histogram SD of particle distribution: " + TextColors.OKGREEN +  "python cvt_00014.py --sigma_period 19 -v -hrat False -hsd True -hsdp 34" + TextColors.ENDC + "\n" + \
			"• Price SD + histogram moving average (MA) of particle distribution: " + TextColors.OKGREEN +  "python cvt_00014.py --sigma_period 17 -v -hrat False -hsa True -hsap 23" + TextColors.ENDC + "\n" + \
			"• Price SD + histogram MA with a larger set of low SD highlighted: " + TextColors.OKGREEN +  "python cvt_00014.py --sigma_period 34 -v -hrat True -ssl 100" + TextColors.ENDC + "\n" + \
			"• Start at some other index in the dataset (e.g. 120 candles from latest): " + TextColors.OKGREEN +  "python cvt_00014.py --sigma_period 34 -v -oo 120 -hrat 1" + TextColors.ENDC + "\n" + \
			"• Start at some other index and march forward N candles: " + TextColors.OKGREEN +  "python cvt_00014.py --sigma_period 34 -v -oo 120 -sps 10 -hrat 1" + TextColors.ENDC + "\n" + \
			"• Run a series of simulations at the same index: " + TextColors.OKGREEN +  "python cvt_00014.py --sigma_period 23 -v -oo 127 -hrat 1 -ssl 1" + TextColors.ENDC + "\n" + \
			" "

			
		parser = argparse.ArgumentParser(description=helpMessage, epilog=textwrap.dedent(""), formatter_class=argparse.RawTextHelpFormatter)
		parser.add_argument('-s', '--highlight_sigma', dest='highlight_sigma', required=False, help="Paint lines from low sigma regions to the top of the chart. This helps isolate important areas in the histogram.")
		parser.add_argument('-p', '--sigma_period', dest='sigma_period', required=False, help="The sigma period used to calculate the standard deviation. Default is 17.")
		parser.add_argument('-hrat', '--show_histo_ratio', dest='show_histo_ratio', required=False, help="Show the histogram ratio lines.")
		parser.add_argument('-hsd', '--show_histo_sd', dest='show_histo_sd', required=False, help="Show a standard deviation line of the histogram.")
		parser.add_argument('-hsdp', '--histo_sd_period', dest='histo_sd_period', required=False, help="Histogram standard deviation period. Default is 7.")
		parser.add_argument('-hsa', '--show_histo_simple_average', dest='show_histo_simple_average', required=False, help="Show a simple average line of the histogram.")
		parser.add_argument('-hsap', '--histo_simple_average_period', dest='histo_simple_average_period', required=False, help="Histogram simple average period. Default is 9.")
		parser.add_argument('-ssl', '--sigma_sort_low', dest='sigma_sort_low', required=False, help="The number of samples to use for highlighting the low points in sigma. Default is 40. Higher numbers will add more lines and include a larger range.")
		parser.add_argument('-oo', '--offset_index_override', dest='offset_index_override', required=False, help="The index of the current data set to begin at. This is helpful if you see a breakout candle somewhere in the past and want to run the simulation with that price being at the far right of the chart.")
		parser.add_argument('-sps', '--sample_period_size', dest='sample_period_size', required=False, help="The size of the sample set of candles to run a simulation on. Use with offset index override -oo.")

		parser.add_argument('-v','--verbose', dest='verbose', action='store_true', help="Explain what is being done.")
		parser.add_argument('-d','--debug', dest='debug', action='store_true', help="Lower level messages for debugging.")		
		parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

		args = parser.parse_args()
		
		if args.verbose:
			self.verbose = True

		if args.debug:
			self.debug = True

		if self.string_to_bool(args.highlight_sigma):
			self.highlight_sigma = True

		if self.string_to_bool(args.show_histo_ratio): 
			self.show_histogram_ratio = True
		else:
			self.show_histogram_ratio = False

		if args.sigma_period: 
			self.sigma_period = int( args.sigma_period )

		if args.sigma_sort_low: 
			self.sigma_sort_low = int( args.sigma_sort_low )

		if self.string_to_bool(args.show_histo_sd): 
			self.show_histogram_standard_dev = True

		if args.sample_period_size:
			self.sample_period_size = int(args.sample_period_size)

		if args.histo_sd_period:
			self.histogram_standard_dev_period = int(args.histo_sd_period)

		if self.string_to_bool(args.show_histo_simple_average): 
			self.show_histogram_simple_average = True

		if args.histo_simple_average_period:
			self.histogram_simple_average_period = int(args.histo_simple_average_period)

		if args.offset_index_override:
			self.offset_index_override = int(args.offset_index_override)

		if args.debug and args.verbose:
			self.print_debug("Running in verbose mode with debug messages.")
		elif args.debug and not args.verbose:
			self.print_debug("Running in debug mode.")
		elif args.verbose and not args.debug:
			self.print_verbose("Running in verbose mode.")
	
	def string_to_bool(self, pArg):
  		if None == pArg:
  			return False
  		elif pArg.lower() in ("y", "yes", "true", "t", "1"):
  			return True
  		else:
  			return False

	def set_dataset_file(self, pFileName):
		self.dataset_file = pFileName

	def draw_box(self, x, y, w, h, rot, color):
		points = [[-w / 2.0, -h / 2.0], [w / 2.0, -h / 2.0], [w / 2.0, h / 2.0], [-w / 2.0, h / 2.0]]
		for p in points:
			p[:] = [x + p[0] * math.cos(rot) + p[1] * math.sin(rot), y - p[0] * math.sin(rot) + p[1] * math.cos(rot)]
		pygame.draw.polygon(self.surf_window, color, points, 1)

	def draw_circle(self, x, y, d, color):
		points = [[-d / 2.0, -d / 2.0], [d / 2.0, -d / 2.0]]
		pygame.draw.circle(self.surf_window, color, [x,y], d/2, 1)
		# circle(Surface, color, pos, radius, width=0) -> Rect

	# for drawing a progress bar
	def draw_growing_rectangle(self, pInt):
		points = (20,20,50+pInt, 30)
		# TODO: make this grow automatically
		pygame.draw.rect(self.surf_window, self.COLOR_STANDARD_DEVIATION, points, 1)

	def draw_standard_dev_line(self, pCoords):
		pygame.draw.line(self.surf_window, self.COLOR_STANDARD_DEVIATION, pCoords[0], pCoords[1], 1)

	def draw_standard_dev_line_vol(self, pCoords):
		pygame.draw.line(self.surf_window, self.COLOR_STANDARD_DEVIATION_VOL, pCoords[0], pCoords[1], 1)

	def init_dataset(self):	
		csvfile = open(self.dataset_file, 'r')
		lines = csvfile.readlines() 
		
		rowCount = 0
		for row in lines:
			rowCount += 1
		
		tmpDataSet = []

		# this reverse orders the orig data so we can paint from left to right with it
		startIndex = rowCount - self.offset_index - 315

		for i in range( startIndex, rowCount - self.offset_index ):
			tmpDataSet.append(lines[i])
		
		self.dataset = tmpDataSet

		tmpList = []
		tmpCount = 0

		for row in self.dataset:
			# if tmpCount > 0:			
			# this is to determine the min/max
			# tmpTruncatedRow = row[1:4] # works for dukascopy
			rowList = row.split(",")
			# self.print_debug(rowList)
			tmpTruncatedRow = rowList[2:6] # works for metatrader
			# self.print_debug(tmpTruncatedRow)

			if tmpTruncatedRow != []:
				tmpList.append(  max(tmpTruncatedRow)  )
				tmpList.append(  min(tmpTruncatedRow)  )

			# if tmpCount == 0:
			# 	tmpCount = 1

		self.DATASET_LOWEST = int( round( float( min(tmpList))  ) ) -1
		self.DATASET_HIGHEST = int( round( float( max(tmpList))  ) ) +1

		# firstRowRead = 0
		for row in self.dataset:
			self.paint_candle(row) # returns 0 if row volume is empty
			self.candleIndex += 1

		self.print_verbose( str(self.candleIndex) + " records in data set" )

		slashLocation = self.dataset_file.rfind('/') 
		directory = self.dataset_file[slashLocation+1:]
		self.truncated_dataset_file_name = directory[:-4] #trim off the '.csv'
		self.print_verbose( self.truncated_dataset_file_name )

	def game_start(self):
		
		self.world = ep_world_create()
		ep_world_set_sleeping(self.world, True, 30, 0, 0.002, 0.0001)
		ep_world_set_settings(self.world, 1.0 / 4.0, 20, 10, 0.1, 0.5, 0, 0.5, 1)

		self.init_dataset()

		self.mouseParticleId = self.get_static_body_id()
		self.MOUSE_HINGE_JOINT = -1.0
		particlePosition_X = 10

		# HOW TO SET THE FRICTIONS...
		# ep_shape_set_material(global.world,body,shape1,0.5,0.4,0,0);
		# 0.5: coefficient of restitution.
		# 0.4: friction.
		# 0: normal surface velocity.
		# 0: tangential surface velocity.

		# physics boundaries of the stage, AKA the Control Volume Tank.
		# MAKE FLOOR
		tmpW = self.WINDOW_WIDTH - self.CONTAINER_WALLS_WIDTH
		tmpH = self.CONTAINER_WALLS_WIDTH
		tmpX = self.WINDOW_WIDTH / 2
		tmpY = self.WINDOW_HEIGHT - self.CONTAINER_WALLS_WIDTH

		# ep_shape_create_box(world_id, body_id, w, h, x, y, rot, density)
		tmpBodyId = self.get_static_body_id()
		self.edge_boxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.COEFFICIENT_RESTITUTION, self.FRICTION, 0, 0)

		# LEFT WALL
		tmpW = self.CONTAINER_WALLS_WIDTH
		tmpH = self.WINDOW_HEIGHT - self.CONTAINER_WALLS_WIDTH
		tmpX = 0
		tmpY = self.WINDOW_HEIGHT / 2

		tmpBodyId = self.get_static_body_id()
		self.edge_boxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.COEFFICIENT_RESTITUTION, self.FRICTION, 0, 0)

		# RIGHT WALL
		tmpW = self.CONTAINER_WALLS_WIDTH
		tmpH = self.WINDOW_HEIGHT - self.CONTAINER_WALLS_WIDTH
		tmpX = self.WINDOW_WIDTH - self.CONTAINER_WALLS_WIDTH
		tmpY = self.WINDOW_HEIGHT / 2

		tmpBodyId = self.get_static_body_id()
		self.edge_boxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.COEFFICIENT_RESTITUTION, self.FRICTION, 0, 0)

		# MAKE CEILING
		tmpW = self.WINDOW_WIDTH - self.CONTAINER_WALLS_WIDTH
		tmpH = self.CONTAINER_WALLS_WIDTH
		tmpX = self.WINDOW_WIDTH / 2
		tmpY = self.CONTAINER_WALLS_WIDTH

		tmpBodyId = self.get_static_body_id()
		self.edge_boxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.COEFFICIENT_RESTITUTION, self.FRICTION, 0, 0)

		# GENERATE PARTICLES
		particleCount = 0
		for i in range(0, self.particles_birth_count):

			# HEAVY PARTICLES
			tmpId = self.get_dynamic_body_id()
			shape = self.get_particle_shape(tmpId)
			ep_shape_set_collision(self.world, tmpId, shape, 1, 1, 0)
			ep_shape_set_material(self.world, tmpId, shape, self.COEFFICIENT_RESTITUTION, self.FRICTION, 0, 0)
			ep_body_calculate_mass(self.world, tmpId)

			if particlePosition_X >= self.WINDOW_WIDTH:
				particlePosition_X = 0
			else:
				particlePosition_X += 1
			tmpRadian = random.randrange(0,57)
			ep_body_set_position(self.world, tmpId, particlePosition_X, 10, math.radians(tmpRadian))
			ep_body_set_gravity(self.world, tmpId, 0, 1.0)
			self.heavy_particles.append(tmpId)
			particleCount += 1

			# LIGHTWEIGHT PARTICLES
			tmpId = self.get_dynamic_body_id()
			shape = self.get_particle_shape(tmpId) 
			ep_shape_set_collision(self.world, tmpId, shape, 1, 1, 0)
			ep_shape_set_material(self.world, tmpId, shape, self.COEFFICIENT_RESTITUTION, self.FRICTION, 0, 0)
			ep_body_calculate_mass(self.world, tmpId)
			tmpRadian = random.randrange(0,57)
			ep_body_set_position(self.world, tmpId, particlePosition_X, self.WINDOW_HEIGHT-10, math.radians(tmpRadian))
			ep_body_set_gravity(self.world, tmpId, 0, -1.0)
			self.light_particles.append(tmpId)
			particleCount += 1

	def get_particle_shape(self, tmpId):
		# ep_shape_create_circle method API...
		# shape1 = ep_shape_create_circle(global.world,body,32,0,0,0,1);
		# 32: the radius of the circle.
		# 0,0,0: the relative coordinates of the shape (x,y,rot).
		# 1: the density of the circle (not used for static bodies).

		if self.PARTICLE_SHAPE_MODE == "CIRCLE":
			return ep_shape_create_circle(self.world, tmpId, self.PARTICLE_DIAMETER,0,0,0,1);
		else: #default square
			return ep_shape_create_box(self.world, tmpId, self.PARTICLE_DIAMETER, self.PARTICLE_DIAMETER, 0, 0, 0, 1)

	def paint_candle(self, pRow):
		if self.new_x >= self.PAINTABLE_LIMIT: # no matter the record count, limit candles to window width
			return 0

		if pRow == []:
			return 0

		timestamp = pRow[0][0]

		# self.print_debug(timestamp)
		# self.print_debug(self.dataset[pIndex])
		# for dukascopy the rows are 1 thru 4
		# for metatrader it's 2 through 5
		priceOpen = self.interpolate(float(pRow.split(",")[2]))
		priceHigh = self.interpolate(float(pRow.split(",")[3]))
		priceLow = self.interpolate(float(pRow.split(",")[4]))
		priceClose = self.interpolate(float(pRow.split(",")[5]))
		volume = self.interpolate(float(pRow[6]))

		if self.DATASET_HIGHEST == priceHigh:
			self.DATASET_HIGHEST_INDEX = self.candleIndex

		if self.DATASET_LOWEST == priceLow:
			self.DATASET_LOWEST_INDEX = self.candleIndex

		# experimental, use to filter out zero volume periods
		# if volume == 0:
		# 	return 0

		candleHeight = 0
		
		# DETERMINE CANDLE PRICE HEIGHT
		candleHeight = priceHigh - priceLow
		newY = ((candleHeight/2)) + priceLow
		candleHeight = abs(candleHeight)

		tmpBodyId = self.get_static_body_id()
		self.edge_boxes.append([self.CANDLESTICK_WIDTH, candleHeight, self.new_x, newY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, self.CANDLESTICK_WIDTH, candleHeight, self.new_x, newY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		tmpCoef = 2
		tmpFric = 1
		ep_shape_set_material(self.world, tmpBodyId, shape, tmpCoef, tmpFric, 0, 0)

		# PRICE STANDARD DEVIATION
		sdSet = self.get_last_n_prices(self.candleIndex)
		standardDev = sdef.getStandardDeviation(sdSet).real
		standardDev *= (math.pow(  math.pi*self.get_phi(), 4) )
		
		self.standard_dev_list.append([[self.previous_sdev_x, self.previous_sdev_y], [self.new_x, self.standard_dev_start_y-standardDev]])
		self.previous_sdev_x = self.new_x
		self.previous_sdev_y = self.standard_dev_start_y-standardDev			

		# VOLUME SD
		sdSetVol = self.get_last_n_volumes(self.candleIndex)
		standardDevVol = sdef.getStandardDeviation(sdSetVol).real
		standardDevVol *= (math.pow(  math.pi*self.get_phi(), 2.5) )

		self.standard_dev_list_vol.append([[self.previous_sdev_vol_x, self.previous_sdev_vol_y], [self.new_x, self.standard_dev_vol_start_y-standardDevVol]])
		self.previous_sdev_vol_x = self.new_x
		self.previous_sdev_vol_y = self.standard_dev_vol_start_y-standardDevVol

		# advance the x
		self.new_x += (self.CANDLESTICK_WIDTH + self.CANDLE_GUTTER)

		return 1

	def get_x_location_of_candle(self, pIndex):
		tmpAdd = self.new_x_default_value
		for i in range(0, pIndex):
			tmpAdd += (self.CANDLESTICK_WIDTH + self.CANDLE_GUTTER)
		return tmpAdd

	def get_last_n_prices(self, pIndex):
		tmpList = []
		returnList = []
		dsSubset = []
		lookback = self.sigma_period

		dsSubset.append( self.dataset[pIndex] )
		try:
			for i in range(1, lookback):
				dsSubset.append( self.dataset[pIndex-i] )
			
		except Exception as e:
			pass

		for i in range(0, len(dsSubset)):
			# priceOpen = float(dsSubset[i].split(",")[2])
			# priceHigh = float(dsSubset[i].split(",")[3])
			# priceLow = float(dsSubset[i].split(",")[4])
			priceClose = float(dsSubset[i].split(",")[5])
			# tmpList.append(priceOpen)
			# tmpList.append(priceHigh)
			# tmpList.append(priceLow)
			tmpList.append(priceClose) # note: just using the close makes for a bit spikier, low notches are more defined

		return tmpList

	def get_last_n_volumes(self, pIndex):
		tmpList = []
		returnList = []
		dsSubset = []
		lookback = self.sigma_period

		dsSubset.append( self.dataset[pIndex] )
		try:
			for i in range(1, lookback):
				dsSubset.append( self.dataset[pIndex-i] )
			
		except Exception as e:
			pass

		for i in range(0, len(dsSubset)):
			# priceOpen = float(dsSubset[i].split(",")[2])
			# priceHigh = float(dsSubset[i].split(",")[3])
			# priceLow = float(dsSubset[i].split(",")[4])
			# priceClose = float(dsSubset[i].split(",")[5])
			volume = int(dsSubset[i].split(",")[6])
			# tmpList.append(priceOpen)
			# tmpList.append(priceHigh)
			# tmpList.append(priceLow)
			# tmpList.append(priceClose)
			tmpList.append(volume)

		return tmpList

	def get_static_body_id(self):
		return ep_body_create_static(self.world)

	def get_dynamic_body_id(self):
		return ep_body_create_dynamic(self.world, False)

	def interpolate(self, pVal):
		newVal = interp(pVal, [self.DATASET_LOWEST, self.DATASET_HIGHEST ], [self.WINDOW_HEIGHT*self.HEIGHT_SCALING_FACTOR, 0])
		return newVal

	def game_end(self):	
		ep_world_destroy(self.world)

	def game_run(self):
		self.game_start()

		while self.run == True:	
			for event in pygame.event.get():
				if event.type == "QUIT":
					pygame.quit()
					sys.exit()
				elif event.type == "MOUSEMOTION":
					self.mouse_x, self.mouse_y = event.pos
				elif event.type == "MOUSEBUTTONDOWN":
					self.mouse_x, self.mouse_y = event.pos
					if ep_world_collision_test_circle(self.world, 0, self.mouse_x, self.mouse_y, 0, 1, 1, 0) > 0:
						b = ep_world_get_collision_body(self.world, 0)
						s = ep_world_get_collision_shape(self.world, 0)
						if not ep_body_is_static(self.world, b):
							xx = ep_body_coord_world_to_local_x(self.world, b, self.mouse_x, self.mouse_y)
							yy = ep_body_coord_world_to_local_y(self.world, b, self.mouse_x, self.mouse_y)
							mousehingejoint = ep_hingejoint_create(self.world, b, self.mouseParticleId, xx, yy, 0, 0, 0)
							ep_hingejoint_set_max_force(self.world, mousehingejoint, 10000)
				elif event.type == "MOUSEBUTTONUP":
					self.mouse_x, self.mouse_y = event.pos
					if self.MOUSE_HINGE_JOINT != -1.0:
						ep_hingejoint_destroy(self.world, self.MOUSE_HINGE_JOINT)
						self.MOUSE_HINGE_JOINT = -1.0
				elif event.type == "KEYDOWN":
					if event.key == "K_ESCAPE":
						pygame.event.post(pygame.event.Event(QUIT))
					elif event.key == "K_r":
						self.game_end()
						self.game_start()
			
			vx = self.mouse_x - ep_body_get_x_center(self.world, self.mouseParticleId)
			vy = self.mouse_y - ep_body_get_y_center(self.world, self.mouseParticleId)
			if self.MOUSE_HINGE_JOINT != -1.0:
				d = math.sqrt(vx * vx + vy * vy)
				if d > 10:
					vx *= 10 / d
					vy *= 10 / d
			ep_body_set_velocity_center(self.world, self.mouseParticleId, vx, vy, 0)
			
			for i in range(4):
				ep_world_update_contacts(self.world)
				ep_world_simulate_step(self.world)
			
			self.surf_window.lock()
			self.surf_window.fill(pygame.Color(0, 0, 0))
			
			for b in self.edge_boxes:
				self.draw_box(b[2], b[3], b[0], b[1], b[4], self.color_static)
			
			for b in self.heavy_particles:
				self.draw_box(ep_body_get_x(self.world, b), \
					ep_body_get_y(self.world, b), self.PARTICLE_DIAMETER, self.PARTICLE_DIAMETER, ep_body_get_rot(self.world, b), \
					self.COLOR_HEAVY_PARTICLES)
			
			for b in self.light_particles:

				self.draw_box(ep_body_get_x(self.world, b), \
					ep_body_get_y(self.world, b), self.PARTICLE_DIAMETER, self.PARTICLE_DIAMETER, ep_body_get_rot(self.world, b), \
					self.COLOR_LIGHT_PARTICLES)
			
			for b in self.candlestick_boxes:
				self.draw_box(b[2], b[3], b[0], b[1], b[4], self.color_static)
			
			
			for b in self.standard_dev_list:
				self.draw_standard_dev_line(b)

			for b in self.standard_dev_list_vol:
				self.draw_standard_dev_line_vol(b)

			pygame.display.set_caption(self.truncated_dataset_file_name + "    |||    " + str( self.offset_index  ) + " steps back " )

			self.surf_window.unlock()
			
			self.display_text_large(self.truncated_dataset_file_name, 10, 695, pygame.Color(255, 255, 255))
						
			# chart labels
			# text = "----" + str(self.DATASET_HIGHEST)
			# self.displayText(text, self.interpolate(self.DATASET_HIGHEST + 2), self.get_x_location_of_candle(self.DATASET_HIGHEST_INDEX),\
			# 	pygame.Color(255, 255, 0))

			pygame.display.update()
			self.fpsclock.tick(self.FRAME_RATE)

			self.index_counter += 1

			# make another frame for the animation
			if self.save_sequences == True:

				if not os.path.exists(self.render_frames_directory + self.truncated_dataset_file_name):
					os.makedirs(self.render_frames_directory + self.truncated_dataset_file_name)

				tmpDir = self.render_frames_directory + self.truncated_dataset_file_name + "/" + self.code_name + "_" + self.number_formatter( self.index_counter )

				pygame.image.save(self.surf_window, tmpDir  + ".png")

			# make the histogram
			if self.index_counter == self.FRAME_LIMIT:
				
				tmpFileName = self.render_histogram_directory + self.truncated_dataset_file_name + ".png"
					
				# make the histogram folder if it's absent
				if not os.path.exists(self.render_histogram_directory):
					os.makedirs(self.render_histogram_directory)

				self.print_verbose( "Preparing final frame output to " + tmpFileName ) 
				pygame.image.save(self.surf_window, tmpFileName)

				self.make_histogram( tmpFileName )

				# Delete the temp file
				os.system( "rm " + tmpFileName )

				self.make_video_from_sequence()

				self.run = False

		self.game_end()

	def make_video_from_sequence(self):
		tmpDir = self.render_frames_directory + self.truncated_dataset_file_name + "/"

		files = sorted( glob.glob( tmpDir + '*.png') )

		if len( files ) == 0:
			print("nothing to convert in " + tmpDir)
			return

		# arg = "ffmpeg -framerate 30 -pattern_type glob -i '" + tmpDir + "*.png' -c:v libx264 -pix_fmt yuv420p -crf 23 -y " + self.render_frames_directory + "/" + self.truncated_dataset_file_name + ".mp4"
		# os.system( arg )

		# make an AVI so we can convert into GIF
		arg = "ffmpeg -framerate 30 -pattern_type glob -i '" + tmpDir + "*.png' -c:v ffv1 -y " + self.render_frames_directory + "/temp.avi"
		os.system( arg )

		arg = "ffmpeg -i " + self.render_frames_directory + "/temp.avi -pix_fmt rgb8 -y " + self.render_frames_directory + "/" + \
		self.truncated_dataset_file_name + "_" + self.number_formatter(self.offset_index) + "_sig" + str( self.sigma_period ) + ".gif"
		os.system( arg )
		os.system( "rm " + self.render_frames_directory + "temp.avi" )

		# delete all PNGs from this location when done.
		shutil.rmtree(tmpDir)

	def number_formatter(self, pNum):
		return "%03d" % (pNum,)

	def displayText(self, pTxt, pPosLeft, pPosRight, pColor):
		surf_text = self.font.render(pTxt, False, pColor)
		rect = surf_text.get_rect()
		rect.topleft = (pPosLeft, pPosRight)
		self.surf_window.blit(surf_text, rect)	

	def display_text_large(self, pTxt, pPosLeft, pPosRight, pColor):
		surf_text = self.font_large.render(pTxt, False, pColor)
		rect = surf_text.get_rect()
		rect.topleft = (pPosLeft, pPosRight)
		self.surf_window.blit(surf_text, rect)	

	def special_number(self):
		return math.pi
		return ((1+5 ** 0.5) / 2) * pow(math.pi, 4) 

	def get_phi(self):
		return ((1+5 ** 0.5) / 2)

	def make_histogram(self, pImg):
		img = Image.open(pImg)
		img_bbox = img.getbbox()
		self.draw = ImageDraw.Draw(img)
		pixels = img.load()
		imbalanceRatioArray = []

		for xx in range( img.size[0] ):

			heavyParticleCounter = 0.0
			lightParticleCounter = 0.0
			tmpOffset = 12

			for yy in range(tmpOffset, img.size[1] - tmpOffset): # filter out particle detritus from the histogram data

				if pixels[ xx, yy ] == (0, 146, 255):
					heavyParticleCounter += 1.0
				elif pixels[ xx, yy ] == (255, 0, 255):
					lightParticleCounter += 1.0

			imbalanceRatio1 = (heavyParticleCounter+1.0)/(lightParticleCounter+1.0)
			imbalanceRatio2 = (lightParticleCounter+1.0)/(heavyParticleCounter+1.0)
			imbalanceRatioArray.append( [-imbalanceRatio1, imbalanceRatio2] )

		# Draw histogram at the top of the chart
		if self.show_histogram_ratio == True:
			for r in range(0, len(imbalanceRatioArray)):
				self.draw.line(( r-1, 100+imbalanceRatioArray[r-1][0]*self.special_number(), r, 100+imbalanceRatioArray[r][0]*self.special_number()), \
					fill=(self.COLOR_HISTOGRAM_UP), width=1 )
				self.draw.line(( r-1, 100+imbalanceRatioArray[r-1][1]*self.special_number(), r, 100+imbalanceRatioArray[r][1]*self.special_number()), \
					fill=(self.COLOR_HISTOGRAM_DOWN), width=1 )

		# ---------------------------------------------------------------------------		
		# Draw a simple average of the ratio - this section draws for the blue side

		# note: we are doing the averaging even if we don't show it, 
		# this is because we need the average to perform other work later on

		tmpAvg1 = []
		offsetY = 80
		for r in range(0, len(imbalanceRatioArray)): 
			tmpAvg = 0
			tmpthing = 0 
			for f in range(0, self.histogram_simple_average_period):
				tmpthing += imbalanceRatioArray[r-f][0]
			tmpAvg = tmpthing/self.histogram_simple_average_period
			tmpAvg1.append(tmpAvg)

		if self.show_histogram_simple_average == True:
			for r in range(0, len( tmpAvg1 ) ):
				self.draw.line(( r-1, offsetY+tmpAvg1[r-1]*self.special_number(), r, offsetY+tmpAvg1[r]*self.special_number()), fill=(self.COLOR_HISTOGRAM_UP), width=1 )
		
		# Draw a simple average of the ratio - this section draws for the pink side
		tmpAvg1 = []
		for r in range(0, len(imbalanceRatioArray)): 
			tmpAvg = 0
			tmpthing = 0 
			for f in range(0, self.histogram_simple_average_period):
				tmpthing += imbalanceRatioArray[r-f][1]
			tmpAvg = tmpthing/self.histogram_simple_average_period
			tmpAvg1.append(tmpAvg)

		if self.show_histogram_simple_average == True:
			for r in range(0, len( tmpAvg1 ) ):
				self.draw.line(( r-1, offsetY+tmpAvg1[r-1]*self.special_number(), r, offsetY+tmpAvg1[r]*self.special_number()), fill=(self.COLOR_HISTOGRAM_DOWN), width=1 )

		# ---------------------------------------------------------------------------

		if self.highlight_sigma == True:

			# DRAW VERTICAL LINE AT POINT OF LOWEST STANDARD DEV
			# find the low points in the standard dev
			# put all the Y values of the standard deviation in a separate list
			# an entry in the list looks like [[0, 900], [10, 639.1957450511611]]
			# we want to look a the second nested list, and only the Y component
			# the higher this number is, the lower it occurs on the chart, i.e. the lowest standard dev value
			tmpList = []
			for index in range(0, len(self.standard_dev_list)):
				tmpList.append( self.standard_dev_list[index][1][1] )

			# this works fine for the lowest, but only one result 
			# tmpX = self.standard_dev_list[tmpList.index( max(tmpList) )][1][0]
			# tmpY = max(tmpList) # returns what represents the lowest standard dev value
			# # print(tmpX, tmpY)
			# self.draw.line(( tmpX, 0, tmpX, tmpY ), fill=(self.COLOR_ENTRY_SIGNAL), width=1 )

			# ----- TEST AREA -----------------------------------------------------------------------	
			# TODO: determine if we can be smarter about how many lines to show per sigma low

			largest = heapq.nlargest(self.sigma_sort_low, enumerate(tmpList), key=lambda x: x[1])

			for item in largest:
				# self.print_debug( item )

				tmpX = self.standard_dev_list[item[0]][1][0]
				tmpY = item[1]

				buyers = abs( imbalanceRatioArray[ self.get_x_location_of_candle( item[0] ) ][0] )
				sellers = abs( imbalanceRatioArray[ self.get_x_location_of_candle( item[0] ) ][1] )
				tmpYIndicatorStart = self.standard_dev_list_vol[  item[0]  ][0][1]
				if ( buyers > sellers):
					self.draw.line(( tmpX, tmpYIndicatorStart, tmpX, tmpY ), fill=(self.COLOR_ENTRY_SIGNAL), width=1 )
				elif ( sellers > buyers):
					self.draw.line(( tmpX, tmpYIndicatorStart, tmpX, tmpY ), fill=( (255,0,0) ), width=1 )	

				# orig
				# self.draw.line(( tmpX, 150, tmpX, tmpY ), fill=(self.COLOR_ENTRY_SIGNAL), width=1 )


				# test area
				# new idea: 
				# while we are looping the low sigmas, 
				# get the histogram average based on which index we're on
				# self.print_debug( imbalanceRatioArray[ self.get_x_location_of_candle( item[0] ) ][0]  )

				# compare this with what the volume is doing

				# self.print_debug(  self.standard_dev_list_vol[  item[0]  ] ) 

			# ----------------------------------------------------------------------------------------
		# print("-------------------")
		# print(len(imbalanceRatioArray))		
		# print(len(self.standard_dev_list))

		if self.show_histogram_standard_dev == True:
			# Draw a standard deviation line based on the particle counts
			# histogram up - blue
			sdevParticles = []
			sigmaLookbackParticleCount = self.histogram_standard_dev_period
			sdevParticlesAdjust = 2
			offsetY = 125
			for r in range(0, len(imbalanceRatioArray)): 
				topParticlesSet = []
				for f in range(0, sigmaLookbackParticleCount):
					topParticlesSet.append( imbalanceRatioArray[r-f][0] )			
				standardDev = sdef.getStandardDeviation(topParticlesSet).real
				standardDev *= (math.pow(  math.pi*self.get_phi(), sdevParticlesAdjust) )
				standardDev *= -1  # negative adjustment to flip the projection
				sdevParticles.append( standardDev )		
			for r in range(0, len( sdevParticles ) ):
				self.draw.line(( r-1, offsetY+sdevParticles[r-1]*self.special_number(), r, offsetY+sdevParticles[r]*self.special_number()), fill=(self.COLOR_HISTOGRAM_UP), width=1 )

			# histogram down - pink
			sdevParticles = []
			for r in range(0, len(imbalanceRatioArray)): 
				bottomParticlesSet = []
				for f in range(0, sigmaLookbackParticleCount):
					bottomParticlesSet.append( imbalanceRatioArray[r-f][1] )			
				standardDev = sdef.getStandardDeviation(bottomParticlesSet).real
				standardDev *= (math.pow(  math.pi*self.get_phi(), sdevParticlesAdjust) )
				standardDev *= -1  # negative adjustment to flip the projection
				sdevParticles.append( standardDev )
			for r in range(0, len( sdevParticles ) ):
				self.draw.line(( r-1, offsetY+sdevParticles[r-1]*self.special_number(), r, offsetY+sdevParticles[r]*self.special_number()), fill=(self.COLOR_HISTOGRAM_DOWN), width=1 )


		# Build the histogram directory if it's not there
		gif_animation_directory = self.render_histogram_directory + self.histogram_animation_directory + \
								  self.truncated_dataset_file_name + "_" + self.number_formatter(self.offset_index) + "_sig" + str( self.sigma_period )
		if not os.path.exists( gif_animation_directory ):
			os.makedirs( gif_animation_directory )

		# TODO: consider putting local timestamp on histogram
		local_current_time = "" # TBD

		# Save the histogram
		img.save(gif_animation_directory + "/" + \
				 self.truncated_dataset_file_name + "_" + \
				 # local_current_time + "_" + \
				 self.number_formatter(self.offset_index) + "_" + \
				 self.number_formatter(self.permutation_index) + \
				 "_sig" + str( self.sigma_period ) + \
				 ".png", format='PNG')

		# make a gif from available images
		arg = "ffmpeg -pattern_type glob -i '" + gif_animation_directory + "/*.png' -y " + gif_animation_directory + "/temp.avi"
		os.system( arg )
		arg = "ffmpeg -i " + gif_animation_directory + "/temp.avi -pix_fmt rgb8 -y " + gif_animation_directory + "/" + \
				self.truncated_dataset_file_name + "_" + self.number_formatter(self.offset_index) + "_sig" + str( self.sigma_period ) + ".gif"
		os.system( arg )
		os.system( "rm " + gif_animation_directory + "/temp.avi" )

		self.print_verbose(self.dataset_file + " simulation done.")

		# Automatically display the image
		# img.show()

	def set_permutation_name(self, pIterationNumber):
		self.permutation_name = \
		str(pIterationNumber) + "_" + \
		str(self.dataset_file) + "_" + \
		str(self.particles_birth_count) + "_" + \
		str(self.CANDLESTICK_WIDTH) + "_" + \
		str(self.PARTICLE_DIAMETER) + "_" + \
		str(self.CANDLE_GUTTER)

	def set_particles_birth_count(self, pParticleBirthCount):
		self.particles_birth_count = pParticleBirthCount

	def	set_candlestick_width(self, pCandlestickWidth):
		self.CANDLESTICK_WIDTH = pCandlestickWidth

	def set_particles_diameter(self, pParticleDiameter):
		self.PARTICLE_DIAMETER = pParticleDiameter

	def set_candle_gutter(self, pCandleGutter):
		self.CANDLE_GUTTER = pCandleGutter

	def print_verbose(self, pMessage):
		if (self.verbose == True):
			print(pMessage)

	def print_debug(self, pMessage):
		if (self.debug == True):
			print(pMessage)			
		
#--- RUNTIME NOTES  --------------------------------------------------------------------
# This particular flavor uses CSV files containing OHLC data. These files can be static or
# dynamically updated, provided they adhere to the structure as included in sample CSV.
# Place or write all CSV files in the directory specified in app.yaml.
app_yaml = open("../config/app.yaml", "r").readlines()
path_to_csv_files = app_yaml[0].split(":")[1] # TODO: make this a little smarter
arbitraryRunLimit = 99 # The number of times to run the simulation

for r in range(0, arbitraryRunLimit): 

	dataset_list = []
	if r == 0: # only strip this the first time
		path_to_csv_files = path_to_csv_files.strip() + "/*.csv"
	files = glob.glob(path_to_csv_files) # Get all the CSV files
	files.sort(key=os.path.getmtime) # Sort the files based on latest
	
	for csvfile in reversed(files):
		dataset_list.append(csvfile) # Add the files to a list
	print("-----------------",dataset_list[:1])


	for dataset in dataset_list[:1]: # Loop up to [:N] datasets e.g. [:3]		
		lookback = 0 # Default is 1. To loop iterations within a dataset use following loop with lookback. e.g., setting this to 60 will use one dataset to create 60 simulations, each one starting a candle earlier. Useful for looking for patterns on old data. Set lookback to 1 when running in a production/trading mode, assuming your CSV file is being updated in real time.	
		i = 0
		while i <= lookback:
			print("-------------------------------------------------")

			cvt = ControlVolumeTank() # The ControlVolumeTank is the class running the simulation.
			lookback = int(cvt.sample_period_size) # override if this was passed in
			cvt.permutation_index = r

			if lookback > 0:
				cvt.offset_index = i  # Sets an index based on where we are at in the lookback sequence. If lookback is 1 then we aren't running multiple simulations off the same dataset, but fresh ones every time.
			if cvt.offset_index_override != 0:
				cvt.offset_index = cvt.offset_index_override - i
				print("Beginning at candle " + str( cvt.offset_index ))
			cvt.dataset_file = dataset
			print( "Current OHLC dataset: " + TextColors.HEADERLEFT2 + TextColors.INVERTED + dataset + TextColors.ENDC)
			random.seed()
			cvt.set_particles_diameter( 2 )
			cvt.set_candlestick_width( 3 )
			cvt.set_particles_birth_count( particle_birth_count )
			cvt.set_candle_gutter( 1 )
			cvt.game_run()
			i += 1
