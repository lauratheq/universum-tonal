#!/usr/bin/python3

# NAME
#   Image to Wave - Chord
#
# SYNOPSIS
#   ./image-to-wave-chord.py -o <target>
#
# DESCRIPTION
#   This script generates a two second b minor chord as a test.
#
# EXAMPLE:
#   ./image-to-wave-chord.py -o chord.wav
#
# OPTIONS
#   -o|--output-file Path to the output file
#
# LEGAL NOTE
#   Written and maintained by Laura Herzog (laura-herzog@outlook.com)
#   Permission to copy and modify is granted under the AGPL license
#   Project Information: https://github.com/lauraherzog/universum-tonal/

import getopt, sys, os.path
import wave, struct, math

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "ho:", ["output-file"])
  except getopt.GetoptError as err:
    help()
    sys.exit(2)

  outputFile = None

  for operator, argument in opts:
    if operator in ("-h", "--help"):
      help()
      sys.exit()
    elif operator in ("-o", "--output-file"):
      outputFile = argument
      checkOutputFile(outputFile)
    else:
      assert False, "unhandled option"

  generateChord(outputFile)
  print("done")

def generateChord(outputFile):
  notes = [
    [246.94, 0.6],
    [146.83, 0.5],
    [185.00, 0.7] 
  ]

  sineList = generateSineWaves(notes)

  # prep the wave file
  waveFile = wave.open(outputFile,'w')
  waveFile.setnchannels(1) # mono
  waveFile.setsampwidth(2)
  waveFile.setframerate(44100)

  for sine in sineList:
    waveFile.writeframes(struct.pack('h', int(sine*8000/2)))

  # finished writing
  waveFile.close()

def generateSineWaves(notes):
  frameRate = 44100
  sineList=[]

  for x in range(88200):
    sineWave = 0
    for frequency, amplitude in notes:
      sineWave = sineWave + amplitude * math.sin(2*math.pi*frequency*(x/44100))
    sineList.append(sineWave)

  return sineList

# checks the ouputFile if there are any validation errors
def checkOutputFile(outputFile):
  if outputFile.lower().endswith(('.wav')) == False:
    printError("Filetype not supported. Use .wav")

  return True

# help, I need somebody, help!
def help():
  print("Usage: ./image-to-wave-chord.py -o <target>")

# prints an error and exists after showing help()
def printError(errorMessage):
  message = "\033[1mError:\033[0m {}".format(errorMessage)
  print(message)
  help()
  sys.exit()

if __name__ == "__main__":
  main()