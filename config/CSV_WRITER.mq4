#property indicator_chart_window
#define c 6
#define e 7

extern bool show_comment=true;

string tmpFileName="";
string date="";
string time="";
string high="";
string low="";
string close="";
string open="";
string volume="";
string delimiter=",";
int	handlefile=0;
int	b=0;
int	d=0;
int	bar=0;
int	res=0;
bool writefile=false;

int init()
{
	return(0);
}

int deinit()
{
	if(show_comment)
  {
    Comment(" ");
	}
  return(0);
}

int start()
{
	if(show_comment)
	{
		constructComment();
	}

	if(bar==Bars)
	{
		return(0);
	}


  tmpFileName = Symbol() + "_" + Period() + "m_" + date + "_" + Hour() + "." + Minute() + ".csv";

	handlefile = FileOpen(tmpFileName, FILE_CSV|FILE_WRITE, " ");

	if(handlefile>0)
	{ 
		for(int i=Bars-1; i>=0; i--)
		{
			date=TimeToStr(Time[i], TIME_DATE);
			time=TimeToStr(Time[i], TIME_MINUTES);
			high=DoubleToStr(High[i], Digits);
			low=DoubleToStr(Low[i], Digits);
			close=DoubleToStr(Close[i], Digits);
			open=DoubleToStr(Open[i], Digits);
			volume=DoubleToStr(Volume[i], 0);
			writefile=FileWrite(handlefile, date+delimiter+time+delimiter+open+delimiter+high+delimiter+low+delimiter+close+delimiter+volume);
		}
	}
	else
	{
		for(i=Bars-1; i>=0; i--)
		{
			date=TimeToStr(Time[i], TIME_DATE);
			time=TimeToStr(Time[i], TIME_MINUTES);
			high=DoubleToStr(High[i], Digits);
			low=DoubleToStr(Low[i], Digits);
			close=DoubleToStr(Close[i], Digits);
			open=DoubleToStr(Open[i], Digits);
			volume=DoubleToStr(Volume[i], 0);
			writefile=FileWrite(handlefile, date+delimiter+time+delimiter+open+delimiter+high+delimiter+low+delimiter+close+delimiter+volume);
		}

		if(writefile)
		{
			d=e;
		}
	} 

	if(writefile)
	{
		FileClose(handlefile);	
	}
	 return(0);
}

string constructComment()
{
	 date=TimeToStr(Time[0], TIME_DATE);
	 time=TimeToStr(Time[0], TIME_MINUTES);
	 high=DoubleToStr(High[0], Digits);
	 low=DoubleToStr(Low[0], Digits);
	 close=DoubleToStr(Close[0], Digits);
	 open=DoubleToStr(Open[0], Digits);
	 volume=DoubleToStr(Volume[0], 0);
	 Comment("CSV_WRITER ", Symbol(), " period M", Period(),"\n\n", "LAST BAR DATA : \n", "date	 =	",date,"\n",
			 "time	 =	",time,"\n","high	 =	",high,"\n", "low	=	",low,"\n", "volume =	",volume);
	 return("");
} 

