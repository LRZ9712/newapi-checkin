from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, requests, os, datetime
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
import urllib.parse
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'potato_secret_2026')
DB_DIR = 'data'
DB_PATH = os.path.join(DB_DIR, 'checkin.db')

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', '123456')

def init_db():
    if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, url TEXT, user_id TEXT, session_cookie TEXT,
                  cron_time TEXT DEFAULT '08:00',
                  last_status TEXT, last_time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  site_id INTEGER, check_date TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    # 数据库热更新：自动增加排序字段，防止旧数据库报错
    try:
        c.execute("ALTER TABLE sites ADD COLUMN sort_order INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # 列已存在则忽略
        
    conn.commit()
    conn.close()

def get_all_settings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    settings = {row[0]: row[1] for row in c.execute("SELECT key, value FROM settings").fetchall()}
    conn.close()
    settings.setdefault('site_title', 'potato')
    settings.setdefault('profile_name', '蝎子赖赖')
    settings.setdefault('profile_avatar', 'https://api.dicebear.com/7.x/notionists/svg?seed=Felix&backgroundColor=e0d6c1')
    settings.setdefault('profile_signature', 'Ciallo～(∠・ω<)⌒★')
    return settings

def send_notification(title, content):
    settings = get_all_settings()
    if settings.get('bark_enabled') == 'true' and settings.get('bark_url'):
        try:
            base_url = settings['bark_url'].strip().rstrip('/')
            title_enc = urllib.parse.quote(title)
            content_enc = urllib.parse.quote(content)
            requests.get(f"{base_url}/{title_enc}/{content_enc}", timeout=5)
        except Exception as e:
            print(f"Bark 发送失败: {e}")

    if settings.get('email_enabled') == 'true':
        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['Subject'] = title
            msg['From'] = settings.get('email_user')
            msg['To'] = settings.get('email_receiver')
            server = smtplib.SMTP_SSL(settings.get('email_smtp'), int(settings.get('email_port', 465)))
            server.login(settings.get('email_user'), settings.get('email_pass'))
            server.sendmail(settings.get('email_user'), [settings.get('email_receiver')], msg.as_string())
            server.quit()
        except Exception as e:
            print(f"邮件发送失败: {e}")

def execute_checkin(site_id=None, manual=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if site_id:
        sites = c.execute("SELECT id, name, url, user_id, session_cookie, cron_time FROM sites WHERE id=?", (site_id,)).fetchall()
    else:
        current_time = datetime.datetime.now().strftime('%H:%M')
        sites = c.execute("SELECT id, name, url, user_id, session_cookie, cron_time FROM sites WHERE cron_time=?", (current_time,)).fetchall()
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    failed_sites = []

    for site in sites:
        sid, name, url, uid, cookie_str, cron_time = site
        headers = {
            'accept': 'application/json, text/plain, */*',
            'new-api-user': str(uid),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        if not cookie_str.startswith('session='): cookie_str = 'session=' + cookie_str
        cookies = {'session': cookie_str.replace('session=', '')}
        
        is_success = False
        try:
            res = requests.post(url, headers=headers, cookies=cookies, timeout=10)
            if res.status_code == 200:
                try:
                    res_json = res.json()
                    message = res_json.get('message', '')
                    if res_json.get('success') == True:
                        status_text = "签到成功"
                        is_success = True
                    elif "已签到" in message:
                        status_text = "今日已签到"
                        is_success = True 
                    else:
                        status_text = f"失败: {message}"
                except:
                    status_text = "签到成功"
                    is_success = True
            else:
                status_text = f"失败 ({res.status_code})"
        except Exception as e:
            status_text = "请求异常"
            
        c.execute("UPDATE sites SET last_status=?, last_time=? WHERE id=?", (status_text, now_time, sid))
        
        log_status = "签到成功" if is_success else status_text
        c.execute("INSERT INTO logs (site_id, check_date, status) VALUES (?, ?, ?)", (sid, today, log_status))
        
        if not is_success:
            failed_sites.append(name)
            
    conn.commit()
    conn.close()

    if failed_sites:
        failed_names = "，".join(failed_sites)
        settings = get_all_settings()
        send_notification(f"⚠️ {settings.get('site_title')} 签到失败", f"站点【{failed_names}】于 {now_time} 签到失败。\n请登录面板更新信息。")

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
scheduler.add_job(func=execute_checkin, trigger="interval", minutes=1)
scheduler.start()

@app.before_request
def require_login():
    allowed_routes = ['login', 'do_login', 'static']
    if request.endpoint not in allowed_routes and 'logged_in' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login(): return render_template('login.html', s=get_all_settings())

@app.route('/login', methods=['POST'])
def do_login():
    data = request.json
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        session['logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "账号或密码错误"})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index(): return render_template('index.html', s=get_all_settings())

@app.route('/api/sites', methods=['GET'])
def get_sites():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 按照 sort_order 和 id 排序返回
    sites = c.execute("SELECT id, name, url, user_id, session_cookie, cron_time, last_status, last_time FROM sites ORDER BY sort_order ASC, id ASC").fetchall()
    conn.close()
    return jsonify([{"id": s[0], "name": s[1], "url": s[2], "user_id": s[3], "session_cookie": s[4],
                     "cron_time": s[5], "last_status": s[6], "last_time": s[7]} for s in sites])

@app.route('/api/logs/<int:site_id>/<month>', methods=['GET'])
def get_logs(site_id, month):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    logs = c.execute("SELECT check_date, status FROM logs WHERE site_id=? AND check_date LIKE ?", (site_id, f"{month}%")).fetchall()
    conn.close()
    return jsonify([{"date": l[0], "status": l[1]} for l in logs])

@app.route('/api/add', methods=['POST'])
def add_site():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 新增的卡片默认排在最下面
    sort_order = int(time.time())
    c.execute("INSERT INTO sites (name, url, user_id, session_cookie, cron_time, last_status, last_time, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (data['name'], data['url'], data['user_id'], data['session_cookie'], data.get('cron_time', '08:00'), '等待执行', '-', sort_order))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/edit/<int:site_id>', methods=['POST'])
def edit_site(site_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE sites SET name=?, url=?, user_id=?, session_cookie=?, cron_time=?, last_status='信息已修改,等待执行' WHERE id=?", 
              (data['name'], data['url'], data['user_id'], data['session_cookie'], data['cron_time'], site_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/reorder', methods=['POST'])
def reorder_sites():
    # 接收包含 id 和 sort_order 的数组进行批量更新
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for item in data:
        c.execute("UPDATE sites SET sort_order=? WHERE id=?", (item['sort_order'], item['id']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/trigger/<int:site_id>', methods=['POST'])
def trigger_site(site_id):
    execute_checkin(site_id, manual=True)
    return jsonify({"success": True})

@app.route('/api/delete/<int:site_id>', methods=['DELETE'])
def delete_site(site_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM sites WHERE id=?", (site_id,))
    c.execute("DELETE FROM logs WHERE site_id=?", (site_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'POST':
        data = request.json
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for k, v in data.items():
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    else:
        return jsonify(get_all_settings())

@app.route('/api/test_notify', methods=['POST'])
def test_notify():
    settings = get_all_settings()
    send_notification(f"✅ {settings.get('site_title')} 测试成功", "这是一条来自自动签到系统的测试消息。配置工作完全正常！")
    return jsonify({"success": True, "message": "测试通知已发送，请检查接收端。"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
