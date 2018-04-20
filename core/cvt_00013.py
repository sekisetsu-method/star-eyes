#!/usr/bin/env python
# -*- coding: utf8 -*-
print(unicode("積雪メソッド","UTF-8"))

__author__ = "Arlo Emerson <arlo.emerson@sekisetsumethod.com>"
__status__  = "production"
__version__ = "13.0"
__date__    = "14 April 2018"

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
Sekisetsu is a Japanese word for snowfall accumulation. The Sekisetsu Method (積雪メソッド) combines price action geometry (candlesticks) with fluid dynamics to reveal otherwise hidden structure and market participant intention in price charts. The method can also be termed "Price Action Fluid Dynamics". Many terms and ideas from fluid dynamics and chaotic systems are borrowed and used both in the code and as allegory in the training material. Regardless of terminology, the goal of the method is to empower the user to align trades with larger players. 

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
# Project website: http://www.sekisetsumethod.com

# See the README file for detailed information on usage.
# See http://www.sekisetsumethod.com for charts, signals and training.

# Thanks to Maarten Baert's excellent physics engine (licensed under LGPL).
# More info: http://www.maartenbaert.be/extremephysics/
#------------------------------------------------------------------------------

import os as os
os.environ['SDL_VIDEODRIVER']='dummy' # use this if running bash ubuntu on windows
import pygame, sys, math, random, csv, glob, subprocess, shutil
from pygame.locals import *
from lib.extremephysics import *
from numpy import interp
import lib.standard_deviation_function as sdef
from PIL import Image, ImageDraw

_targetDir = "../csv/"
_fileType = '.csv'
_particleBirthCount = 1280 # should match window width

# Particle/fluid simulations occur within a Control Volume Tank. 
# The current settings in this version are tuned to USDJPY 15 and 30 minute chart data.
# Make a copy of this class and try other settings and data sources.
class ControlVolumeTank():

	def __init__(self):
		print(self.__class__.__name__, __version__)

		self.datasetFile = '' # overridden
		self.saveSequences = True
		self.particlesBirthCount = 0 # overridden
		self.frameLimit = 200 # 200 for production
		self.renderFramesDirectory = "../simulations/"
		self.renderHistogramDirectory = "../histograms/"
		self.codeName = "star_eyes"
		self.permutationName = __version__
		self.histogramAnimationDir = self.codeName + "_" + __version__ + "/" 
		self.particleShapeMode = "CIRCLE"
		self.particleDiameter = .1
		self.coefficientRestitution = 0.1 #0.01
		self.friction = 0.1
		self.datasetHighestIndex = 0
		self.datasetLowestIndex = 0
		self.draw = ImageDraw.Draw
		self.newDevX = 0
		self.previousSDefX = 0
		self.previousSDefY = 900
		self.standardDefStartY = 900 # these should match
		self.frameRate = 24 
		self.candlestickWidth = 1
		self.newXDefaultVal = 10
		self.containerWallsWidth = 2
		self.candleGutter = 3
		self.run = True
		self.datasetLowest = 107 # overridden, used for scaling the chart into this game window
		self.datasetHighest = 111  # overridden
		self.offsetIndex = 0 # global used for cycling through the T axis
		self.truncatedDatasetFileName = ""
		self.paintableLimit = 1268 # used as a canvas limit so there are some venting gaps on L and R side of chart
		self.heightScalingFactor = 1.1 # set to 1.2 initially. if things are getting truncated, lower this number to fit more into the screen
		# note: set to negative number to do interesting head-on particle collisions.

		random.seed()
		pygame.display.init()
		pygame.font.init()
		self.fpsclock = pygame.time.Clock()
		self.WINDOW_WIDTH = 1280
		self.WINDOW_HEIGHT = 720
		self.surf_window = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
		self.font = pygame.font.SysFont("Sans", 12)	
		self.fontLarge = pygame.font.SysFont("Sans", 16)	
		self.cx = self.WINDOW_WIDTH / 2
		self.cy = self.WINDOW_HEIGHT / 2
		self.mouse_x = 0
		self.mouse_y = 0
		self.color_static = pygame.Color(52, 30, 162)
		self.colorStandardDeviation = pygame.Color("yellow")
		self.colorHeavyParticles = pygame.Color(0, 146, 255)
		self.colorLightParticles = pygame.Color(255, 0, 255)
		self.colorHistogramUp = (0, 146, 255)
		self.colorHistogramDown = (255, 0, 255)
		self.colorEntrySignal = (0, 255, 100)
		self.mousehingejoint = -1.0
		self.edgeBoxes = []
		self.candlestickBoxes = []
		self.heavyParticles = []
		self.lightParticles = []
		self.standardDefList = []
		self.newX = self.newXDefaultVal
		self.index_counter = 0
		
	def setDatasetFile(self, pFileName):
		self.datasetFile = pFileName

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
	def drawGrowingRectangle(self, pInt):
		points = (20,20,50+pInt, 30)
		# make this grow automatically
		pygame.draw.rect(self.surf_window, self.colorStandardDeviation, points, 1)

	def drawStandardDevLine(self, pCoords):
		pygame.draw.line(self.surf_window, self.colorStandardDeviation, pCoords[0], pCoords[1], 1)

	def initDataset(self):	
		csvfile = open(self.datasetFile, 'r')
		lines = csvfile.readlines() 
		
		# print(lines)
		rowCount = 0
		for row in lines:
			rowCount += 1
		
		tmpDataSet = []

		# this reverse orders the orig data so we can paint from left to right with it
		startIndex = rowCount - self.offsetIndex - 315
		for i in range( startIndex, rowCount - self.offsetIndex ):
			tmpDataSet.append(lines[i])
		
		self.dataset = tmpDataSet

		tmpList = []
		tmpCount = 0

		for row in self.dataset:
			# if tmpCount > 0:			
			# this is to determine the min/max
			#tmpTruncatedRow = row[1:4] # works for dukascopy
			rowList = row.split(",")
			# print(rowList)
			tmpTruncatedRow = rowList[2:6] # works for metatrader
			# print(tmpTruncatedRow)

			if tmpTruncatedRow != []:
				tmpList.append(  max(tmpTruncatedRow)  )
				tmpList.append(  min(tmpTruncatedRow)  )

			# if tmpCount == 0:
			# 	tmpCount = 1

		self.datasetLowest = int( round( float( min(tmpList))  ) ) -1
		self.datasetHighest = int( round( float( max(tmpList))  ) ) +1

		firstRowRead = 0
		rowCount = 0
		tmpIndex = 0
		for row in self.dataset:
			self.candleIndex = tmpIndex

			#TODO - no need to pass in tmpindex if paintCandle is global
			self.paintCandle(row, tmpIndex) # returns 0 if row volume is empty
			tmpIndex += 1

		# print( str(rowCount) + " records in data set" )

		slashLocation = self.datasetFile.rfind('/') 
		directory = self.datasetFile[slashLocation+1:]
		self.truncatedDatasetFileName = directory[:-4] #trim off the '.csv'
		# print( self.truncatedDatasetFileName )

	def game_start(self):
		
		self.world = ep_world_create()
		ep_world_set_sleeping(self.world, True, 30, 0, 0.002, 0.0001)
		ep_world_set_settings(self.world, 1.0 / 4.0, 20, 10, 0.1, 0.5, 0, 0.5, 1)

		self.initDataset()

		self.mouseParticleId = self.getStaticBodyId()
		self.mousehingejoint = -1.0
		particlePosition_X = 10

		# HOW TO SET THE FRICTIONS...
		# ep_shape_set_material(global.world,body,shape1,0.5,0.4,0,0);
		# 0.5: coefficient of restitution.
		# 0.4: friction.
		# 0: normal surface velocity.
		# 0: tangential surface velocity.

		# physics boundaries of the stage, AKA the Control Volume Tank.
		# MAKE FLOOR
		tmpW = self.WINDOW_WIDTH - self.containerWallsWidth
		tmpH = self.containerWallsWidth
		tmpX = self.WINDOW_WIDTH / 2
		tmpY = self.WINDOW_HEIGHT - self.containerWallsWidth

		# ep_shape_create_box(world_id, body_id, w, h, x, y, rot, density)
		tmpBodyId = self.getStaticBodyId()
		self.edgeBoxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.coefficientRestitution, self.friction, 0, 0)

		# LEFT WALL
		tmpW = self.containerWallsWidth
		tmpH = self.WINDOW_HEIGHT - self.containerWallsWidth
		tmpX = 0
		tmpY = self.WINDOW_HEIGHT / 2

		tmpBodyId = self.getStaticBodyId()
		self.edgeBoxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.coefficientRestitution, self.friction, 0, 0)

		# RIGHT WALL
		tmpW = self.containerWallsWidth
		tmpH = self.WINDOW_HEIGHT - self.containerWallsWidth
		tmpX = self.WINDOW_WIDTH - self.containerWallsWidth
		tmpY = self.WINDOW_HEIGHT / 2

		tmpBodyId = self.getStaticBodyId()
		self.edgeBoxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.coefficientRestitution, self.friction, 0, 0)

		# MAKE CEILING
		tmpW = self.WINDOW_WIDTH - self.containerWallsWidth
		tmpH = self.containerWallsWidth
		tmpX = self.WINDOW_WIDTH / 2
		tmpY = self.containerWallsWidth

		tmpBodyId = self.getStaticBodyId()
		self.edgeBoxes.append([tmpW, tmpH, tmpX, tmpY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, tmpW, tmpH, tmpX, tmpY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		ep_shape_set_material(self.world, tmpBodyId, shape, self.coefficientRestitution, self.friction, 0, 0)

		# GENERATE PARTICLES
		particleCount = 0
		for i in range(0, self.particlesBirthCount):

			# HEAVY PARTICLES
			tmpId = self.getDynamicBodyId()
			shape = self.getParticleShape(tmpId)
			ep_shape_set_collision(self.world, tmpId, shape, 1, 1, 0)
			ep_shape_set_material(self.world, tmpId, shape, self.coefficientRestitution, self.friction, 0, 0)
			ep_body_calculate_mass(self.world, tmpId)

			if particlePosition_X >= self.WINDOW_WIDTH:
				particlePosition_X = 0
			else:
				particlePosition_X += 1
			ep_body_set_position(self.world, tmpId, particlePosition_X, 10, math.radians(0))
			ep_body_set_gravity(self.world, tmpId, 0, 1.0)
			self.heavyParticles.append(tmpId)
			particleCount += 1

			# LIGHTWEIGHT PARTICLES
			tmpId = self.getDynamicBodyId()
			shape = self.getParticleShape(tmpId) 
			ep_shape_set_collision(self.world, tmpId, shape, 1, 1, 0)
			ep_shape_set_material(self.world, tmpId, shape, self.coefficientRestitution, self.friction, 0, 0)
			ep_body_calculate_mass(self.world, tmpId)

			ep_body_set_position(self.world, tmpId, particlePosition_X, self.WINDOW_HEIGHT-10, math.radians(0))
			ep_body_set_gravity(self.world, tmpId, 0, -1.0)
			self.lightParticles.append(tmpId)
			particleCount += 1

	def getParticleShape(self, tmpId):
		# ep_shape_create_circle method API...
		# shape1 = ep_shape_create_circle(global.world,body,32,0,0,0,1);
		# 32: the radius of the circle.
		# 0,0,0: the relative coordinates of the shape (x,y,rot).
		# 1: the density of the circle (not used for static bodies).

		if self.particleShapeMode == "CIRCLE":
			return ep_shape_create_circle(self.world, tmpId, self.particleDiameter,0,0,0,1);
		else: #default square
			return ep_shape_create_box(self.world, tmpId, self.particleDiameter, self.particleDiameter, 0, 0, 0, 1)

	def paintCandle(self, pRow, pIndex):
		if self.newX >= self.paintableLimit: # no matter the record count, limit candles to window width
			return 0

		if pRow == []:
			return 0

		timestamp = pRow[0]

		# print(timestamp)
		# print(self.dataset[pIndex])
		# for dukascopy the rows are 1 thru 4
		# for metatrader it's 2 through 5
		priceOpen = self.interpolate(float(pRow.split(",")[2]))
		priceHigh = self.interpolate(float(pRow.split(",")[3]))
		priceLow = self.interpolate(float(pRow.split(",")[4]))
		priceClose = self.interpolate(float(pRow.split(",")[5]))
		# volume = float(pRow[6])

		if self.datasetHighest == priceHigh:
			self.datasetHighestIndex = self.candleIndex

		if self.datasetLowest == priceLow:
			self.datasetLowestIndex = self.candleIndex

		# experimental, use to filter out zero volume periods
		# if volume == 0:
		# 	return 0

		candleHeight = 0
		
		# DETERMINE CANDLE PRICE HEIGHT
		candleHeight = priceHigh - priceLow
		newY = ((candleHeight/2)) + priceLow
		candleHeight = abs(candleHeight)

		tmpBodyId = self.getStaticBodyId()
		self.edgeBoxes.append([self.candlestickWidth, candleHeight, self.newX, newY, math.radians(0)])
		shape = ep_shape_create_box(self.world, tmpBodyId, self.candlestickWidth, candleHeight, self.newX, newY, math.radians(0), 1)
		ep_shape_set_collision(self.world, tmpBodyId, shape, 1, 1, 0)
		tmpCoef = 2
		tmpFric = 1
		ep_shape_set_material(self.world, tmpBodyId, shape, tmpCoef, tmpFric, 0, 0)

		# STANDARD DEVIATION
		sdSet = self.getLastNPrices(pIndex)
		standardDef = sdef.getStandardDeviation(sdSet).real
		standardDef *= (math.pow(  math.pi*self.getPhi()  , 4) )
		
		self.standardDefList.append([[self.previousSDefX, self.previousSDefY], [self.newX, self.standardDefStartY-standardDef]])
		self.previousSDefX = self.newX
		self.previousSDefY = self.standardDefStartY-standardDef			

		self.newX += (self.candlestickWidth + self.candleGutter)

		return 1

	def getXLocationOfCandle(self, pIndex):
		tmpAdd = self.newXDefaultVal
		for i in range(0, pIndex):
			tmpAdd += (self.candlestickWidth + self.candleGutter)
		return tmpAdd

	def getLastNPrices(self, pIndex):
		tmpList = []
		returnList = []
		dsSubset = []
		lookback = 17

		dsSubset.append( self.dataset[pIndex] )
		try:
			for i in range(1, lookback):
				dsSubset.append( self.dataset[pIndex-i] )
			
		except Exception as e:
			pass

		for i in range(0, len(dsSubset)):
			priceOpen = float(dsSubset[i].split(",")[2])
			priceHigh = float(dsSubset[i].split(",")[3])
			priceLow = float(dsSubset[i].split(",")[4])
			priceClose = float(dsSubset[i].split(",")[5])
			tmpList.append(priceOpen)
			tmpList.append(priceHigh)
			tmpList.append(priceLow)
			tmpList.append(priceClose)

		return tmpList

	def getStaticBodyId(self):
		return ep_body_create_static(self.world)

	def getDynamicBodyId(self):
		return ep_body_create_dynamic(self.world, False)

	def interpolate(self, pVal):
		newVal = interp(pVal, [self.datasetLowest, self.datasetHighest ], [self.WINDOW_HEIGHT*self.heightScalingFactor, 0])
		return newVal

	def game_end(self):	
		ep_world_destroy(self.world)

	def game_run(self):
		self.game_start()

		while self.run == True:	
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEMOTION:
					self.mouse_x, self.mouse_y = event.pos
				elif event.type == MOUSEBUTTONDOWN:
					self.mouse_x, self.mouse_y = event.pos
					if ep_world_collision_test_circle(self.world, 0, self.mouse_x, self.mouse_y, 0, 1, 1, 0) > 0:
						b = ep_world_get_collision_body(self.world, 0)
						s = ep_world_get_collision_shape(self.world, 0)
						if not ep_body_is_static(self.world, b):
							xx = ep_body_coord_world_to_local_x(self.world, b, self.mouse_x, self.mouse_y)
							yy = ep_body_coord_world_to_local_y(self.world, b, self.mouse_x, self.mouse_y)
							mousehingejoint = ep_hingejoint_create(self.world, b, self.mouseParticleId, xx, yy, 0, 0, 0)
							ep_hingejoint_set_max_force(self.world, mousehingejoint, 10000)
				elif event.type == MOUSEBUTTONUP:
					self.mouse_x, self.mouse_y = event.pos
					if self.mousehingejoint != -1.0:
						ep_hingejoint_destroy(self.world, self.mousehingejoint)
						self.mousehingejoint = -1.0
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						pygame.event.post(pygame.event.Event(QUIT))
					elif event.key == K_r:
						self.game_end()
						self.game_start()
			
			vx = self.mouse_x - ep_body_get_x_center(self.world, self.mouseParticleId)
			vy = self.mouse_y - ep_body_get_y_center(self.world, self.mouseParticleId)
			if self.mousehingejoint != -1.0:
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
			
			for b in self.edgeBoxes:
				self.draw_box(b[2], b[3], b[0], b[1], b[4], self.color_static)
			
			for b in self.heavyParticles:
				self.draw_box(ep_body_get_x(self.world, b), \
					ep_body_get_y(self.world, b), self.particleDiameter, self.particleDiameter, ep_body_get_rot(self.world, b), \
					self.colorHeavyParticles)
			
			for b in self.lightParticles:

				self.draw_box(ep_body_get_x(self.world, b), \
					ep_body_get_y(self.world, b), self.particleDiameter, self.particleDiameter, ep_body_get_rot(self.world, b), \
					self.colorLightParticles)
			
			for b in self.candlestickBoxes:
				self.draw_box(b[2], b[3], b[0], b[1], b[4], self.color_static)
			
			
			for b in self.standardDefList:
				self.drawStandardDevLine(b)

			pygame.display.set_caption(self.truncatedDatasetFileName + "    |||    " + str( self.offsetIndex  ) + " steps back " )

			self.surf_window.unlock()
			
			self.displayTextLarge(self.truncatedDatasetFileName, 1000, 18, pygame.Color(255, 255, 255))
						
			# chart labels
			text = "----" + str(self.datasetHighest)
			self.displayText(text, self.interpolate(self.datasetHighest + 2), self.getXLocationOfCandle(self.datasetHighestIndex),\
				pygame.Color(255, 255, 0))

			pygame.display.update()
			self.fpsclock.tick(self.frameRate)

			self.index_counter += 1

			# make another frame for the animation
			if self.saveSequences == True:

				if not os.path.exists(self.renderFramesDirectory + self.truncatedDatasetFileName):
					os.makedirs(self.renderFramesDirectory + self.truncatedDatasetFileName)

				tmpDir = self.renderFramesDirectory + self.truncatedDatasetFileName + "/" + self.codeName + "_" + self.numberFormatter( self.index_counter )

				pygame.image.save(self.surf_window, tmpDir  + ".png")

			# make the histogram
			if self.index_counter == self.frameLimit:
				
				tmpFileName = self.renderHistogramDirectory + self.truncatedDatasetFileName + ".png"
				
				# make the histogram folder if it's absent
				if not os.path.exists(self.renderHistogramDirectory):
					os.makedirs(self.renderHistogramDirectory)

				# print( "preparing final frame output to " + tmpFileName ) 
				pygame.image.save(self.surf_window, tmpFileName)

				self.makeHistogram( tmpFileName )

				self.makeVideoFromSequences()

				self.run = False

		self.game_end()

	def makeVideoFromSequences(self):
		tmpDir = self.renderFramesDirectory + self.truncatedDatasetFileName + "/"

		files = sorted( glob.glob( tmpDir + '*.png') )

		if len( files ) == 0:
			print("nothing to convert in " + tmpDir)
			return

		# arg = "ffmpeg -framerate 30 -pattern_type glob -i '" + tmpDir + "*.png' -qscale:v 1 -y " + self.renderFramesDirectory + "/" + self.truncatedDatasetFileName + ".mpg"
		arg = "ffmpeg -framerate 30 -pattern_type glob -i '" + tmpDir + "*.png' -c:v libx264 -pix_fmt yuv420p -crf 23 -y " + self.renderFramesDirectory + "/" + self.truncatedDatasetFileName + ".mp4"

		os.system( arg )

		# delete all PNGs from this location when done.
		shutil.rmtree(tmpDir)

	def numberFormatter(self, pNum):
		return "%03d" % (pNum,)

	def displayText(self, pTxt, pPosLeft, pPosRight, pColor):
		surf_text = self.font.render(pTxt, False, pColor)
		rect = surf_text.get_rect()
		rect.topleft = (pPosLeft, pPosRight)
		self.surf_window.blit(surf_text, rect)	

	def displayTextLarge(self, pTxt, pPosLeft, pPosRight, pColor):
		surf_text = self.fontLarge.render(pTxt, False, pColor)
		rect = surf_text.get_rect()
		rect.topleft = (pPosLeft, pPosRight)
		self.surf_window.blit(surf_text, rect)	

	def specialNumber(self):
		return math.pi
		return ((1+5 ** 0.5) / 2) * pow(math.pi, 4) 

	def getPhi(self):
		return ((1+5 ** 0.5) / 2)

	def makeHistogram(self, pImg):

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

		# DRAW VERTICAL LINE AT POINT OF LOWEST STANDARD DEV
		# find the low points in the standard dev
		# put all the Y values of the standard deviation in a separate list
		# an entry in the list looks like [[0, 900], [10, 639.1957450511611]]
		# we want to look a the second nested list, and only the Y component
		# the higher this number is, the lower it occurs on the chart, i.e. the lowest standard dev value
		tmpList = []
		for index in range(0, len(self.standardDefList)):
			tmpList.append( self.standardDefList[index][1][1] )

		tmpX = self.standardDefList[tmpList.index( max(tmpList) )][1][0]
		tmpY = max(tmpList) # returns what represents the lowest standard dev value
		print(tmpX, tmpY)
		self.draw.line(( tmpX, 0, tmpX, tmpY ), fill=(self.colorEntrySignal), width=1 )

		# DRAW HISTOGRAM AT TOP OF CHART
		for r in range(0, len(imbalanceRatioArray)):
			self.draw.line(( r-1, 100+imbalanceRatioArray[r-1][0]*self.specialNumber(), r, 100+imbalanceRatioArray[r][0]*self.specialNumber()), \
				fill=(self.colorHistogramUp), width=1 )
			self.draw.line(( r-1, 100+imbalanceRatioArray[r-1][1]*self.specialNumber(), r, 100+imbalanceRatioArray[r][1]*self.specialNumber()), \
				fill=(self.colorHistogramDown), width=1 )
		
		if not os.path.exists(self.renderHistogramDirectory + self.histogramAnimationDir):
			os.makedirs(self.renderHistogramDirectory + self.histogramAnimationDir)

		img.save(self.renderHistogramDirectory + self.histogramAnimationDir + self.truncatedDatasetFileName + "_hist_" + self.numberFormatter(self.offsetIndex)  +  ".png", format='PNG')
		print(self.datasetFile + " simulation done.")


		# img.show()


	def setPermutationName(self, pIterationNumber):
		self.permutationName = \
		str(pIterationNumber) + "_" + \
		str(self.datasetFile) + "_" + \
		str(self.particlesBirthCount) + "_" + \
		str(self.candlestickWidth) + "_" + \
		str(self.particleDiameter) + "_" + \
		str(self.candleGutter)

	def setParticlesBirthCount(self, pParticleBirthCount):
		self.particlesBirthCount = pParticleBirthCount

	def	setCandlestickWidth(self, pCandlestickWidth):
		self.candlestickWidth = pCandlestickWidth

	def setParticleDiameter(self, pParticleDiameter):
		self.particleDiameter = pParticleDiameter

	def setCandleGutter(self, pCandleGutter):
		self.candleGutter = pCandleGutter

		
#--- RUNTIME NOTES  --------------------------------------------------------------------
# This particular flavor uses CSV files containing OHLC data. These files can be static or
# dynamically updated, provided they adhere to the structure as included in sample CSV.
# Place or write all CSV files in the "csv" folder at project root.
# Or store the relative path to your CSV files in the app.yaml 
appYaml = open("../config/app.yaml", "r").readlines()
pathToCSVs = appYaml[0].split(":")[1] # TODO: make this a little smarter

_datasetList = []
files = glob.glob(pathToCSVs + "/*.csv")
files.sort(key=os.path.getmtime)
sortList = []

for csvfile in reversed(files):
	_datasetList.append(csvfile)

arbitraryRunLimit = 100
for i in range(0, arbitraryRunLimit): 

	for dataset in _datasetList[:3]: # loop all datasets
		# to loop iterations within a dataset use
		# for i in range(0, 100):		
		cvt = ControlVolumeTank()
		# cvt.offsetIndex = i  # uncomment when looping iterations within a dataset
		cvt.datasetFile = dataset
		print( "running dataset: ", dataset )
		random.seed()
		cvt.setParticleDiameter( 2 )
		cvt.setCandlestickWidth( 3 )
		cvt.setParticlesBirthCount( _particleBirthCount ) #4000 for production
		cvt.setCandleGutter( 1 )
		cvt.game_run()
