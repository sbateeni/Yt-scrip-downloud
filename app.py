from flask import Flask, render_template, request, jsonify, send_file
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import time
import io
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def extract_video_id(url):
    # Try multiple methods to extract video ID
    try:
        # Method 1: Using regex
        pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        # Method 2: Using URL parsing
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['youtube.com', 'www.youtube.com', 'youtu.be']:
            if parsed_url.hostname == 'youtu.be':
                return parsed_url.path[1:]
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
    except:
        pass
    return None

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
                
                # Try multiple languages in order of preference
                languages = ['en', 'ar', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
                
                # First try manual transcripts
                for lang in languages:
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        return format_transcript(transcript.fetch())
                    except:
                        continue
                
                # If no manual transcripts, try generated ones
                for lang in languages:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        return format_transcript(transcript.fetch())
                    except:
                        continue
                
                # If still no transcript, try to get any available transcript
                try:
                    transcript = transcript_list.find_transcript(languages)
                    return format_transcript(transcript.fetch())
                except:
                    pass
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Increased wait time between retries
                    continue
                return f"Error: Could not retrieve transcript. {str(e)}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # Increased wait time between retries
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
    try:
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
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/download/<video_id>', methods=['GET'])
def download_transcript(video_id):
    try:
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
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 