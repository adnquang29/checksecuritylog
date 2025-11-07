from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import db
from app.models import User
from datetime import datetime, timezone
from app.email import send_password_reset_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/', methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid usename or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    return render_template("user.html", user=user, form=form)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)

@app.route("/remove_user/<username>", methods=["POST"])
@login_required
def remove_user(username):
    if current_user.username != username:
        return redirect(url_for("index"))
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.")
    return redirect(url_for("index"))

@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("login"))
    return render_template("reset_password_request.html", title="Reset Password", form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route("/checklog", methods=["GET", "POST"])
@login_required
def checklog():
    if request.method == "GET":
        return render_template("checklog.html", title="Check Log")

    # ----------------- helpers (cục bộ, không đổi file khác) -----------------
    import re, math
    from collections import Counter

    WORD_RE = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)?", re.UNICODE)

    def _tokens(text: str):
        return [w.lower() for w in WORD_RE.findall(text or "")]

    def _bow(text: str) -> Counter:
        return Counter(_tokens(text))

    def _cosine(counter_a: Counter, counter_b: Counter) -> float:
        if not counter_a or not counter_b:
            return 0.0
        vocab = set(counter_a) | set(counter_b)
        dot = sum(counter_a[w] * counter_b[w] for w in vocab)
        na = math.sqrt(sum(v * v for v in counter_a.values()))
        nb = math.sqrt(sum(v * v for v in counter_b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    # ====== Dummy tiêu chí cho NIST SP 800-207 ======
    ZT5_CRITERIA = [
        {
            "id": "integrity_check_failed",
            "name": "Integrity check thất bại",
            "keywords": [
                "integrity", "tamper", "checksum", "hash mismatch",
                "attestation", "measured boot", "secure boot", "tpm error"
            ],
            "desc": "Phát hiện integrity check/attestation thất bại trên tài sản."
        },
        {
            "id": "device_posture_noncompliant",
            "name": "Thiết bị không tuân thủ posture",
            "keywords": [
                "noncompliant", "mdm", "compliance", "policy violation",
                "encryption off", "disk not encrypted", "firewall disabled",
                "av disabled", "edr disabled", "os outdated"
            ],
            "desc": "Posture thiết bị lệch chuẩn chính sách (MDM/AV/EDR/Firewall/Encryption)."
        },
        {
            "id": "vuln_exposure",
            "name": "Phơi lộ lỗ hổng/CVE",
            "keywords": [
                "cve-", "vulnerability", "critical", "high severity",
                "exploitable", "patch available", "not patched", "kb-"
            ],
            "desc": "Tài sản có lỗ hổng/CVE nghiêm trọng, chưa vá."
        },
        {
            "id": "edr_alert",
            "name": "EDR/AV cảnh báo",
            "keywords": [
                "edr alert", "malware", "quarantine", "suspicious",
                "ransomware", "behavior", "ioc", "threat detected"
            ],
            "desc": "Giám sát EDR/AV phát hiện hành vi/IOC độc hại."
        },
        {
            "id": "inventory_drift",
            "name": "Drift cấu hình / thay đổi tài sản",
            "keywords": [
                "asset change", "new asset", "removed asset",
                "config drift", "baseline deviation", "unauthorized change"
            ],
            "desc": "Theo dõi thay đổi tài sản/baseline bất thường."
        },
        {
            "id": "patch_compliance",
            "name": "Không đạt chuẩn vá lỗi",
            "keywords": [
                "missing patch", "patch failed", "patch pending",
                "kb", "update failed", "reboot required", "superseded"
            ],
            "desc": "Đo lường trạng thái vá lỗi & tuân thủ."
        },
    ]

    # chuẩn bị vector tiêu chí
    def _criteria_bow(c):
        text = " ".join(c["keywords"]) + " . " + c["desc"]
        return _bow(text)
    CRIT_VECTORS = {c["id"]: _criteria_bow(c) for c in ZT5_CRITERIA}

    def analyze_log_text(text: str, threshold: float = 0.55, topk: int = 5):
        log_vec = _bow(text)
        scored = []
        for c in ZT5_CRITERIA:
            s = _cosine(log_vec, CRIT_VECTORS[c["id"]])
            scored.append({
                "id": c["id"],
                "name": c["name"],
                "score": round(float(s), 3),
                "desc": c["desc"],
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        matches = [x for x in scored if x["score"] >= threshold][:topk]
        return {"matches": matches, "all": scored}

    def _format_message(result):
        if not result["matches"]:
            return "Không phát hiện tiêu chí Zero Trust 800-207 nào vượt ngưỡng."
        parts = [f"{m['name']} (score={m['score']})" for m in result["matches"]]
        return "Khớp: " + "; ".join(parts)

    # ----------------- lấy dữ liệu từ form hoặc file upload -----------------
    text_input = (request.form.get("text") or "").strip()

    if not text_input and "file" in request.files and request.files["file"]:
        f = request.files["file"]
        content = f.read()
        try:
            text_input = content.decode("utf-8", errors="ignore")
        except Exception:
            text_input = content.decode("latin-1", errors="ignore")

    # nếu vẫn trống, thử dùng file mẫu checklog.txt (cho demo)
    if not text_input:
        try:
            with open("checklog.txt", "r", encoding="utf-8") as fh:
                text_input = fh.read()
        except Exception:
            text_input = ""

    # ----------------- chạy phân tích cosine -----------------
    result = analyze_log_text(text_input, threshold=0.55, topk=5)
    flash(_format_message(result))

    # render lại trang và truyền kết quả (frontend có thể hiển thị từ biến result)
    return render_template("checklog.html", title="Check Log", result=result, raw=text_input)

@app.route("/datasources", methods=["GET", "POST"])
@login_required
def datasources():
    return render_template("datasources.html", title="Data Sources")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("home.html", title="Home")