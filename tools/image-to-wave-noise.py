#!/usr/bin/python3

# NAME
#   Image to Wave - Noise-Generator
#
# SYNOPSIS
#   ./image-to-wave-noise.py -o <target> [-d <duration>]
#
# DESCRIPTION
#   This script generates some noise based on the given duration. If no duration
#   is given the script defaults to five seconds.
#
# EXAMPLE:
#   ./image-to-wave-noise.py -o noise.wav -d 10
#
# OPTIONS
#   -o|--output-file Path to the output file
#   -d|--duration    Optional. The duration in seconds. Defaults to 5
#
# LEGAL NOTE
#   Written and maintained by Laura Herzog (laura-herzog@outlook.com)
#   Permission to copy and modify is granted under the AGPL license
#   Project Information: https://github.com/lauraherzog/universum-tonal/

import getopt, sys, os.path
import wave, struct, math, random

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "vho:d:", ["verbose", "output-file", "duration"])
  except getopt.GetoptError as err:
    help()
    sys.exit(2)

  verbose = False
  outputFile = None
  duration = 44100 * 5

  for operator, argument in opts:
    if operator in ("-h", "--help"):
      help()
      sys.exit()
    elif operator in ("-o", "--output-file"):
      outputFile = argument
      checkOutputFile(outputFile)
    elif operator in ("-d", "--duration"):
      duration = int(argument) * 44100
    elif operator in ("-v", "--verbose"):
      verbose = True
    else:
      assert False, "unhandled option"

  generateNoise(duration, outputFile)

def generateNoise(duration, outputFile):
  sampleRate = 44100
  frequency = 440

  waveFile = wave.open(outputFile,'w')
  waveFile.setnchannels(1) # mono
  waveFile.setsampwidth(2)
  waveFile.setframerate(sampleRate)

  for i in range(duration):
    value = random.randint(-32767, 32767)
    data = struct.pack('<h', value)
    waveFile.writeframesraw( data )
  waveFile.close()

# checks the ouputFile if there are any validation errors
def checkOutputFile(outputFile):
  if outputFile.lower().endswith(('.wav')) == False:
    printError("Filetype not supported. Use .wav")

  return True

# help, I need somebody, help!
def help():
  print("Usage: ./image-to-wave-noise.py -o <target> [-d <duration>]")

# prints an error and exists after showing help()
def printError(errorMessage):
  message = "\033[1mError:\033[0m {}".format(errorMessage)
  print(message)
  help()
  sys.exit()

if __name__ == "__main__":
  main()