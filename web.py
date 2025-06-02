from flask import Flask, render_template_string, send_from_directory, request, redirect, url_for
import os
from threading import Thread

app1 = Flask(__name__)

# تابع تبدیل حجم به واحد مناسب
def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"

@app1.route('/on')
def on():
    return 'alive'



@app1.route('/')
@app1.route('/<path:req_path>')
def dir_listing(req_path=''):
    BASE_DIR = os.path.join(os.getcwd(), 'downloads')
    abs_path = os.path.join(BASE_DIR, req_path)

    if os.path.isfile(abs_path):
        return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path))

    if not os.path.exists(abs_path):
        return "مسیر پیدا نشد", 404

    files = os.listdir(abs_path)
    files.sort()

    html = '''
    <h1>📁 مسیر جاری: /{{ current_path }}</h1>
    <ul>
      {% if parent_link %}
        <li><a href="{{ parent_link }}">⬅️ بازگشت</a></li>
      {% endif %}
      {% for file in files %}
        <li>
          <a href="{{ file.link }}">{{ file.name }}</a>
          {% if not file.is_dir %}
            - {{ file.size }}
            <form method="post" action="/delete" style="display:inline;">
              <input type="hidden" name="filepath" value="{{ file.full_path }}">
              <input type="password" name="password" placeholder="رمز حذف" required>
              <button type="submit">🗑 حذف</button>
            </form>
          {% endif %}
        </li>
      {% endfor %}
    </ul>
    '''

    parent_link = '/'.join(req_path.strip('/').split('/')[:-1])
    if parent_link:
        parent_link = '/' + parent_link

    file_links = []
    for f in files:
        full_path = os.path.join(abs_path, f)
        is_dir = os.path.isdir(full_path)
        link = os.path.join('/', req_path, f)
        if is_dir:
            link += '/'
        file_links.append({
            'name': f + ('/' if is_dir else ''),
            'link': link,
            'is_dir': is_dir,
            'size': "" if is_dir else format_size(os.path.getsize(full_path)),
            'full_path': os.path.join(req_path, f)
        })

    return render_template_string(html, files=file_links, current_path=req_path, parent_link=parent_link)

@app1.route('/delete', methods=['POST'])
def delete_file():
    filepath = request.form.get('filepath')
    password = request.form.get('password')

    if password != "omid1234@A":
        return "❌ رمز اشتباه است!", 403

    abs_path = os.path.join(os.getcwd(), filepath)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
        return redirect(request.referrer or '/')
    else:
        return "❌ فایل پیدا نشد یا قابل حذف نیست.", 404

def run():
    app1.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()