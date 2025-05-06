# YouTube Transcript Downloader

A Streamlit web application that allows you to download transcripts from YouTube videos.

## Features

- Extract transcripts from any YouTube video
- Download transcripts as text files
- Simple and user-friendly interface
- Works with both regular YouTube URLs and shortened youtu.be URLs

## How to Use

1. Enter a YouTube video URL in the input field
2. Click the "Get Transcript" button
3. View the transcript in the text area
4. Click "Download Transcript" to save the transcript as a text file

## Deployment

This application is designed to be deployed on Streamlit Cloud. To deploy:

1. Push this repository to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your GitHub repository
4. Select `app.py` as the main file
5. Deploy!

## Requirements

- Python 3.7+
- streamlit
- youtube-transcript-api

## Note

Some YouTube videos may not have available transcripts, or the transcripts may be disabled. In such cases, the application will display an error message. 