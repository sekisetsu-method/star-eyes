# Instructions for setting up Sekisetsu Method from the ground up

* Install CSV_WRITER.mq4 (writes OHLC data in CSV format)
	
> Note: On Windows, put the indicator in your appdata/roaming folder, e.g. C:\Users\[user name]\AppData\Roaming\MetaQuotes\Terminal\[guid]\MQL4\Indicators

* Open C:\Program Files (x86)\FXCM MetaTrader 4\terminal.exe

* Install indicator on chart
	
> Note: On Windows, CSV files will be written to C:\Users\[user name]\AppData\Roaming\MetaQuotes\Terminal\[guid]\MQL4\Files

* Use powershell to start copy_service.cmd (a RoboCopy script)

* If not using real-time data (CSV files), just copy one or more CSV files to the ./csv folder