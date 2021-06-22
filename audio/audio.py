#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
from threading import Thread

import chatbot

import pvporcupine
import pyaudio

from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

class WakeUp(Thread):
	
	def __init__(
		self, 
		library_path,
		model_path,
		keyword_paths,
		sensitivities):

		"""
		Constructor.
		
		:param library_path: Absolute path to Porcupine's dynamic library.
		:param model_path: Absolute path to the file containing model parameters.
		:param keyword_paths: Absolute paths to keyword model files.
		:param sensitivities: Sensitivities for detecting keywords. Each value should be a number within [0, 1]. A
		higher sensitivity results in fewer misses at the cost of increasing the false alarm rate. If not set 0.5 will be used.
		"""
		super(WakeUp, self).__init__()
	
		self._library_path = library_path
		self._model_path = model_path
		self._keyword_paths = keyword_paths
		self._sensitivities = sensitivities
	
	def run(self):
		"""
		Creates an input audio stream, instantiates an instance of Porcupine object, and monitors the audio stream for
		occurrences of the wake word(s). It prints the time of detection for each occurrence and the wake word.
		"""

		keywords = list()
		for x in self._keyword_paths:
			keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
			if len(keyword_phrase_part) > 6:
				keywords.append(' '.join(keyword_phrase_part[0:-6]))
			else:
				keywords.append(keyword_phrase_part[0])
		porcupine = None
		pa = None
		audio_stream = None
        
		try:
			porcupine = pvporcupine.create(
				library_path=self._library_path,
				model_path=self._model_path,
				keyword_paths=self._keyword_paths,
				sensitivities=self._sensitivities)

			with noalsaerr():
				pa = pyaudio.PyAudio()

			audio_stream = pa.open(
				rate=porcupine.sample_rate,
				channels=1,
				format=pyaudio.paInt16,
				input=True,
				frames_per_buffer=porcupine.frame_length,
				input_device_index=1)
				
			pi = chatbot.Chatbot()

			print('Listening {')
			for keyword, sensitivity in zip(keywords, self._sensitivities):
				print('  %s (%.2f)' % (keyword, sensitivity))
			print('}')
			
			
			while True:
				pcm = audio_stream.read(porcupine.frame_length)
				pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
				
				result = porcupine.process(pcm)
		
				if result >= 0:
					print('Detected %s' % keywords[result])
					pi.say("Hello!",1.3)
					#audio_stream.stop_stream()
					audio_stream.close()
					while True:
						text = pi.listen()
						print(text)
						if text == "bye":
							pi.say("goodbye")
							break
						pi.say(text)
					audio_stream = pa.open(
					rate=porcupine.sample_rate,
					channels=1,
					format=pyaudio.paInt16,
					input=True,
					frames_per_buffer=porcupine.frame_length,
					input_device_index=1)
		
		except KeyboardInterrupt:
			print('Stopping ...')
				
		finally:
			if porcupine is not None:
				porcupine.delete()

			if audio_stream is not None:
				audio_stream.close()

			if pa is not None:
				pa.terminate()

def main():
	#words = input("Keywords: ").split(' ')
	words = ['blueberry']
	WakeUp(library_path=pvporcupine.LIBRARY_PATH,
	model_path=pvporcupine.MODEL_PATH,
	keyword_paths=[pvporcupine.KEYWORD_PATHS[x] for x in words],
	sensitivities=[0.6] * len(words)).run()

if __name__ == '__main__':
	main()
