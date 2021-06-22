#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import stt, tts

class Chatbot:
    def __init__(self) -> None:
        self.listener = stt.Listener()
        self.speaker = tts.Speaker()

    def say(self, text, speed = 1):
        self.speaker.speak(text, speed)
        
    def listen(self):
        return self.listener.listens()

def main():
    pi = Chatbot()
    
    pi.say("hello", 1.3)
    try:
        while True:
            text = pi.listen()
            if text == "bye":
                pi.say("goodbye")
                exit()
            print(text)
    except KeyboardInterrupt:
         pass
            
if __name__ == "__main__":
    main()
        

