from flask import Flask, render_template, request, jsonify, send_file
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import time
import io

app = Flask(__name__)

def extract_video_id(url):
    # Regular expression to match YouTube video IDs
    pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            # First try to get the transcript in the original language
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return format_transcript(transcript_list)
        except (TranscriptsDisabled, NoTranscriptFound):
            try:
                # If original language fails, try to get available transcripts
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Try to get English transcript first
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    return format_transcript(transcript.fetch())
                except:
                    # If English is not available, try other languages
                    try:
                        # Try to get any available manual transcript
                        transcript = transcript_list.find_manually_created_transcript(['en', 'ar', 'fr', 'es', 'de'])
                        return format_transcript(transcript.fetch())
                    except:
                        # If no manual transcript, try generated ones
                        transcript = transcript_list.find_generated_transcript(['en', 'ar', 'fr', 'es', 'de'])
                        return format_transcript(transcript.fetch())
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retrying
                    continue
                return f"Error: Could not retrieve transcript. {str(e)}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retrying
                continue
            return f"Error: {str(e)}"
    
    return "Error: Maximum retry attempts reached. Please try again later."

def format_transcript(transcript_list):
    formatted_transcript = ""
    for entry in transcript_list:
        formatted_transcript += entry['text'] + " "
    return formatted_transcript.strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript_route():
    data = request.get_json()
    youtube_url = data.get('url')
    
    if not youtube_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    transcript = get_transcript(video_id)
    if transcript.startswith("Error"):
        return jsonify({'error': transcript}), 400
    
    return jsonify({
        'transcript': transcript,
        'video_id': video_id
    })

@app.route('/download/<video_id>', methods=['GET'])
def download_transcript(video_id):
    transcript = get_transcript(video_id)
    if transcript.startswith("Error"):
        return jsonify({'error': transcript}), 400
    
    # Create a file-like object in memory
    file_obj = io.BytesIO(transcript.encode())
    file_obj.seek(0)
    
    return send_file(
        file_obj,
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'transcript_{video_id}.txt'
    )

if __name__ == '__main__':
    app.run(debug=True) 