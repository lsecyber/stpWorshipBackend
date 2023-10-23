import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys, os
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)


def update_current_info(section = '', song_name = '', copyright = '', ccliSongNumber = '', lyrics = ''):
    with open('static/info/currentinfo.json', 'r') as f:
        # Check if the file is empty
        if os.stat('static/info/currentinfo.json').st_size == 0:
            # If it's empty, write an empty JSON object to it
            with open('static/info/currentinfo.json', 'w') as f_new:
                json.dump({}, f_new)

        # Seek to the beginning of the file in case it was written to
        f.seek(0)

        # Parse the JSON from the file
        current_info = json.load(f)
        f.close()

    if section != '':
        current_info['section'] = section
    if song_name != '':
        current_info['song_name'] = song_name
    if copyright != '':
        current_info['copyright'] = copyright
    if ccliSongNumber != '':
        current_info['ccliSongNumber'] = ccliSongNumber

    current_info['lyrics'] = lyrics

    # Write the json to the file
    with open('static/info/currentinfo.json', 'w') as f:
        json.dump(current_info, f)
        f.close()


def get_lyrics_for_song_and_section(song_name, section):
    with open('static/info/' + song_name + '--songinfo.json', 'r') as f:
        # Parse the JSON from the file
        song_info = json.load(f)
        f.close()
    section_options = song_info['lyrics'].keys()

    if section in section_options:
        return song_info['lyrics'][section]
    else:
        for section_choice in section_options:
            if section.lower() in section_choice.lower() or section_choice.lower() in section.lower():
                return song_info['lyrics'][section_choice]
        print('returning blank')
        return ''


def get_current_info():
    with open('static/info/currentinfo.json', 'r') as f:
        # Parse the JSON from the file
        current_info = json.load(f)
        f.close()
    return current_info


# Serve files in the current directory and subdirectories
@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)


@socketio.on('connect')
def handle_connect():
    print('A user connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('User disconnected')


# Open a WebSocket for sending notifications
@socketio.on('notification')
def handle_notification(data):
    print(f"Received notification: {data}")
    # Add any additional logic to handle the notification data


# Check if a GET request to a certain URL performs special actions based on query parameters
@app.route('/updateinfo', methods=['GET'])
def special_action():
    query_params = request.args
    print(query_params)
    section = query_params['section'] if 'section' in query_params else get_current_info()['section']
    song_name = query_params['song_name'] if 'song_name' in query_params else get_current_info()['song_name']
    copyright = query_params['copyright'] if 'copyright' in query_params else ''
    ccliSongNumber = query_params['ccliSongNumber'] if 'ccliSongNumber' in query_params else ''
    lyrics = get_lyrics_for_song_and_section(song_name, section)

    update_current_info(section, song_name, copyright, ccliSongNumber, lyrics)
    print('updated')

    if copyright == '' or ccliSongNumber == '':
        with open('static/info/' + song_name + '--songinfo.json', 'r') as f:
            # Parse the JSON from the file
            song_info = json.load(f)
            f.close()
        update_current_info(copyright=song_info['copyright'], ccliSongNumber=song_info['ccliSongNumber'], lyrics=lyrics)

    socketio.emit('update', get_current_info())

    return "{'status': 'success'}"


if __name__ == '__main__':
    # Start the Flask application with WebSocket support
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5111, host='0.0.0.0')


"""
class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        # Parse the URL and extract query parameters
        url_parts = urlparse(self.path)
        if url_parts.path == '/updateinfo':
            query_params = parse_qs(url_parts.query)

            section = query_params['section'][0] if 'section' in query_params else get_current_info()['section']
            song_name = query_params['song_name'][0] if 'song_name' in query_params else get_current_info()['song_name']
            copyright = query_params['copyright'][0] if 'copyright' in query_params else ''
            ccliSongNumber = query_params['ccliSongNumber'][0] if 'ccliSongNumber' in query_params else ''
            lyrics = get_lyrics_for_song_and_section(song_name, section)

            update_current_info(section, song_name, copyright, ccliSongNumber, lyrics)
            print('updated')
            self.send_response(200, '{status: "success"}')
        else:
            # Call the parent class method to handle the request as usual
            super().do_GET()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5111
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"Serving on port {port}")
    httpd.serve_forever()"""
