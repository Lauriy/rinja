#!/usr/bin/env python

# Taken from https://github.com/Kagami/chaptcha

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import errno
import os
import sys
import threading
import time
import traceback

import bs4
import cv2
import numpy as np
import requests
from pyfann import libfann

__title__ = 'chaptcha.py'
__version__ = '0.0.1'
__license__ = 'CC0'
__doc__ = 'asd'

NUM_CHARS = 4
CAPTCHA_WIDTH = 200
CAPTCHA_HEIGHT = 50
CH_WIDTH = 20
CH_HEIGHT = 45
LINE_THICK = 1
# See <https://github.com/numpy/numpy/issues/7112>.
_CONSTANT = str('constant')


def check_image(img):
    assert img is not None, 'cannot read image'
    assert img.shape == (CAPTCHA_HEIGHT, CAPTCHA_WIDTH), 'bad image dimensions'


def get_image(fpath):
    img = cv2.imread(fpath, 0)
    check_image(img)

    return img


def decode_image(data):
    img = cv2.imdecode(data, 0)
    check_image(img)

    return img


def get_network(fpath):
    ann = libfann.neural_net()
    assert ann.create_from_file(fpath), 'cannot init network'

    return ann


def get_ch_data(img):
    data = img.flatten() & 1
    assert len(data) == CH_WIDTH * CH_HEIGHT, 'bad data size'

    return data


POSSIBLE_SYMBOLS = 'abcdefghijklmnopqrstuvwxyz0123456789'


def make_ann_output(symbol):
    out = [0.0] * len(POSSIBLE_SYMBOLS)
    out[POSSIBLE_SYMBOLS.index(symbol)] = 1.0

    return out


def get_match(answer1, answer2):
    return sum(dg1 == dg2 for (dg1, dg2) in zip(answer1, answer2))


def report(line='', progress=False):
    if progress:
        line = '\033[1A\033[K' + line
    line += '\n'
    sys.stderr.write(line)


def mkdirp(dpath):
    try:
        os.makedirs(dpath)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def _denoise(img):
    img = cv2.fastNlMeansDenoising(img, None, 85, 5, 21)
    img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)[1]

    return img


def _get_lines(img):
    lines = cv2.HoughLinesP(img, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=100)
    if lines is None:
        lines = []

    return [line[0] for line in lines]


def _preprocess(img):
    img = img.copy()
    img = _denoise(img)
    lines = _get_lines(img)
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(img, (x1, y1), (x2, y2), 0, LINE_THICK)

    return img


def segment(img):
    def find_filled_row(rows):
        for i, row in enumerate(rows):
            dots = np.sum(row) // 255
            if dots >= DOTS_THRESHOLD:
                return i
        assert False, 'cannot find filled row'

    def pad_ch(ch):
        pad_w = CH_WIDTH - len(ch.T)
        assert pad_w >= 0, 'bad char width'
        pad_w1 = pad_w // 2
        pad_w2 = pad_w - pad_w1
        pad_h = CH_HEIGHT - len(ch)
        assert pad_h >= 0, 'bad char height'
        pad_h1 = pad_h // 2
        pad_h2 = pad_h - pad_h1

        return np.pad(ch, ((pad_h1, pad_h2), (pad_w1, pad_w2)), _CONSTANT)

    BLANK_THRESHHOLD = 1
    DOTS_THRESHOLD = 5
    CH_MIN_WIDTH = 7

    # Search blank intervals.
    img = _preprocess(img)
    dots_per_col = np.apply_along_axis(lambda row: np.sum(row) // 255, 0, img)
    blanks = []
    was_blank = False
    first_ch_x = None
    prev_x = 0
    x = 0
    while x < CAPTCHA_WIDTH:
        if dots_per_col[x] >= DOTS_THRESHOLD:
            if first_ch_x is None:
                first_ch_x = x
            if was_blank:
                # Skip first blank.
                if prev_x:
                    blanks.append((prev_x, x))
                # Don't allow too tight chars.
                x += CH_MIN_WIDTH
                was_blank = False
        elif not was_blank:
            was_blank = True
            prev_x = x
        x += 1
    print (first_ch_x)
    blanks = [b for b in blanks if b[1] - b[0] >= BLANK_THRESHHOLD]
    blanks = sorted(blanks, key=lambda b: b[1] - b[0], reverse=True)[:5]
    # No more than one glued pair currently.
    # assert len(blanks) >= 4, 'bad number of blanks'
    blanks = sorted(blanks, key=lambda b: b[0])
    # Add last (imaginary) blank to simplify following loop.
    blanks.append((prev_x if was_blank else CAPTCHA_WIDTH, 0))
    print (blanks)

    # blanks = [(87, 89), (106, 108), (116, 118), (133, 135)]
    # first_ch_x = 67

    # Get chars.
    chars = []
    x1 = first_ch_x
    widest = 0, 0
    for i, (x2, next_x1) in enumerate(blanks):
        width = x2 - x1
        # Don't allow more than CH_WIDTH * 2.
        extra_w = width - CH_WIDTH * 2
        extra_w1 = extra_w // 2
        extra_w2 = extra_w - extra_w1
        x1 = max(x1, x1 + extra_w1)
        x2 = min(x2, x2 - extra_w2)
        ch = img[:CAPTCHA_HEIGHT, x1:x2]

        y2 = CAPTCHA_HEIGHT - find_filled_row(ch[::-1])
        y1 = max(0, y2 - CH_HEIGHT)
        ch = ch[y1:y2]

        chars.append(ch)
        if width > widest[0]:
            widest = x2 - x1, i
        x1 = next_x1

    # Fit chars into boxes.
    chars2 = []
    for i, ch in enumerate(chars):
        widest_w, widest_i = widest
        # Split glued chars.
        if len(chars) < NUM_CHARS and i == widest_i:
            ch1 = ch[:, 0:widest_w // 2]
            ch2 = ch[:, widest_w // 2:widest_w]
            chars2.append(pad_ch(ch1))
            chars2.append(pad_ch(ch2))
        else:
            ch = ch[:, 0:CH_WIDTH]
            chars2.append(pad_ch(ch))

    assert len(chars2) == NUM_CHARS, 'bad number of chars'

    return chars2


def vis_all_lines(fpath):
    def to_rgb(img):
        return cv2.merge([img] * 3)

    HIGH_COLOR = (0, 255, 0)

    orig = get_image(fpath)
    with_lines = to_rgb(orig.copy())
    for line in _get_lines(orig.copy()):
        x1, y1, x2, y2 = line
        cv2.line(with_lines, (x1, y1), (x2, y2), HIGH_COLOR, LINE_THICK)

    res = np.concatenate((
        to_rgb(orig),
        with_lines,
    ))
    cv2.imshow('opencv-result', res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def denoise_all(captchas_dir):
    def to_rgb(img):
        return cv2.merge([img] * 3)

    captchas_dir = os.path.abspath(captchas_dir)
    captchas = os.listdir(captchas_dir)
    for i, name in enumerate(captchas):
        fpath = os.path.join(captchas_dir, name)
        print(fpath)
        orig = get_image(fpath)
        #denoised = _denoise(orig.copy())
        preprocessed = _preprocess(orig)
        res = np.concatenate((
            # to_rgb(orig),
            # to_rgb(denoised),
            to_rgb(preprocessed),
        ))
        print(captchas_dir + '\\..\\denoised\\' + name)
        cv2.imwrite(captchas_dir + '\\..\\denoised\\' + name, res)
        time.sleep(0.5)


def vis(fpath):
    def to_rgb(img):
        return cv2.merge([img] * 3)

    BOX_W = CAPTCHA_WIDTH // NUM_CHARS
    PAD_W = (BOX_W - CH_WIDTH) // 2
    PAD_H = (CAPTCHA_HEIGHT - CH_HEIGHT) // 2
    EXTRA_PAD_W = (CAPTCHA_WIDTH % NUM_CHARS) // 2
    HIGH_COLOR = (0, 255, 0)

    # Real result used for OCR.
    orig = get_image(fpath)
    try:
        ch_imgs = segment(orig)
    except Exception:
        traceback.print_exc()
        ch_imgs = [np.zeros((CH_HEIGHT, CH_WIDTH), dtype=np.uint8)] * NUM_CHARS

    # Visualizations.
    denoised = _denoise(orig)
    with_lines = to_rgb(denoised.copy())
    for line in _get_lines(denoised):
        x1, y1, x2, y2 = line
        cv2.line(with_lines, (x1, y1), (x2, y2), HIGH_COLOR, LINE_THICK)
    processed = _preprocess(orig)
    # cv2.imwrite('denoised/vis.png', processed)
    with_rects = [np.pad(a, ((PAD_H,), (PAD_W,)), _CONSTANT) for a in ch_imgs]
    with_rects = np.concatenate(with_rects, axis=1)
    with_rects = np.pad(with_rects, ((0,), (EXTRA_PAD_W,)), _CONSTANT)
    with_rects = to_rgb(with_rects)
    for i in range(NUM_CHARS):
        x1 = i * BOX_W + PAD_W + EXTRA_PAD_W - 1
        x2 = x1 + CH_WIDTH + 1
        y1 = PAD_H - 1
        y2 = y1 + CH_HEIGHT + 1
        cv2.rectangle(with_rects, (x1, y1), (x2, y2), HIGH_COLOR, 1)

    res = np.concatenate((
        to_rgb(orig),
        to_rgb(denoised),
        with_lines,
        to_rgb(processed),
        with_rects))
    cv2.imshow('opencv-result', res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def train(captchas_dir):
    NUM_INPUT = CH_WIDTH * CH_HEIGHT
    NUM_NEURONS_HIDDEN = NUM_INPUT // 3
    NUM_OUTPUT = 36
    ann = libfann.neural_net()
    ann.create_standard_array((NUM_INPUT, NUM_NEURONS_HIDDEN, NUM_OUTPUT))
    # ann.set_activation_function_hidden(libfann.SIGMOID)
    # ann.set_activation_function_output(libfann.SIGMOID)
    # ann.randomize_weights(0.0, 0.0)

    start = time.time()
    succeed = 0
    captchas_dir = os.path.abspath(captchas_dir)
    captchas = os.listdir(captchas_dir)
    report()
    for i, name in enumerate(captchas):
        answer = name[:4]
        if not answer:
            continue
        fpath = os.path.join(captchas_dir, name)
        try:
            img = get_image(fpath)
            ch_imgs = segment(img)
            for ch_img, symbol in zip(ch_imgs, answer):
                ann.train(get_ch_data(ch_img), make_ann_output(symbol))
        except Exception as exc:
            report('Error occured while processing {}: {}'.format(name, exc))
            report()
        else:
            succeed += 1
            report('{}/{}'.format(i + 1, len(captchas)), progress=True)
    runtime = time.time() - start
    report('Done training on {}/{} captchas in {:.3f} seconds'.format(
        succeed, len(captchas), runtime))

    return ann


def ocr(ann, img):
    def get_symbol(ch_img):
        data = get_ch_data(ch_img)
        out = ann.run(data)
        return POSSIBLE_SYMBOLS[out.index(max(out))]

    return ''.join(map(get_symbol, segment(img)))


def ocr_bench(ann, captchas_dir):
    start = time.time()
    captchas_dir = os.path.abspath(captchas_dir)
    captchas = os.listdir(captchas_dir)
    correct = 0
    total = 0
    full = 0
    report()
    for i, name in enumerate(captchas):
        answer1 = name[:4]
        if not answer1:
            continue
        total += NUM_CHARS
        fpath = os.path.join(captchas_dir, name)
        try:
            img = get_image(fpath)
            answer2 = ocr(ann, img)
        except Exception as exc:
            report('Error occured while processing {}: {}'.format(name, exc))
            report()
        else:
            match = get_match(answer1, answer2)
            correct += match
            if match == NUM_CHARS:
                full += match
            report('{}/{}'.format(i + 1, len(captchas)), progress=True)
    runtime = time.time() - start
    report('{:.2f}% ({:.2f}% full) in {:.3f} seconds'.format(
        correct / total * 100,
        full / total * 100,
        runtime))


def get_captcha():
    CAPTCHA_URL = 'http://statistics.e-register.ee/et/shareholders/'
    CAPTCHA_IMAGE_URL_TEMPLATE = 'http://statistics.e-register.ee/graphics/captcha/%s.png'
    CHROME_UA = (
        'Mozilla/5.0 (Windows NT 6.1; WOW64) ' +
        'AppleWebKit/537.36 (KHTML, like Gecko) ' +
        'Chrome/48.0.2564.116 Safari/537.36'
    )
    CAPTCHA_HEADERS = {
        'User-Agent': CHROME_UA,
        'Referer': 'http://statistics.e-register.ee/',
    }
    res = requests.get(CAPTCHA_URL, headers=CAPTCHA_HEADERS).text
    soup = bs4.BeautifulSoup(res, 'html.parser')
    captcha_id = soup.select('#captcha-id')[0]['value']
    captcha_image_url = CAPTCHA_IMAGE_URL_TEMPLATE % captcha_id
    image_request = requests.get(captcha_image_url, headers=CAPTCHA_HEADERS)
    if image_request.headers.get('Content-Type') != 'image/png':
        raise Exception('Bad CAPTCHA image request')

    return image_request.content, captcha_id


def collect(run, captchas_dir, tmp_path):
    while run.is_set():
        try:
            data = get_captcha()
            name = data[1] + '.png'
            fpath = os.path.join(captchas_dir, name)
            # In order to not leave partial files.
            open(tmp_path, 'wb').write(data[0])
            os.rename(tmp_path, fpath)
        except Exception as exc:
            report('Error occured while collecting: {}'.format(exc))
        else:
            report('Saved {}'.format(name))
        time.sleep(1)


def run_collect_threads(captchas_dir):
    NUM_THREADS = 10
    SPAWN_DELAY = 0.5

    threads = []
    run = threading.Event()
    run.set()
    captchas_dir = os.path.abspath(captchas_dir)
    mkdirp(captchas_dir)

    for i in range(NUM_THREADS):
        tmp_path = os.path.join(captchas_dir, '.{}.tmp'.format(i))
        thread = threading.Thread(target=collect, args=(run, captchas_dir, tmp_path))
        threads.append(thread)
        thread.start()
        time.sleep(SPAWN_DELAY)

    try:
        while run.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        report('Closing threads')
        run.clear()
        for thread in threads:
            thread.join()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'mode',
        choices=['vis', 'vis_all_lines', 'denoise_all', 'collect', 'train', 'ocr', 'ocr-bench'],
        help='operational mode')
    parser.add_argument(
        '-i', dest='infile', metavar='infile',
        help='input file/directory')
    parser.add_argument(
        '-o', dest='outfile', metavar='outfile',
        help='output file/directory')
    parser.add_argument(
        '-n', dest='netfile', metavar='netfile',
        help='neural network')
    opts = parser.parse_args(sys.argv[1:])
    if opts.mode == 'vis':
        if opts.infile is None:
            parser.error('specify input captcha')
        vis(opts.infile)
    elif opts.mode == 'vis_all_lines':
        if opts.infile is None:
            parser.error('specify input captcha')
        vis_all_lines(opts.infile)
    elif opts.mode == 'denoise_all':
        if opts.infile is None:
            parser.error('specify input directory with captchas')
        denoise_all(opts.infile)
    elif opts.mode == 'train':
        if opts.infile is None:
            parser.error('specify input directory with captchas')
        if opts.outfile is None:
            parser.error('specify output file for network data')
        ann = train(opts.infile)
        ann.save(opts.outfile)
    elif opts.mode == 'collect':
        if opts.outfile is None:
            parser.error('specify output directory for captchas')
        run_collect_threads(opts.outfile)
    elif opts.mode == 'ocr':
        if opts.infile is None:
            parser.error('specify input captcha')
        if opts.netfile is None:
            parser.error('specify network file')
        ann = get_network(opts.netfile)
        img = get_image(opts.infile)
        print(ocr(ann, img))
    elif opts.mode == 'ocr-bench':
        if opts.infile is None:
            parser.error('specify input directory with captchas')
        if opts.netfile is None:
            parser.error('specify network file')
        ann = get_network(opts.netfile)
        ocr_bench(ann, opts.infile)


if __name__ == '__main__':
    main()
