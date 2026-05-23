"""
MediAI — Diabetes Detection System
Flask Backend + Pure HTML/CSS/JS Frontend
Run: python app.py
Open: http://localhost:5000
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle, os, json
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = "mediai-2025-secret-key"

BASE   = os.path.dirname(os.path.abspath(__file__))
FEATS  = ['TimesPregnant','GlucoseConcentration','BloodPrs',
          'SkinThickness','Serum','BMI','DiabetesFunct','Age']

# ── Load model ───────────────────────────────────────────────────
with open(os.path.join(BASE, "diabetes_model.pkl"), "rb") as f:
    model = pickle.load(f)
with open(os.path.join(BASE, "model_meta.pkl"), "rb") as f:
    meta = pickle.load(f)

# ── Load dataset for stats ───────────────────────────────────────
df = pd.read_csv(os.path.join(BASE, "data", "PimaIndiansDiabetes.csv"))
for c in ['GlucoseConcentration','BloodPrs','SkinThickness','Serum','BMI']:
    df[c] = df[c].replace(0, df[c][df[c] != 0].median())

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def index():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if request.form.get("demo"):
            session["logged_in"] = True
            session["username"]  = "Demo User"
            return redirect(url_for("dashboard"))
        if username and password:
            session["logged_in"] = True
            session["username"]  = username
            return redirect(url_for("dashboard"))
        error = "Please enter both username and password."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ══════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════
@app.route("/dashboard")
@login_required
def dashboard():
    cv  = meta.get("cv_accuracy", 79.15)
    diab_count   = int(df['Class'].sum())
    nodiab_count = int(len(df) - diab_count)
    avg_glucose  = round(float(df['GlucoseConcentration'].mean()), 1)
    avg_bmi      = round(float(df['BMI'].mean()), 1)
    return render_template("dashboard.html",
        username=session["username"], cv=cv,
        diab=diab_count, nodiab=nodiab_count,
        avg_glucose=avg_glucose, avg_bmi=avg_bmi,
        total=len(df))

@app.route("/analysis", methods=["GET", "POST"])
@login_required
def analysis():
    result = None
    if request.method == "POST":
        try:
            vals = {k: float(request.form[k]) for k in
                    ['preg','glucose','bp','skin','insulin','bmi','dpf','age']}
            X = pd.DataFrame([[
                vals['preg'], vals['glucose'], vals['bp'], vals['skin'],
                vals['insulin'], vals['bmi'], vals['dpf'], vals['age']
            ]], columns=FEATS)
            pred = int(model.predict(X)[0])
            prob = model.predict_proba(X)[0]
            conf = round(float(prob[pred]) * 100, 1)
            pd_  = round(float(prob[1]) * 100, 1)

            def bmi_cat(v):
                if v < 18.5: return "Underweight", "warning"
                if v < 25:   return "Normal", "success"
                if v < 30:   return "Overweight", "warning"
                return "Obese", "danger"
            def gluc_cat(v):
                if v < 100: return "Normal", "success"
                if v < 126: return "Pre-Diabetic", "warning"
                return "Diabetic Range", "danger"
            def bp_cat(v):
                if v < 80: return "Normal", "success"
                if v < 90: return "Elevated", "warning"
                return "High", "danger"
            def age_cat(v):
                if v < 30: return "Low Risk", "success"
                if v < 50: return "Moderate", "warning"
                return "Higher Risk", "danger"

            # Save to history
            if "history" not in session:
                session["history"] = []
            entry = dict(preg=vals['preg'], glucose=vals['glucose'],
                         bmi=vals['bmi'], age=vals['age'],
                         result="Diabetic" if pred == 1 else "No Diabetes",
                         confidence=conf)
            history = session.get("history", [])
            history.append(entry)
            session["history"] = history[-20:]  # keep last 20

            result = dict(
                pred=pred, conf=conf, pd=pd_, ph=round(100-pd_,1),
                vals=vals,
                bmi_s=bmi_cat(vals['bmi']),
                gluc_s=gluc_cat(vals['glucose']),
                bp_s=bp_cat(vals['bp']),
                age_s=age_cat(vals['age']),
            )
        except Exception as e:
            result = dict(error=str(e))
    return render_template("analysis.html",
        username=session["username"], result=result)

@app.route("/map")
@login_required
def world_map():
    return render_template("map.html", username=session["username"])

@app.route("/info")
@login_required
def info():
    return render_template("info.html", username=session["username"])

@app.route("/visualization")
@login_required
def visualization():
    # Pass dataset stats as JSON for Chart.js
    gluc_nod = df[df['Class']==0]['GlucoseConcentration'].round(0).astype(int).tolist()[:200]
    gluc_d   = df[df['Class']==1]['GlucoseConcentration'].round(0).astype(int).tolist()[:200]
    ages_nod = df[df['Class']==0]['Age'].tolist()[:200]
    ages_d   = df[df['Class']==1]['Age'].tolist()[:200]
    bmi_nod  = df[df['Class']==0]['BMI'].round(1).tolist()[:200]
    bmi_d    = df[df['Class']==1]['BMI'].round(1).tolist()[:200]
    corr     = df[FEATS].corr().round(2).values.tolist()
    feat_labels = ['Pregnancies','Glucose','BP','Skin','Insulin','BMI','DPF','Age']
    return render_template("visualization.html",
        username=session["username"],
        gluc_nod=json.dumps(gluc_nod), gluc_d=json.dumps(gluc_d),
        ages_nod=json.dumps(ages_nod), ages_d=json.dumps(ages_d),
        bmi_nod=json.dumps(bmi_nod), bmi_d=json.dumps(bmi_d),
        corr=json.dumps(corr), feat_labels=json.dumps(feat_labels),
        diab_count=int(df['Class'].sum()), nodiab_count=int(len(df)-df['Class'].sum()))

@app.route("/history")
@login_required
def history():
    hist = session.get("history", [])
    return render_template("history.html",
        username=session["username"], history=hist)

if __name__ == "__main__":
    print("\n🩺 MediAI — Diabetes Detection System")
    print("   Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)