import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from transcribe import transcribe_audio
from emailing import email
from datetime import datetime
app = Flask(__name__)

CORS(app)

AUDIO_UPLOAD_FOLDER = os.path.join(os.getcwd(),'audios')
TRANSCRIPTS_UPLOAD_FOLDER = os.path.join(os.getcwd(),'transcripts')

if os.path.exists(AUDIO_UPLOAD_FOLDER) == False:
    os.mkdir(AUDIO_UPLOAD_FOLDER)

if os.path.exists(TRANSCRIPTS_UPLOAD_FOLDER) == False:
    os.mkdir(TRANSCRIPTS_UPLOAD_FOLDER)


@app.route('/', methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route('/upload_static_file', methods=["GET","POST"])
def upload_static_file():
    audio_file = request.files["static_file"]
    if audio_file:

        audio_location = os.path.join(
            AUDIO_UPLOAD_FOLDER,
            audio_file.filename
        )
        audio_name = audio_file.filename
        audio_file.save(audio_location)

        response = transcribe_audio('tpus-302411',audio_name, audio_location,'en-US')
        filename = f'Transcription_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'
        currfile = os.path.join(TRANSCRIPTS_UPLOAD_FOLDER,filename)
        
        with open(currfile,'w+') as f:
            f.write(f'{response}\n\nDURATION TAKEN(LOCAL MACHINE): {response}\n')

        if email(["bhuvana.kundumani@gmail.com"], currfile, filename):
            os.remove(audio_location)
            os.remove(currfile)
            
        resp = {"success": True, 
                "response": "File processed!",
                "text": response,
                "path":currfile}
        return jsonify(resp), 200

if __name__=="__main__":
    app.run(debug=True)