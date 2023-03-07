import os
import requests
from flask import Flask, request, render_template, send_from_directory, jsonify
import torch
from PIL import Image, ImageDraw
from werkzeug.utils import secure_filename

#config
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

PROBABILITY = 0.5
NEED_CLASS = 'car'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'last.jpg')
    return render_template('index.html', last_image = full_filename, count = 0)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload/<type_object>', methods=['GET', 'POST'])
def upload_file(type_object=None):

    if request.method == 'POST':
        #check exist image 
        if 'file_img' not in request.files:
            return render_template('create.html')

        file_rcv = request.files['file_img']

        if file_rcv.filename == '' or not allowed_file(file_rcv.filename):
            return render_template('create.html')

        filename = secure_filename(file_rcv.filename)

        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'out-' + filename)
        file_rcv.save(path)

        result = model(path)

        if type_object!=None:
            NEED_CLASS = check_class_category(type_object)
        else:
            NEED_CLASS=None

        if NEED_CLASS!=None:
            all_box = select_object(result, NEED_CLASS)
            count_object = len(all_box)   

            if all_box!=[]:
                draw_box(all_box, path, result_path)
            else:
                result_path = path
        else:
            result.render()
            count_object = len(result.pred[0])
            Image.fromarray(result.ims[0]).save(result_path)

        if type_object:
            result_path = '../' + result_path
        return render_template('index.html', last_image = result_path, count = count_object)

    return render_template('create.html')

@app.route('/json', methods=['POST'])
def recv_message():
    content = request.get_json()
    filename = content['img'].rsplit('/', 1)[1].lower()
    type_object = content['object']
    NEED_CLASS = check_class_category(type_object)

    url = content['img']

    r = requests.get(url)

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'out-' + filename)

    with open(path, 'wb') as f:
        f.write(r.content)
        result = model(path)

        if NEED_CLASS!=None:
            all_box = select_object(result, NEED_CLASS)
            count_object = len(all_box)

            if all_box!=[]:
                draw_box(all_box, path, result_path)
            else:
                result_path = path
        else:
            result.render()
            count_object = len(result.pred[0])
            Image.fromarray(result.ims[0]).save(result_path)

    result = {"count":count_object, "image":result_path}
    return jsonify(result)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def select_object(result, OUR_CLASS):
    box_one = []
    all_box = []

    category = get_class_index(model.names, OUR_CLASS)
    for line in list(result.pred[0]):
        if line[5] == category and line[4] > PROBABILITY:
            box_one = [int(line[0]), int(line[1]), int(line[2]), int(line[3])]
            all_box.append(box_one)

    return all_box   

def draw_box(boxes, filename_input, filename_output):
    with Image.open(filename_input) as im:
        draw = ImageDraw.Draw(im)
        for box in boxes:
            A1, A2, B1, B2 = box[0], box[1], box[2], box[3]
            draw.rectangle((A1, A2, B1, B2), fill=None, outline=(255,0,0), width=3)
        im.save(filename_output, quality=95)

def get_class_index(all_classess, need_class):

    class_index = list(all_classess.keys())[list(all_classess.values()).index(need_class)]

    return int(class_index)

def check_class_category(type_object):

    type_object_right = type_object.replace('_', ' ')

    if type_object_right in model.names.values():
        return type_object_right
    else:
        return None


if __name__ == '__main__':
    '''
    0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 
    5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 
    10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 
    14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 
    20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 
    25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 
    30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 
    34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard',
    37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 
    41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana',
    47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 
    52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 
    57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 
    61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 
    66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 
    70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 
    75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 
    79: 'toothbrush'}
    '''
    model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained=True)
    model.eval()

    app.run(host='0.0.0.0')
