import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
import openai
import tkinter as tk

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize text-to-speech
engine = pyttsx3.init()

# OpenAI API key (replace with your own key)
openai.api_key = 'your_own_api_key'

# Weather API key (replace with your own key)
weather_api_key ='http://api.openweathermap.org/data/2.5/forecast?id=524901&appid={API key}'

# Email configuration
smtp_server = 'your_smtp_server'
smtp_port = 587
email_address = 'your_email@example.com'
email_password = 'your_email_password'

# Create the main application window
app = tk.Tk()
app.title("Virtual Assistant")

# Create a text box for displaying responses
response_text = tk.Text(app, height=10, width=40)
response_text.pack()


def speak(text):
    engine.say(text)
    engine.runAndWait()
    response_text.insert(tk.END, text + "\n")


def process_command():
    command = command_entry.get()
    command_entry.delete(0, tk.END)

    if "open Google" in command:
        webbrowser.open("https://www.google.com")

    elif "open YouTube" in command:
        webbrowser.open("https://www.youtube.com")

    elif "show date" in command:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {current_date}")

    elif "show time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {current_time}")

    elif "send email" in command:
        speak("Who is the recipient?")
        recipient = listen_for_command()
        speak("What's the subject?")
        subject = listen_for_command()

        # Create an email message
        message = MIMEMultipart()
        message['From'] = email_address
        message['To'] = recipient
        message['Subject'] = subject

        # Attach a file (e.g., 'attachment.txt')
        attachment_path = 'path_to_attachment.txt'
        with open(attachment_path, 'rb') as attachment:
            part = MIMEApplication(attachment.read(), Name='attachment.txt')
        part['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
        message.attach(part)

        # Send the email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient, message.as_string())
            server.quit()
            speak("Email sent successfully.")
        except Exception as e:
            speak(f"Sorry, there was an error sending the email: {str(e)}")

    elif "weather" in command:
        speak("Sure, please provide your location.")
        location = listen_for_command()
        weather_data = get_weather(location)
        speak(weather_data)

    elif "question" in command:
        speak("What's your question?")
        question = listen_for_command()
        answer = get_answer(question)
        speak("The answer is: " + answer)

    elif "exit" in command:
        speak("Goodbye!")
        app.quit()

    else:
        speak("Sorry, I didn't understand the command. Please try again.")


def listen_for_command():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("You said: " + command)
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return ""


def get_weather(location):
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}"
        response = requests.get(weather_url)
        data = response.json()
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        return f"The weather in {location} is {description} with a temperature of {temperature} degrees Celsius."
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return "Sorry, I couldn't fetch the weather data."


def get_answer(question):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=question,
            max_tokens=50,
            n=1,
            stop=None,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error fetching answer: {str(e)}")
        return "Sorry, I couldn't find an answer."


# Create an input field for user commands
command_entry = tk.Entry(app, width=40)
command_entry.pack()

# Create a button to submit commands
submit_button = tk.Button(app, text="Submit", command=process_command)
submit_button.pack()

if __name__ == "__main__":
    speak("Hello! How can I assist you today?")
    app.mainloop()
