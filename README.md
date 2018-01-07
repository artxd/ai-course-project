# AI Course Project

Chatbot + speech synthesis.

## Requirements

### Dependencies
* `pip install google-cloud-speech`
* `pip install pyaudio`
* `pip install pynput`
* `pip install pyttsx3`

### Google Cloud
Required Google cloud account with google speech api enabled

Create new `service account key` at google cloud->Api & Services -> Credentials -> As JSON
Set python environment variable `GOOGLE_APPLICATION_CREDENTIALS=<downloaded json file name>.json`