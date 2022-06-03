#!/usr/bin/python3

# NAME
#   Image to wave - a converter
#
# SYNOPSIS
#   ./image-to-wave.py -i <source> -o <target>
#
# DESCRIPTION
#   This script converts images (currently jpg files) to wave files. It reads
#   images from left to right row by row and decides what octave, frequency and
#   velocity a pixel has - based on the properties of the HSL color system.
#
# EXAMPLE:
#   ./image-to-wave.py -i sample.jpg -o sample.wav
#
# OPTIONS
#   -i|--input-file       path to the input file
#   -o|--output-file      path to the output file
#   -s|--sample-rate      the length of one row
#   -f|--ignore-frequency frequencies till this will be ignored
#
# LEGAL NOTE
#   Written and maintained by Laura Herzog (laura-herzog@outlook.com)
#   Permission to copy and modify is granted under the AGPL license
#   Project Information: https://github.com/lauraherzog/universum-tonal/

import getopt, sys, os.path
import cv2, colorsys
import wave, struct, math, random

frameRate = 44100
octaveFrequencies = [
  [16.35, 30.87],
  [32.70, 61.74],
  [65.41, 123.47],
  [130.81, 246.94],
  [261.63, 493.88],
  [523.25, 987.77],
  [1046.50, 1975.53],
  [2093.00, 3951.07],
  [4186.01,  7902.13]
]

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:f:s:", ["help", "input-file", "output-file", "ignore-frequency", "sample-rate"])
  except getopt.GetoptError as err:
    help()
    sys.exit(2)

  lowestFrequency = 16.35
  sampleRate = 2048
  inputFile = None
  outputFile = None

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
    elif operator in ("-f", "--ignore-frequency"):
      lowestFrequency = float(argument)
    elif operator in ("-s", "--sample-rate"):
      sampleRate = int(argument)
    else:
      assert False, "unhandled option"

  print("Step: convertImageToData")
  convertedData = convertImageToData(inputFile)
  print("Step: convertDataToWave")
  convertDataToWave(convertedData, outputFile, sampleRate, lowestFrequency)

def convertDataToWave(data, outputFile, sampleRate, lowestFrequency):

  # prep the wave file
  waveFile = wave.open(outputFile,'w')
  waveFile.setnchannels(1) # mono
  waveFile.setsampwidth(2)
  waveFile.setframerate(frameRate)

  i = 0
  for notes in data:
    sineList = []
    print("Generating sine waves for row {}".format(i))
    sineList = generateSineWaves(notes, sampleRate, lowestFrequency)
    for sine in sineList:
      waveFile.writeframes(struct.pack('h', int(sine*250/2)))
    i = i + 1

  # finished writing
  waveFile.close()

def generateSineWaves(notes, sampleRate, lowestFrequency):
  sineList=[]

  for x in range(sampleRate):
    sineWave = 0
    for frequency, amplitude in notes:
      if frequency < lowestFrequency:
        continue
      sineWave = sineWave + amplitude * math.sin(2*math.pi*frequency*(x/frameRate))
    sineList.append(sineWave)

  return sineList

def convertImageToData(inputFile):
  imageObject = cv2.imread(inputFile)
  imageHeigth, imageWidth, imageChannel = imageObject.shape
  
  rows = []
  # rows from left to right
  for x in range(0, imageWidth):
    rowData = []
    for y in range(0, imageHeigth):

      # get rgb value (they are switched in cv2) and convert them to hsv
      b, g, r = imageObject[x, y]
      (h, s, v) = convertToHSV(b, g, r)

      octave = int((((v - 0) * (8 - (0))) / (100 - 0)) + (0))
      frequency = int((((h - 0) * (octaveFrequencies[octave][1] - (octaveFrequencies[octave][0]))) / (360 - 0)) + (octaveFrequencies[octave][0]))
      amplitude = (((s - 0) * (1 - (0))) / (100 - 0)) + (0)

      rowData.append((frequency, amplitude))
    rows.append(rowData)

  return rows

def convertToHSV(b, g, r):
  (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
  (h, s, v) = (int(h*360), int(s*100), int(v*100))
  return (h, s, v)

# checks the inputFile if there are any validation errors
def checkInputFile(inputFile):
  if os.path.exists(inputFile) == False:
    printError("File not found")

  if inputFile.lower().endswith(('.png', '.jpg', '.jpeg')) == False:
    printError("Filetype not supported. Use .jpg and .jpeg")

  return True

# checks the ouputFile if there are any validation errors
def checkOutputFile(outputFile):
  if outputFile.lower().endswith(('.wav')) == False:
    printError("Filetype not supported. Use .wav")

  return True

# help, I need somebody, help!
def help():
  print("Usage: ./image-to-wave-pf.py -i <source> -o <target>")

# prints an error and exists after showing help()
def printError(errorMessage):
  message = "\033[1mError:\033[0m {}".format(errorMessage)
  print(message)
  help()
  sys.exit()

if __name__ == "__main__":
  main()