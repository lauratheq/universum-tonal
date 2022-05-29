#!/usr/bin/python3

# NAME
#   Image to midi - a converter
#
# SYNOPSIS
#   ./image-to-midi.py -i <source> -o <target> [-bd]
#
# DESCRIPTION
#   This script converts images (currently jpg files) to midi files. It reads
#   images from left to right row by row and decides what note, channel and
#   velocity a pixel has - based on the properties of the HSL color system.
#
# EXAMPLE:
#   ./image-to-midi.py -i resources/image-to-midi-sample-sgta.jpg -o image-to-midi-output-sgta.mid
#
# OPTIONS
#   -i|--input-file        path to the input file
#   -o|--output-file       path to the output file
#   -b|--ignore-background dark pixel will be ignored
#   -d|--dynamic-range     enables the dynamic color range instead of fixed definition
#
# LEGAL NOTE
#   Written and maintained by Laura Herzog (laura-herzog@outlook.com)
#   Permission to copy and modify is granted under the AGPL license
#   Project Information: https://github.com/lauraherzog/universum-tonal/

import getopt, sys, os.path
import cv2, colorsys
import numpy as np
from pathlib import Path
from midiutil.MidiFile import MIDIFile

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "vhi:o:b", ["verbose", "help", "input-file", "output-file", "ignore-background"])
  except getopt.GetoptError as err:
    help()
    sys.exit(2)

  verbose = False
  inputFile = None
  outputFile = None
  ignoreBackground = False
  dynamicRange = False

  for operator, argument in opts:
    if operator in ("-h", "--help"):
      help()
      sys.exit()
    elif operator in ("-i", "--input-file"):
      inputFile = argument
      checkInputFile(inputFile)
    elif operator in ("-o", "--output-file"):
      outputFile = argument
      checkOutputFile(outputFile)
    elif operator in ("-b", "--ignore-background"):
      ignoreBackground = True
    elif operator in ("-v", "--verbose"):
      verbose = True
    else:
      assert False, "unhandled option"

  print("Converting image to midi")
  print("Step: convertImageToHSV")
  convertedData = convertImageToHSV(inputFile)
  print("Step: convertImageToMidi")
  convertedData = convertHSVToMidi(inputFile, convertedData, ignoreBackground, verbose)
  print("Step: buildMidiFile")
  buildMidiFile(convertedData, outputFile, verbose)
  print("Done")

def convertImageToHSV(inputFile):
  imageObject = cv2.imread(inputFile)
  imageHeigth, imageWidth, imageChannel = imageObject.shape
  convertedData = {}
  # rows from left to right
  for x in range(0, imageWidth):
    for y in range(0, imageHeigth):
      # get rgb value (they are switched in cv2) and convert them to hsv
      b, g, r = imageObject[x, y]
      (h, s, v) = convertToHSV(b, g, r)
      convertedData["{}-{}".format(x,y)] = (h, s, v)

  return convertedData

def convertHSVToMidi(inputFile, data, ignoreBackground, verbose):
  checkData = []
  convertedData = {}
  readAdjacentPixel = []
  imageObject = cv2.imread(inputFile)
  imageHeigth, imageWidth, imageChannel = imageObject.shape
  
  # rows from left to right
  for x in range(0, imageWidth):
    for y in range(0, imageHeigth):
      if "{}-{}".format(x,y) in readAdjacentPixel:
        continue

      (h, s, v) = data["{}-{}".format(x,y)]

      # set the note
      note = int((((h - 0) * (108 - 21)) / (360 - 0)) + 21)

      # set the velocity
      velocity = int((((s - 0) * (127 - 0)) / (100 - 0)) + 0)

      # set the channel
      if velocity <= 5:
        if ignoreBackground == True:
          continue
        channel = 15
      else:
        channel = int((((v - 0) * (0 - 14)) / (100 - 0)) + 14)

      # set start time
      start = x

      # set duration based on adjacent pixel
      duration = 1
      nextPixel = x + 1
      while nextPixel < imageWidth:

        nb, ng, nr = imageObject[nextPixel, y]
        (nh, ns, nv) = convertToHSV(nb, ng, nr)

        if nh == h:
          duration = duration + 1
          if "{}-{}".format(nextPixel,y) not in readAdjacentPixel:
            readAdjacentPixel.append("{}-{}".format(nextPixel,y))
        else:
          break

        nextPixel = nextPixel + 1

      if (channel, note, velocity, start) not in checkData:
        convertedData["{}-{}".format(x,y)] = (channel, note, velocity, start, duration)

    if verbose == True:
      print("Converted line {} of {}".format(x, imageWidth))
  return convertedData

def buildMidiFile(data, outputFile, verbose):
  blockedNotes = []

  # build a mf
  mf = MIDIFile(16)
  for i in range(0,15):
    mf.addTrackName(i, 0, "Track {}".format(i))
    mf.addTempo(i, 0, 480)

  # add note to that mf
  for node, note in data.items():
    channel, pitch, velocity, start, duration = note

    # skip blocked notes
    if (channel, pitch, start) in blockedNotes:
      continue

    if (channel, pitch, start) not in blockedNotes:
      blockedNotes.append((channel, pitch, start))
      mf.addNote(channel, 0, pitch, start, duration, velocity)
      if verbose == True:
        print("Added {}".format(node))

    for d in range(0, duration):
      start = start + d
      if (channel, pitch, start) not in blockedNotes:
        blockedNotes.append((channel, pitch, start))

  outputFile = open(outputFile, "wb")
  mf.writeFile(outputFile)

# checks the inputFile if there are any validation errors
def checkInputFile(inputFile):
  if os.path.exists(inputFile) == False:
    printError("File not found")

  if inputFile.lower().endswith(('.png', '.jpg', '.jpeg')) == False:
    printError("Filetype not supported. Use .jpg and .jpeg")

  return True

# checks the ouputFile if there are any validation errors
def checkOutputFile(outputFile):
  if outputFile.lower().endswith(('.mid')) == False:
    printError("Filetype not supported. Use .mid")

  return True

def convertToHSV(b, g, r):
  (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
  (h, s, v) = (int(h*360), int(s*100), int(v*100))
  return (h, s, v)

# help, I need somebody, help!
def help():
  print("Usage: ./image-to-midi.py -i <source> -o <target> [-bd]")

# prints an error and exists after showing help()
def printError(errorMessage):
  message = "\033[1mError:\033[0m {}".format(errorMessage)
  print(message)
  help()
  sys.exit()

if __name__ == "__main__":
  main()