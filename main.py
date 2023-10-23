import json
import os
import re

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Create a list to store the extracted text from each page
    extracted_text = []

    # Iterate through each page and extract text
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text().split('\n')  # Split text into lines
        extracted_text.append(text)

    # Close the PDF
    pdf_document.close()

    return extracted_text


def save_text_to_json(data, output_json_path):
    # Write the dictionary to a JSON file
    with open(output_json_path.replace('/static/pdfs/', '/static/info/'), 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

    print(f'Text extracted and saved to: {output_json_path}')


def filter_caps_lines(text_list):
    # Filter out lines that are not completely in uppercase or match specific patterns for each page
    filtered_text = [
        [
            line
            for line in lines
            if line.strip().isupper()
               and re.match(r'\b(VERSE|TAG|CHORUS|INTRO|ENDING|INTERLUDE|INSTRUMENTAL|BRIDGE|'
                            r'PRE(?:-|\s)?CHORUS|OUTRO|REFRAIN|VAMP|TURNAROUND)\s*\d*\b', line.strip())
        ]
        for lines in text_list
    ]

    return filtered_text


def parse_song_lyrics(song_name):
    with open('static/txts/' + song_name + '-lyrics.txt', 'r') as f:
        lines = f.readlines()
        f.close()

    section_title_pattern = r'\b(VERSE|TAG|CHORUS|INTRO|ENDING|INTERLUDE|INSTRUMENTAL|BRIDGE|' \
                            r'PRE(?:-|\s)?CHORUS|OUTRO|REFRAIN|VAMP|TURNAROUND)\s*\d*\b'
    previous_line_was_break = False
    lines_are_info_lines = False
    current_section = None
    info_types = ['artist', 'ccliSongNumber', 'copyright', 'na', 'na']

    info = {
        'title': song_name,
        'sections': [],
        'lyrics': {},
    }

    for line in lines[1:]:
        print('line: ', line)
        if line == '\n':
            previous_line_was_break = True
            current_section = None
            continue

        if previous_line_was_break:
            if re.match(section_title_pattern, line.strip().replace('\n', '').upper()):
                info['sections'].append(line.strip())
                current_section = line.strip()
                previous_line_was_break = False
                continue
            else:
                lines_are_info_lines = True
                current_section = 0

        if lines_are_info_lines and info_types[current_section] != 'na':
            if current_section == 1:
                info[info_types[current_section]] = line.strip().replace("CCLI Song #", '')
            else:
                info[info_types[current_section]] = line.strip()

            current_section += 1

        elif current_section is not None and not lines_are_info_lines:
            if current_section not in info['lyrics']:
                info['lyrics'][current_section] = ''
            info['lyrics'][current_section] += line.strip() + '\n'

        previous_line_was_break = False
        continue
    return info


def process_pdf(pdf_path):
    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(pdf_path)

    # Filter out lines that are not completely in uppercase
    sections_by_page_raw = filter_caps_lines(extracted_text)

    sections_by_page = {f'Page {i + 1}': lines for i, lines in enumerate(sections_by_page_raw)}

    # The regex pattern
    chords_and_key_pattern = r'-chords-(malekey|femalekey)(?:\.pdf|$)'

    # Applying the regex
    match = re.search(chords_and_key_pattern, pdf_path)

    # Extracting the key if there is a match
    if match:
        key = match.group(1)
        print('key is: ', key)
    else:
        key = None

    info = parse_song_lyrics(re.sub(chords_and_key_pattern, '', pdf_path.split('/')[-1]))
    info['sections_by_page'] = sections_by_page
    #info['key'] = key  # Key is not relevant because there are two versions of the pdf

    # Specify the path for the output text file
    output_json_path = re.sub(chords_and_key_pattern, r'--songinfo.json', pdf_path)
    print('output path: ', output_json_path)
    print('final info: ', info)

    # Save the filtered text to a text file
    save_text_to_json(info, output_json_path)

    return info['title']


def find_and_process_pdfs(directory_path, process_function):
    # Get the current working directory
    current_directory = os.getcwd()

    # Combine the current directory with the specified subdirectory
    target_directory = os.path.join(current_directory, directory_path)

    # Check if the target directory exists
    if not os.path.exists(target_directory):
        print(f"The directory '{target_directory}' does not exist.")
        return

    song_names = []
    # Iterate over the files in the directory
    for filename in os.listdir(target_directory):
        # Check if the file is a PDF
        if filename.lower().endswith(".pdf") and '-femalekey' not in filename.lower():  # Filter out female key ones,
            # so it's not processed twice

            # Get the full path of the PDF file
            pdf_path = os.path.join(target_directory, filename)

            # Call the provided function with the PDF path
            song_names.append(process_function(pdf_path))
    return song_names


if __name__ == '__main__':
    song_names = find_and_process_pdfs('static/pdfs', process_pdf)

    with open('static/info/songlist.json', 'w') as f:
        json.dump(song_names, f, indent=2)
        f.close()
