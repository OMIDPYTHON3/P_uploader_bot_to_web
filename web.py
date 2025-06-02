from flask import Flask, render_template_string, send_from_directory, request, redirect
import os
from threading import Thread
import shutil

app1 = Flask(__name__)

PASSWORD = "omid1234@A"
BASE_DIR = os.path.join(os.getcwd(), "downloads")

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

@app1.route('/')
@app1.route('/<path:req_path>')
def dir_listing(req_path=''):
    abs_path = os.path.join(BASE_DIR, req_path)

    if not os.path.abspath(abs_path).startswith(os.path.abspath(BASE_DIR)):
        return "⛔ دسترسی غیرمجاز", 403

    if os.path.isfile(abs_path):
        return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path))

    if not os.path.exists(abs_path):
        return "❌ مسیر پیدا نشد", 404

    files = os.listdir(abs_path)
    files.sort()

    # جمع حجم فایل‌ها
    total_folder_size = 0

    file_links = []
    for f in files:
        full_path = os.path.join(abs_path, f)
        is_dir = os.path.isdir(full_path)
        size = os.path.getsize(full_path) if not is_dir else 0
        total_folder_size += size
        link = os.path.join('/', req_path, f)
        if is_dir:
            link += '/'
        file_links.append({
            'name': f + ('/' if is_dir else ''),
            'link': link,
            'is_file': not is_dir,
            'size': format_size(size),
            'path': os.path.join(req_path, f)
        })

    parent_link = '/'.join(req_path.strip('/').split('/')[:-1])
    if parent_link:
        parent_link = '/' + parent_link

    # فضای حافظه
    total, used, free = shutil.disk_usage(BASE_DIR)

    html = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>File Browser</title>
  <style>
    body {
      font-family: sans-serif;
      background-color: #f5f5f5;
      color: #333;
      padding: 10px;
      font-size: 14px;
    }
    h1, h2 {
      font-size: 16px;
      margin-bottom: 8px;
    }
    ul {
      list-style: none;
      padding-left: 0;
      margin-top: 0;
    }
    li {
      margin: 6px 0;
      background: #fff;
      padding: 6px 8px;
      border-radius: 4px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      font-size: 13px;
    }
    a {
      text-decoration: none;
      color: #0069d9;
      margin-right: 6px;
    }
    form {
      display: inline;
      margin-left: 6px;
    }
    input[type="password"] {
      padding: 2px 5px;
      border-radius: 3px;
      border: 1px solid #ccc;
      font-size: 12px;
      width: 100px;
    }
    button {
      background-color: #dc3545;
      color: white;
      border: none;
      padding: 3px 6px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 12px;
    }
    button:hover {
      background-color: #c82333;
    }
  </style>
</head>
<body>
  <h2>💾 فضای دیسک:</h2>
  <ul>
      <li>کل: {{ disk_total }}</li>
      <li>مصرف‌شده: {{ disk_used }}</li>
      <li>آزاد: {{ disk_free }}</li>
      <li>📂 مجموع فایل‌های این پوشه: {{ folder_total }}</li>
  </ul>

  <h1>📁 مسیر جاری: /{{ current_path }}</h1>
  <ul>
    {% if parent_link %}
      <li><a href="{{ parent_link }}">⬅️ بازگشت</a></li>
    {% endif %}
    {% for file in files %}
      <li>
        <a href="{{ file.link }}">{{ file.name }}</a>
        {% if file.is_file %}
          - {{ file.size }}
          <form method="POST" action="/delete">
            <input type="hidden" name="path" value="{{ file.path }}">
            <input type="password" name="password" placeholder="رمز حذف" required>
            <button type="submit">🗑️ حذف</button>
          </form>
        {% endif %}
      </li>
    {% endfor %}
  </ul>
</body>
</html>
'''

    return render_template_string(html,
        files=file_links,
        current_path=req_path,
        parent_link=parent_link,
        folder_total=format_size(total_folder_size),
        disk_total=format_size(total),
        disk_used=format_size(used),
        disk_free=format_size(free)
    )

@app1.route('/delete', methods=['POST'])
def delete_file():
    path = request.form.get("path")
    password = request.form.get("password")

    abs_path = os.path.join(BASE_DIR, path)
    if password != PASSWORD:
        return "❌ رمز نادرست", 403

    if os.path.isfile(abs_path):
        os.remove(abs_path)
        return redirect('/' + '/'.join(path.split('/')[:-1]))
    else:
        return "فایل پیدا نشد", 404

def run():
    app1.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()