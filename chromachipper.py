from __future__ import division
import re
import StringIO

from webcolors import hex_to_rgb, normalize_hex
from flat import rgb, shape, document
from flask import Flask, send_file, request

app = Flask(__name__)


@app.route('/test')
def test_chromachipper():
    string_buffer = StringIO.StringIO()
    # string_buffer.write(make_chromachip_png(['#ff0000', '#00ff00', '#0000ff']))
    string_buffer.write(make_chromachip_png(['#F41C54', '#FF9F00', '#FBD506', '#A8BF12', '#00AAB5'], width=1500, height=500))
    string_buffer.seek(0)
    return send_file(string_buffer, mimetype='image/png')


@app.route('/test_message')
def test_chromachipper_with_message():
    """
    A test view that expects a url escaped message containing hex colour
    values:

    /test_message?msg=My%20message%23663399

    '#' characters are escaped as %23
    """
    msg = request.args.get('msg', None)
    if msg:
        colours = get_colours_from_message(msg)
        if colours:
            string_buffer = StringIO.StringIO()
            string_buffer.write(make_chromachip_png(colours))
            string_buffer.seek(0)
            return send_file(string_buffer, mimetype='image/png')
    return "No colours in the message :(", 400  # Bad Request status


def make_chromachip_png(colour_list, width=600, height=600):
    """
    Use flat to generate and return png data with the colours specified in
    the colour_list.
    """

    doc_height = height
    doc_width = width

    d = document(doc_width, doc_height, 'pt')
    p = d.addpage()
    chip_height = doc_height / len(colour_list)
    for i, row in enumerate(colour_list):
        chip_width = doc_width / len(row)
        chip_y = i * chip_height
        for j, colour in enumerate(row):
            chip_rgb = rgb(*hex_to_rgb(colour))
            colour_thing = shape().nostroke().fill(chip_rgb)
            p.place(colour_thing.rect(j * chip_width, chip_y, chip_width, chip_height))
    return p.image(kind='rgb').png()


def get_colours_from_message(message, reg=re.compile(r'#[0-9A-F]{6}|#[0-9A-F]{3}\b', re.I)):
    """
    Harvest hex colour values of 3 or 6 characters in length from the message
    string and return a normalized list.
    """

    # Replace all '0x' with '#'
    message = message.replace('0x', '#')
    lines = message.split('\n')
    normalized_colours = []
    for line in lines:
        colours = reg.findall(line)
        if colours:
            normalized_colours.append([normalize_hex(colour) for colour in colours])
    return normalized_colours


if __name__ == '__main__':
    app.run(debug=True)
