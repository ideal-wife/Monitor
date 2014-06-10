#!/usr/bin/python
import os,sys
import time
import re
from datetime import datetime
LOOP =0



def initEnv():
		global spPattern,hz,dPattern,pagesize
		global statArr,pidDir
		pidDir  = "/proc/"+str(pid)+"/"
		try:
				if not os.access(pidDir,os.F_OK|os.R_OK):
					print >>sys.stderr,"Error: pid is invalid!"
					sys.exit(1)    
		except Exception,e:
				sys.exit(1)
		spPattern       = re.compile("\s+")
		dPattern        = re.compile("\s*:\s*")
		statArr         = spPattern.split(_readLine(pidDir+"stat"))
		hz                      = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
		hz                      = float(hz)
		pagesize        = int(os.sysconf(os.sysconf_names['SC_PAGE_SIZE']))
		print("\n[Pid Monitor v1.0]\n")

		#print cmd
		cmdCal()
		#pint the pid
		pidCal()
		#print start time:
		timeCal()
		openFiles()
		print("\n\n")

def pidCal():
		global pid,statArr,ppid,pgid,spid
		ppid,pgid,spid  =statArr[3:6]
		print("Pid:[%s]\tPPid:[%s]\tPGid:[%s]\tSPid:[%s]" %(pid,ppid,pgid,spid))

def timeCal():
		global start,hz,seconds
		cpustat =_readAll("/proc/stat")
		for st in cpustat:
				arr = spPattern.split(st.rstrip('\n'))
				if arr[0]=='btime':
						btime   =arr[1]
						break
		seconds =int(statArr[21])/hz + int(btime)
		start   =time.strftime("%Y/%m/%d %H:%M:%S",time.gmtime(seconds-int(time.timezone)))
		print("Start time:[%s]" %(start))


def cmdCal():
		global cmd
		cmd             = _readLine(pidDir+"cmdline")
		print("Cmd:[%s]"%(cmd))


def openFiles():
		global openFiles
		openFiles       =[]
		try:
			files   =os.listdir(pidDir+"fd/")
		except Exception,e:
			print >>sys.stderr,"Error:"+str(e)
			sys.exit(1)
		for file in files:
				try:
						link    =os.readlink(pidDir+"fd/"+file)
						openFiles.append(file+': ['+link+']')
				except Exception ,e:
						NOne
		print "OpenFiles:["+str(len(openFiles))+"]"
		loopsize        =0
		for i in range(len(openFiles)):
				loopsize        +=1
				if(loopsize >8):
						print"\t......"
						break
				print "\t"+openFiles[i]


def loopDisp():
	global rawValue,dispValue
	for disp in arrDisp:
		for i in range(disp.getQuantity()):
			rawValue    = disp.getDelta()[i]
			dispValue   = formatValue(rawValue,disp.getUnit()[i])
			width       = disp.getWidth()[i]
			sys.stdout.write(formatWidth(width) % (dispValue))
			sys.stdout.write(" ")
	sys.stdout.write("\n")
	sys.stdout.flush()


def initDisp():
		global arrDisp,display,ioDisplay
		arrDisp     = []
		display    = Display(["HLPid_monitors",'stat','thrd','secs','usr','sys','util','vsiz','rssz'],
												[14,4,4,13,13,13,6,7,7],[0,0,0,0,0,0,0,5,5],9)
		arrDisp.append(display)

		ioDisplay       = IODisplay(['read','writ','rdsz','wrsz'],[4,4,4,4],[3,3,4,4],4)
		arrDisp.append(ioDisplay)
def loopMon():
		global display,pidDir,ioDisplay

		arrLine         = _readLine(pidDir+"stat")
		display.setValue2(arrLine)
		display.calDelta()
		arrLine         = _readAll(pidDir+"io")
		ioDisplay.setValue2(arrLine)
		ioDisplay.calDelta()


def loopTitle():
		global title
		for disp in arrDisp:
				for i in range(disp.getQuantity()):
				   title   = disp.getTitle()[i]
				   sys.stdout.write(formatWidth(disp.getWidth()[i]) % (title))
				   sys.stdout.write(" ")
		sys.stdout.write("\n")
		sys.stdout.flush()

def formatValue(rawValue,unit):
		if unit == 1:
				rawIntValue = int(rawValue)
				if rawIntValue<1000:
						return rawValue
				elif rawIntValue >=1000 and rawIntValue <1000000:
						return str(rawIntValue/1000)+"K"
				elif rawIntValue>=1000000:
						return str(rawIntValue/1000000)+"M"
		if unit == 3:
				rawIntValue = int(rawValue)
				if rawIntValue<10000:
						return rawValue
				elif rawIntValue>=10000 and rawIntValue<1000000:
						return str(rawIntValue/1000)+"K"
				elif rawIntValue>=1000000:
						return str(rawIntValue/1000000)+"M"
		if unit == 4:
				rawIntValue = int(rawValue)
				if rawIntValue<10000:
						return rawValue
				elif rawIntValue>=10000 and rawIntValue<1024000:
						return str(rawIntValue/1024)+"K"
				elif rawIntValue>=1024000 and rawIntValue< 1048576:
						return str(float("%.1f" %(rawIntValue/1024.0/1024.0)))+"M"
				elif rawIntValue> 1048576 and rawIntValue < 1048576000:
						return str(rawIntValue/1024/1024)+"M"
				elif rawIntValue >= 1048576000 and rawIntValue< 1073741824:
						return str(float("%.1f" %(rawIntValue/1024.0/1024.0/1024.0)))+"G"
				elif rawIntValue>=1073741824:
						return str(rawIntValue/1024/1024/1024)+"G"
		if unit == 5:
				rawIntValue = int(rawValue)
				if rawIntValue<100000:
						return rawValue
				elif rawIntValue>=100000 and rawIntValue<102389760:
						return str(rawIntValue/1024)+"K"
				elif rawIntValue>=102389760:
						return str(rawIntValue/1024/1024)+"M"

		return rawValue

def formatWidth(width):
		return "%"+str(width)+"s"

def _readLine(filePath):
		try:
				fh   = open(filePath,'r')
				line = fh.readline()
				fh.close()
				return line
		except Exception,e:
				try:
						fh.close()
				except:
						None
				print >>sys.stderr,"Error: "+str(e)
				sys.exit(1)



def _readAll(filePath):
		try:
				fh              = open(filePath,'r')
				arrLine = fh.readlines()
				fh.close()
				return arrLine
		except Exception,e:
				try:
						fh.close()
				except:
						None
				print >>sys.stderr,"Error: " + str(e)
				sys.exit(1)

class Display:
	def __init__(self,title,width,unit,quantity):
		self.title      = title
		self.width      = width
		#unit 0:primitve    1:1000 3bytes  2:1024 3bytes,3:10000  4bytes 4:10000 4bytes,k/m/g
		self.unit       = unit
		#the array count
		self.quantity   = quantity

		self.pre                = [0,0]
		self.cur                = None
		self.delta              = None

	def getQuantity(self):
		return self.quantity
 
	def getCur(self):
		return self.cur
	def getUnit(self):
		return self.unit
	def getTitle(self):
		return self.title
	def getWidth(self):
		return self.width
	def getDelta(self):
		return self.delta
 
		# the default delta calculation
	def calDelta(self):
				self.delta      = []
				arr             = spPattern.split(self.cur)
				cur_time        = str(time.strftime("%m/%d %H:%M:%S"))
				state           = arr[2]
				thrd            = arr[19]
				secs            = forTime(time.time()-seconds)
				usr                     = forTime(float(arr[13])/hz)
				sys                     = forTime(float(arr[14])/hz)
				util            = ((float(arr[14])-self.pre[1]+float(arr[13])-self.pre[0])/hz*1000/(interval*1000))*100
				util            = ("%.2f"%util)
				self.pre[0]     = float(arr[13])
				self.pre[1]     = float(arr[14])
				vsiz            = arr[22]
				rss             = int(arr[23])*pagesize
				self.delta.extend([cur_time,state,thrd,secs,usr,sys,util,vsiz,rss])

	def setValue2(self,cur):
		self.cur        = cur

class IODisplay(Display):
	def __init__(self,title,width,unit,quantity):
		Display.__init__(self,title,width,unit,quantity)
		self.pre=[0,0,0,0]
	def calDelta(self):
		self.delta      =[]
		for item in self.cur:
			arr     = dPattern.split(item.strip("\n "))
			if(arr[0]=='syscr'):
				read            = int(arr[1])-self.pre[0]
				self.pre[0]     = int(arr[1])
			elif(arr[0]=='syscw'):
				writ            = int(arr[1])-self.pre[1]
				self.pre[1]     = int(arr[1])
			elif(arr[0]=='read_bytes'):
				rdsz            = int(arr[1])-self.pre[2]
				self.pre[2]     = int(arr[1])
			elif(arr[0]=='write_bytes'):
				wrsz            = int(arr[1])-self.pre[3]
				self.pre[3]     = int(arr[1])
		self.delta.extend([read,writ,rdsz,wrsz])


def forTime(ss):
		hours, remainder        = divmod(ss, 3600)
		minutes,sds             = divmod(remainder,60)
		if hours < 10:
				hours   ="0"+str(int(hours))
		if minutes < 10:
				minutes ="0"+str(int(minutes))
		sds     = ("%.3f"%(sds))
		if float(sds) < 10:
				sds     ="0"+str(sds)
		format  =str(int(hours))+":"+str(int(minutes))+":"+str(sds)
		return format

interval        =1

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print >>sys.stderr,"Error: pls input pid!"
		sys.exit(1)
	pid     =str(sys.argv[1])
	initEnv()
	initDisp()
	try:
		while(1):
			loopMon()
			if LOOP%10 ==0:
				loopTitle()
			if(LOOP != 0):
				loopDisp()         
			LOOP += 1
			time.sleep(interval)
	except Exception,e:
		print str(e)
		sys.exit(1)
