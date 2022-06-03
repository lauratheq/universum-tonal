#!/usr/bin/python3

# NAME
#   Image to Wave - Pixel by Pixel
#
# SYNOPSIS
#   ./image-to-wave-pp.py -i <source> -o <target>
#
# DESCRIPTION
#   This script generates some noise based on the given image.
#
# EXAMPLE:
#   ./image-to-wave-pp.py -i sample-image.jpg -o sample-output.wav
#
# OPTIONS
#   -i|--input-file  path to the input file
#   -o|--output-file path to the output file
#
# LEGAL NOTE
#   Written and maintained by Laura Herzog (laura-herzog@outlook.com)
#   Permission to copy and modify is granted under the AGPL license
#   Project Information: https://github.com/lauraherzog/universum-tonal/

import getopt, sys, os.path
import cv2, colorsys
import wave, struct, math, random

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input-file", "output-file"])
  except getopt.GetoptError as err:
    help()
    sys.exit(2)

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
    else:
      assert False, "unhandled option"

  print("Step: convertImageToHSV")
  convertedData = convertImageToHSV(inputFile)
  print("Step: convertHSVtoWave")
  convertHSVtoWave(convertedData, outputFile, verbose)
  print("Done")

def convertImageToHSV(inputFile):
  imageObject = cv2.imread(inputFile)
  imageHeigth, imageWidth, imageChannel = imageObject.shape
  convertedData = {}
  # rows from left to right
  for x in range(0, imageWidth):
    for y in range(0, imageHeight):
      # get rgb value (they are switched in cv2) and convert them to hsv
      b, g, r = imageObject[x, y]
      (h, s, v) = convertToHSV(b, g, r)
      convertedData["{}-{}".format(x,y)] = (h, s, v)

  return convertedData

def convertHSVtoWave(data, outputFile, verbose):

  # prep the wave file
  waveFile = wave.open(outputFile,'w')
  waveFile.setnchannels(1) # mono
  waveFile.setsampwidth(2)
  waveFile.setframerate(44100)

  for coordinates in data:
    (h, s, v) = data[coordinates]

    # i just need the hue value and convert it to the frequency for that tick
    frequency = int((((h - 0) * (32767 - (-32767))) / (360 - 0)) + (-32767))
    tickData = struct.pack('<h', frequency)
    waveFile.writeframesraw( tickData )

  # finished writing
  waveFile.close()

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
  print("Usage: ./image-to-wave-pp.py -i <source> -o <target>")

# prints an error and exists after showing help()
def printError(errorMessage):
  message = "\033[1mError:\033[0m {}".format(errorMessage)
  print(message)
  help()
  sys.exit()

if __name__ == "__main__":
  main()