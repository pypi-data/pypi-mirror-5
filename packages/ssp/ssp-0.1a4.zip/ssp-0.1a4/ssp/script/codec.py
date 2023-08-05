#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# Copyright 2012 by Idiap Research Institute, http://www.idiap.ch
#
# See the file COPYING for the licence associated with this software.
#
# Author(s):
#   Phil Garner, May 2012
#
from ... import ssp
import numpy as np
import numpy.linalg as linalg
from optparse import OptionParser
from os.path import splitext

def main():
  # Command line
  op = OptionParser(usage="usage: %prog [options] [inFile outFile]")
  op.add_option("-r", dest="rate", default='16000',
                help="Sample rate")
  op.add_option("-f", dest="fileList",
                help="List of input output file pairs")
  op.add_option("-m", dest="framePeriod", action="store", type="int",
                help="Frame period")
  op.add_option("-e", dest="encode", action="store_true", default=False,
                help="Encode source files")
  op.add_option("-p", dest="pitch", action="store_true", default=False,
                help="Encode source files, linear cont. pitch only")
  op.add_option("-d", dest="decode", action="store_true", default=False,
                help="Decode source files")
  op.add_option("-o", dest="ola", action="store_false", default=True,
                help="Concatenate frames (i.e., don't use OLA)")
  op.add_option("-x", dest="excitation", action="store_true", default=False,
                help="Output excitation waveform instead of encoding")
  op.add_option("-n", dest="normalise", action="store_true", default=False,
                help="Normalise output to same power as input")
  (opt, arg) = op.parse_args()

  # For excitation we need to disable OLA
  if opt.excitation:
      opt.ola = False

  # Fall back on command line input and output
  pairs = []
  if opt.fileList:
      with open(opt.fileList) as f:
          pairs = f.readlines()
  else:
      if len(arg) != 2:
          print "Need two args if no file list"
          exit(1)
      pairs = [ ' '.join(arg) ]

  lpOrder = {
      8000: 10,
      16000: 24,
      22050: 24
  }


  def encode(a, pcm):
      """
      Encode a speech waveform.  The encoding framers (frames and pitch)
      pad the frames so that the first frame is centered on sample zero.
      This is consistent with STRAIGHT and SPTK (I hope!).  At least, it
      means the pitch can have longer frame lengths and still align with
      the OLA'd frames.
      """
      if opt.ola:
          frameSize = pcm.seconds_to_period(0.025, 'atleast') # 25ms frame size
      else:
          frameSize = framePeriod
      pitchSize = pcm.seconds_to_period(0.1, 'atmost')
      print "Encoding with period", framePeriod, "size", frameSize, \
            "and pitch window", pitchSize

      # First the pitch as it's on the unaltered waveform.  The frame
      # should be long with no window.  1024 at 16 kHz is 64 ms.
      pf = ssp.Frame(a, size=pitchSize, period=framePeriod)
      pitch, hnr = ssp.ACPitch(pf, pcm)

      # Pre-emphasis
      pre = ssp.parameter("Pre", None)
      if pre is not None:
          a = ssp.PoleFilter(a, pre) / 5

      # Keep f around after the function so the decoder can do a
      # reference decoding on the real excitaton.
      global f
      f = ssp.Frame(a, size=frameSize, period=framePeriod)
      #aw = np.hanning(frameSize+1)
      aw = ssp.nuttall(frameSize+1)
      aw = np.delete(aw, -1)
      w = ssp.Window(f, aw)
      ac = ssp.Autocorrelation(w)
      lp = ssp.parameter('AR', 'levinson')
      if lp == 'levinson':
          ar, g = ssp.ARLevinson(ac, lpOrder[r])
      elif lp == 'ridge':
          ar, g = ssp.ARRidge(ac, lpOrder[r], 0.03)
      elif lp == 'lasso':
          ar, g = ssp.ARLasso(ac, lpOrder[r], 5)
      elif lp == 'sparse':
          ar, g = ssp.ARSparse(w, lpOrder[r], ssp.parameter('Gamma', 1.414))
      elif lp == 'student':
          ar, g = ssp.ARStudent(w, lpOrder[r], ssp.parameter('DoF', 50.0))

      if False:
          fig = ssp.Figure(5, 1)
          #stddev = np.sqrt(kVar)
          sPlot = fig.subplot()
          sPlot.plot(pitch, 'c')
          #sPlot.plot(kPitch + stddev, 'b')
          #sPlot.plot(kPitch - stddev, 'b')
          sPlot.set_xlim(0, len(pitch))
          sPlot.set_ylim(0, 500)
          plt.show()

      return (ar, g, pitch, hnr)


  def decode((ar, g, pitch, hnr)):
      """
      Decode a speech waveform.
      """
      nFrames = len(ar)
      assert(len(g) == nFrames)
      assert(len(pitch) == nFrames)
      assert(len(hnr) == nFrames)

      # The original framer padded the ends so the number of samples to
      # synthesise is a bit less than you might think
      if opt.ola:
          frameSize = framePeriod * 2
          nSamples = framePeriod * (nFrames-1)
      else:
          frameSize = framePeriod
          nSamples = frameSize * (nFrames-1)

      ex = ssp.parameter('Excitation', 'synth')

      # Use the original AR residual; it should be a very good
      # reconstruction.
      if ex == 'ar':
          e = ssp.ARExcitation(f, ar, g)

      # Just noise.  This is effectively a whisper synthesis.
      elif ex == 'noise':
          e = np.random.normal(size=f.shape)

      # Just harmonics, and with a fixed F0.  This is the classic robot
      # syntheisis.
      elif ex == 'robot':
          ew = np.zeros(nSamples)
          period = int(1.0 / 200 * r)
          for i in range(0, len(ew), period):
              ew[i] = period
          e = ssp.Frame(ew, size=frameSize, period=framePeriod)

      # Synthesise harmonics plus noise in the ratio suggested by the
      # HNR.
      elif ex == 'synth':
          # Harmonic part
          mperiod = int(1.0 / np.mean(pitch) * r)
          gm = ssp.GlottalModel(ssp.parameter('Pulse', 'impulse'))
          pr, pg = ssp.pulse_response(gm, pcm, period=mperiod, order=lpOrder[r])
          h = np.zeros(nSamples)
          i = 0
          frame = 0
          while i < nSamples and frame < len(pitch):
              period = int(1.0 / pitch[frame] * r)
              if i + period > nSamples:
                  break
              weight = np.sqrt(hnr[frame] / (hnr[frame] + 1))
              h[i:i+period] = gm.pulse(period, pcm) * weight
              i += period
              frame = i // framePeriod
          h = ssp.ARExcitation(h, pr, 1.0)
          fh = ssp.Frame(h, size=frameSize, period=framePeriod)

          # Noise part
          n = np.random.normal(size=nSamples)
          n = ssp.ZeroFilter(n, 1.0) # Include the radiation impedance
          fn = ssp.Frame(n, size=frameSize, period=framePeriod)
          for i in range(len(fn)):
              fn[i] *= np.sqrt(1.0 / (hnr[i] + 1))

          hgain = ssp.parameter("HGain", 1.0)
          e = fn + fh * hgain

      # Like harmonics plus noise, but with explicit sinusoids instead
      # of time domain impulses.
      elif ex == 'sine':
          order = 20
          sine = ssp.Harmonics(r, order)
          h = np.zeros(nSamples)
          for i in range(0, len(h)-framePeriod, framePeriod):
              frame = i // framePeriod
              period = int(1.0 / pitch[frame] * r)
              weight = np.sqrt(hnr[frame] / (hnr[frame] + 1))
              h[i:i+framePeriod] = ( sine.sample(pitch[frame], framePeriod)
                                        * weight )
          fh = ssp.Frame(h, size=frameSize, period=framePeriod)
          n = np.random.normal(size=nSamples)
          fn = ssp.Frame(n, size=frameSize, period=framePeriod)
          for i in range(len(fn)):
              fn[i] *= np.sqrt(1.0 / (hnr[i] + 1))
          e = fn + fh*10

      # High order linear prediction.  Synthesise the harmonics using
      # noise to excite a high order polynomial with roots resembling
      # harmonics.
      elif ex == 'holp':
          # Some noise
          n = np.random.normal(size=nSamples)
          fn = ssp.Frame(n, size=frameSize, period=framePeriod)

          # Use the noise to excite a high order AR model
          fh = np.ndarray(fn.shape)
          for i in range(len(fn)):
              hoar = ssp.ARHarmonicPoly(pitch[i], r, 0.7)
              fh[i] = ssp.ARResynthesis(fn[i], hoar, 1.0 / linalg.norm(hoar)**2)
              print i, pitch[i], linalg.norm(hoar), np.min(fh[i]), np.max(fh[i])
              print ' ', np.min(hoar), np.max(hoar)
              # fh[i] *= np.sqrt(r / pitch[i]) / linalg.norm(fh[i])
              # fh[i] *= np.sqrt(hnr[i] / (hnr[i] + 1))

          # Weight the noise as for the other methods
          for i in range(len(fn)):
              fn[i] *= np.sqrt(1.0 / (hnr[i] + 1))
          e = fh # fn + fh*30

      # Shaped excitation.  The pulses are shaped by a filter to have a
      # rolloff, then added to the noise.  The resulting signal is
      # flattened using AR.
      elif ex == 'shaped':
          # Harmonic part
          gm = ssp.GlottalModel(ssp.parameter('Pulse', 'impulse'))
          gm.angle = pcm.hertz_to_radians(np.mean(pitch)*0.5)
          h = np.zeros(nSamples)
          i = 0
          frame = 0
          while i < nSamples and frame < len(pitch):
              period = int(1.0 / pitch[frame] * r)
              if i + period > nSamples:
                  break
              weight = np.sqrt(hnr[frame] / (hnr[frame] + 1))
              h[i:i+period] = gm.pulse(period, pcm) * weight
              i += period
              frame = i // framePeriod

          # Filter to mimic the glottal pulse
          hfilt = ssp.parameter("HFilt", None)
          hpole1 = ssp.parameter("HPole1", 0.98)
          hpole2 = ssp.parameter("HPole2", 0.8)
          angle = pcm.hertz_to_radians(np.mean(pitch)) * ssp.parameter("Angle", 1.0)
          if hfilt == 'pp':
              h = ssp.ZeroFilter(h, 1.0)
              h = ssp.PolePairFilter(h, hpole1, angle)
          if hfilt == 'g':
              h = ssp.GFilter(h, hpole1, angle, hpole2)
          if hfilt == 'p':
              h = ssp.PFilter(h, hpole1, angle, hpole2)
          fh = ssp.Frame(h, size=frameSize, period=framePeriod)

          # Noise part
          n = np.random.normal(size=nSamples)
          zero = ssp.parameter("NoiseZero", 1.0)
          n = ssp.ZeroFilter(n, zero) # Include the radiation impedance
          npole = ssp.parameter("NPole", None)
          nf = ssp.parameter("NoiseFreq", 4000)
          if npole is not None:
              n = ssp.PolePairFilter(n, npole, pcm.hertz_to_radians(nf))
          fn = ssp.Frame(n, size=frameSize, period=framePeriod)
          for i in range(len(fn)):
              fn[i] *= np.sqrt(1.0 / (hnr[i] + 1))

          # Combination
          assert(len(fh) == len(fn))
          hgain = ssp.parameter("HGain", 1.0)
          e = fn + fh * hgain
          hnw = np.hanning(frameSize)
          for i in range(len(e)):
              ep = ssp.Window(e[i], hnw)
              #ep = e[i]
              eac = ssp.Autocorrelation(ep)
              ea, eg = ssp.ARLevinson(eac, order=lpOrder[r])
              e[i] = ssp.ARExcitation(e[i], ea, eg)

      else:
          print "Unknown synthesis method"
          exit

      if opt.excitation:
          s = e.flatten('C')/frameSize
      else:
          s = ssp.ARResynthesis(e, ar, g)
          if opt.ola:
              # Asymmetric window for OLA
              sw = np.hanning(frameSize+1)
              sw = np.delete(sw, -1)
              s = ssp.Window(s, sw)
              s = ssp.OverlapAdd(s)
          else:
              s = s.flatten('C')

      gain = ssp.parameter("Gain", 1.0)
      return s * gain

  #
  # Main loop over the file list
  #
  r = int(opt.rate)
  pcm = ssp.PulseCodeModulation(r)
  if opt.framePeriod:
      framePeriod = opt.framePeriod
  else:
      framePeriod = pcm.seconds_to_period(0.005, 'atleast') # 5ms period

  for pair in pairs:
      loadFile, saveFile = pair.strip().split()
      aNorm = None
      dNorm = None

      # Neither flag - assume a best effort copy
      if not (opt.encode or opt.decode or opt.pitch):
          a = pcm.WavSource(loadFile)
          d = decode(encode(a, pcm))
          if opt.normalise:
              d *= linalg.norm(a)/linalg.norm(d)
          pcm.WavSink(d, saveFile)

      # Encode to a file
      if opt.encode:
          a = pcm.WavSource(loadFile)
          (ar, g, pitch, hnr) = encode(a, pcm)

          # The cepstrum part is just like HTK
          c = ssp.ARCepstrum(ar, g, lpOrder[r])
          period = float(framePeriod)/r
          ssp.HTKSink(saveFile, c, period)

          # F0 and HNR are both text formats
          (path, ext) = splitext(saveFile)
          saveFileLF0 = path + ".f0"
          saveFileHNR = path + ".hnr"
          np.savetxt(saveFileLF0, np.log(pitch))
          np.savetxt(saveFileHNR, hnr)

      # Encode cont. pitch only to a file
      if opt.pitch:
          a = pcm.WavSource(loadFile)
          (ar, g, pitch, hnr) = encode(a, pcm)

          # F0 and HNR are both text formats
          np.savetxt(saveFile, pitch)

      # Decode from a file
      if opt.decode:
          (path, ext) = splitext(loadFile)
          loadFileLF0 = path + ".f0"
          loadFileHNR = path + ".hnr"
          pitch = np.exp(np.loadtxt(loadFileLF0))
          hnr = np.loadtxt(loadFileHNR)
          c, period = ssp.HTKSource(loadFile)
          (ar, g) = ssp.ARCepstrumToPoly(c)
          d = decode((ar, g, pitch, hnr))
          pcm.WavSink(d, saveFile)
