import speech_recognition as sr

recognizer = sr.Recognizer()

def capture_voice_input():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    return audio

def convert_voice_to_text(audio):
    try:
        text = recognizer.recognize_google(audio)
        print(text)
    except sr.UnknownValueError:
        text = ""
        print("Not understood")
    except sr.RequestError as e:
        text = ""
        print("Error; {0}".format(e))
    return text

def process_voice_command(text):
    if "left" in text.lower():
        print("Left")
    elif "Right" in text.lower():
        print("Right")
        return True
    else:
        print("Command Not understood. Try again.")
    return False

def main():
    end_program = False
    while not end_program:
        audio = capture_voice_input()
        text = convert_voice_to_text(audio)
        end_program = process_voice_command(text)

if __name__ == "__main__":
    main()