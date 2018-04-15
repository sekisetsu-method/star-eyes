# star-eyes
v13 - production ready

THE SEKISETSU METHOD EXPLAINED
-----------------------------------------------------------------------------

### WHAT IT IS ###
Sekisetsu is a Japanese word for snowfall accumulation. The Sekisetsu Method (積雪メソッド) combines price action geometry (candlesticks) with fluid dynamics to reveal otherwise hidden structure and market participant intention in price charts. The method can also be termed "Price Action Fluid Dynamics". Many terms and ideas from fluid dynamics and chaotic systems are borrowed and used both in the code and as allegory in the training material. Regardless of terminology, the goal of the method is to empower the user to align trades with larger players. 

### HOW IT WORKS ###
OHLC price action data (in the form of a modified candlestick chart) creates the surfaces and boundaries within a control volume tank (CVT). The tank is filled with both heavy and light particles. The particles accumulate in the cavities and recesses of the price action surfaces. The pooling of particles results in three patterns: top-heavy, bottom-heavy and stagnant accumulations. These differences can be viewed directly on the chart, and are further expressed as an "imbalance ratio histogram". A standard deviation method is employed to locate relatively stagnant periods of price action. It is these periods of lower volatility coinciding with imbalances in particle accumulation where major entry signals emerge, revealing both the location and trading direction of large players, i.e. market makers. 

The software is open source, highly configurable, and easily lends itself to integration with existing trading systems.

SETUP & USAGE
-----------------------------------------------------------------------------

* CSV files need to live in the "csv" folder at project root.
* Histograms are created in the "histograms" folder at project root.
* Simulations (frame by frame PNGs of the simulation) are created in the "simulations" folder at project root.

To run the program: 
* Use PIP to install all requirements (see requirements.txt).
* Add CSV files to the "csv" folder at project root.
* If running native linux, comment out os.environ['SDL_VIDEODRIVER']='dummy'
	(This is a Windows workaround when running the Ubuntu shell on Windows. Running in native linux will display the game window. Windows will run in a kind of silent mode, but will still perform all calculations and produce the histograms and animations.)
* from a shell, run:
	$ python cvt_[version_number].py

SIGNAL ANALYSIS
-----------------------------------------------------------------------------
Signal analysis consists of coinciding low points in the standard deviation with high points in a given particle accumulation. This typically occurs during the lull period prior to the London open, although the signal can occur in many variations throughout the trading day. 

v13 "star-eyes" is optimized for USDJPY 15m chart data but will work with any OHLC data (currencies, equities or crypto).

ADD'L NOTES
-----------------------------------------------------------------------------
Project website: http://www.sekisetsumethod.com

Thanks to Maarten Baert's excellent physics engine (licensed under LGPL).
More info: http://www.maartenbaert.be/extremephysics/

"Star Eyes" is a jazz nightclub in Nagoya, Japan. 
