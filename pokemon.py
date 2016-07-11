import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageFont, ImageDraw

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
VALID_POKE = ['pika', 'charmander', 'squirtle']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'

@app.route("/")
def home():
    return render_template('create.html')

@app.route("/success")
def success():
    path = request.args.get('path')
    full_path = url_for('static', filename=path)
    return render_template('complete.html', path=full_path)

def create_composite(file, pokemon, text, x, y):
    filename = secure_filename(file.filename)
    upload_path = app.config['UPLOAD_FOLDER']

    file.save(os.path.join(upload_path, filename))

    bg = Image.open(os.path.join(upload_path, filename))
    poke = Image.open(os.path.join(upload_path, pokemon + '.png'))
    pokeball = Image.open(os.path.join(upload_path, 'pokeball.png'))

    pos_x = (x / 2) if x > bg.width or x < 0 else x
    pos_y = (y / 2) if y > bg.width or y < 0 else y

    bg.paste(poke, (pos_x, pos_y), poke.convert('RGBA'))
    bg.paste(pokeball, (bg.width / 2, bg.height - (2 * pokeball.height)), pokeball.convert('RGBA'))

    new_filename = gen_filename()
    bg.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

    return new_filename

def gen_filename():
    return 'new.jpg'

@app.route('/create', methods=['GET', 'POST'])
def create_poke():
    errors = validate(request)
    if errors:
        flash(", ".join(errors))
        return redirect(url_for('home'))

    pokemon = request.form['pokemon']
    x = int(request.form['x'])
    y = int(request.form['y'])
    text = request.form['text']
    file = request.files['file']

    composite_path = create_composite(file, pokemon, text, x, y)
    return redirect(url_for('success', path=composite_path))

def validate(request):
    errors = []
    file = request.files['file']
    poke = request.form['pokemon']
    x = request.form['x']
    y = request.form['y']

    if not file:
        errors.append('no file given')
    elif file.filename == '':
        errors.append('empty filename given')
    elif not allowed_file(file.filename):
        errors.append('illegal file')

    int_x = 0
    int_y = 0

    if not x or not y:
        errors.append('invalid arrangement')
    else:
        try:
            int_x = int(x)
            int_y = int(y)
            if int_x < 0 or int_y < 0:
                errors.append('invalid arrangement')
        except ValueError:
            errors.add('invalid positioning')

    if poke == '' or poke not in VALID_POKE:
        errors.append('please choose a valid pokemon')

    return errors

def allowed_file(filename):
    return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True)
