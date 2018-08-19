# star-eyes
v14 - production ready

THE SEKISETSU METHOD EXPLAINED
-----------------------------------------------------------------------------

### WHAT IT IS ###
Sekisetsu is a Japanese word for snowfall accumulation. The Sekisetsu Method (積雪メソッド) is a technical analysis tool combining price action geometry (candlesticks) with fluid dynamics to reveal otherwise hidden structure and market participant intention, and displays this information on a price chart. The method can also be termed "Price Action Fluid Dynamics". Many terms and ideas from fluid dynamics and chaotic systems are borrowed and used both in the code and as allegory in the training material. Regardless of terminology, the goal of the method is to empower the user to align trades with larger players. 

### HOW IT WORKS ###
OHLC price action data (in the form of a modified candlestick chart) creates the surfaces and boundaries within a control volume tank (CVT). The tank is filled with both heavy and light particles. The particles accumulate in the cavities and recesses of the price action surfaces. The pooling of particles results in three patterns: top-heavy, bottom-heavy and stagnant accumulations. These differences can be viewed directly on the chart, and are further expressed as an "imbalance ratio histogram". A standard deviation method is employed to locate relatively stagnant periods of price action. It is these periods of lower volatility coinciding with imbalances in particle accumulation where major entry signals emerge, revealing both the location and trading direction of large players, i.e. market makers. 

The software is open source, highly configurable, and easily lends itself to integration with existing trading systems.

SETUP & USAGE
-----------------------------------------------------------------------------

* CSV files location is set in the config/app.yaml. 
* Histograms are created in the "histograms" folder at project root.
* Simulations (frame by frame PNGs of the simulation) are created in the "simulations" folder at project root.
* mp4 videos are created from simulation sequences. These allow you to see the particle distribution in action.
* To autogenerate CSV files from MetaTrader4, place the config/CSV_WRITER.mq4 indicator in your application's "Indicators" folder. On Windows this is usually something like 'C:\Users\<USER>\AppData\Roaming\MetaQuotes\Terminal\<GUID>\MQL4\Indicators'. MetaTrader4 will write the CSV to 'C:\Users\<USER>\AppData\Roaming\MetaQuotes\Terminal\<GUID>\MQL4\Files'. Write a shell script to regularly copy this file to the "csv" directory located in this project's root. 

To run the program: 
* Use PIP to install all requirements (see requirements.txt).
* Add CSV files to a location set in the config/app.yaml. 
* If running native linux, comment out os.environ['SDL_VIDEODRIVER']='dummy'
	(This environment var is a Windows workaround when running the Ubuntu shell on Windows. Running in native linux will display the game window. Windows will run in a kind of silent mode, but will still perform all calculations and produce the histograms and animations.)
* from a shell, run:
	$ python cvt_00014.py --sigmaperiod 23 --highlightsigma True -v

SIGNAL ANALYSIS
-----------------------------------------------------------------------------
Signal analysis consists of coinciding low points in the standard deviation with high points in a given particle accumulation. This typically occurs during the lull period prior to the London open, although the signal can occur in many variations throughout the trading day. 

v14 "star-eyes" is optimized for USDJPY 15m chart data but will work with any OHLC data (currencies, equities or crypto).

ADD'L NOTES
-----------------------------------------------------------------------------
Project website: http://www.sekisetsumethod.com

Thanks to Maarten Baert's excellent physics engine (licensed under LGPL).
More info: http://www.maartenbaert.be/extremephysics/

"Star Eyes" is a jazz standard and name of a favorite nightclub in Nagoya, Japan. 
