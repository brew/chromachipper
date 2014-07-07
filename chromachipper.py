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


def make_chromachip_png(hex_list, width=600, height=600):
    """
    Use flat to generate and return png data with the colours specified in
    the hex_list.
    """

    doc_height = height
    doc_width = width

    d = document(doc_width, doc_height, 'pt')
    p = d.addpage()
    chip_width = doc_width / len(hex_list)
    for i, hex in enumerate(hex_list):
        chip_rgb = rgb(*hex_to_rgb(hex))
        colour_thing = shape().nostroke().fill(chip_rgb)
        p.place(colour_thing.rect(i * chip_width, 0, chip_width, doc_height))
    return p.image(kind='rgb').png()


def get_colours_from_message(message):
    """
    Harvest hex colour values of 3 or 6 characters in length from the message
    string and return a normalized list.

    >>> get_colours_from_message("#0ef")
    ['#00eeff']

    >>> get_colours_from_message("#663399")
    ['#663399']

    >>> get_colours_from_message("Colour in a #ff0000 mixed message")
    ['#ff0000']

    >>> get_colours_from_message("#d00#bar")
    ['#dd0000']

    >>> get_colours_from_message("Muliple colours! #0ff, #ff000 #00ff00. #d00#bar")
    ['#00ffff', '#00ff00', '#dd0000']

    >>> get_colours_from_message("No colours in this message :(")
    []
    """
    hexs = re.findall(r'#[0-9A-F]{6}|#[0-9A-F]{3}\b', message, re.I)
    normalized_hexs = [normalize_hex(hex) for hex in hexs]
    return normalized_hexs


if __name__ == '__main__':
    app.run(debug=True)
