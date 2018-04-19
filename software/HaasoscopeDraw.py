import HaasoscopeLib
reload(HaasoscopeLib) # in case you changed it, and to always load some defaults
import time, sys
import matplotlib.pyplot as plt
from serial import SerialException

#Some options
#HaasoscopeLib.num_board = 2 # Number of Haasoscope boards to read out (default is 1)
#HaasoscopeLib.ram_width = 12 # width in bits of sample ram to use (e.g. 9==512 samples (default), 12(max)==4096 samples)
#HaasoscopeLib.max10adcchans = [(0,110),(0,118),(1,110),(1,118)] #max10adc channels to draw (board, channel on board), channels: 110=ain1, 111=pin6, ..., 118=pin14, 119=temp # default is none, []

d = HaasoscopeLib.Haasoscope()
d.construct()

#Some other options
#d.serport="COM7" # the name of the serial port on your computer, connected to Haasoscope, like /dev/ttyUSB0 or COM8, leave blank to detect automatically!
#d.domaindrawing=False # whether to keep updating the main plot (on by default)
d.serialdelaytimerwait=100 #150 #300 # 600 # delay (in 2 us steps) between each 32 bytes of serial output (set to 600 for some slow USB serial setups, but 0 normally)
#d.dolockin=True; d.dolockinplot=d.domaindrawing # whether to calculate the lockin info on the FPGA and read it out (off by default)

try:
    if not d.setup_connections(): sys.exit()
    if not d.init(): sys.exit()
    d.on_launch()
    
    #can change some things
    #d.selectedchannel=0
    #d.tellswitchgain(d.selectedchannel)
    #d.togglesupergainchan(d.selectedchannel)
    #d.toggletriggerchan(d.selectedchannel)
    
    nevents=0; oldnevents=0; tinterval=100.; oldtime=time.time()
    while 1:
        if d.paused: time.sleep(.1)
        else:
            if not d.getchannels(): break
            #print d.xydata[0][0][12], d.xydata[0][1][12] # print the x and y data, respectively, for the 13th sample on fast adc channel 0
            #if len(HaasoscopeLib.max10adcchans)>0: print "slow", d.xydataslow[0][0][99], d.xydataslow[0][1][99] # print the x and y data, respectively, for the 100th sample on slow max10 adc channel 0
            #if d.dolockin: print d.lockinamp, d.lockinphase
            if d.db: print time.time()-d.oldtime,"done with evt",nevents
            nevents+=1
            if nevents-oldnevents >= tinterval:
                elapsedtime=time.time()-oldtime
                lastrate = round(tinterval/elapsedtime,2)
                print nevents,"events,",lastrate,"Hz"
                oldtime=time.time()
                if lastrate>40: tinterval=500.
                else: tinterval=100.
                oldnevents=nevents
            if d.getone: d.paused=True
        d.redraw()
        if len(plt.get_fignums())==0:
            if d.domaindrawing: break # quit when all the plots have been closed
            elif nevents>50: break
except SerialException:
    print "serial com failed!"
finally:
    d.cleanup()