from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

MNC_JOBS = [
    {"id":"m1","title":"Software Engineer — Full Stack","company":"Google","location":"Hyderabad, IN","exp":"Fresher","tags":["fullstack","ml"],"skills":["javascript","python","react","node"],"link":"https://careers.google.com"},
    {"id":"m2","title":"Associate Software Engineer","company":"Infosys","location":"Bengaluru, IN","exp":"Fresher","tags":["fullstack"],"skills":["java","python","javascript","sql"],"link":"https://career.infosys.com"},
    {"id":"m3","title":"Software Engineer Trainee","company":"TCS","location":"Chennai, IN","exp":"Fresher","tags":["fullstack"],"skills":["java","sql","python","javascript"],"link":"https://ibegin.tcs.com"},
    {"id":"m4","title":"Graduate Engineer Trainee","company":"Wipro","location":"Hyderabad, IN","exp":"Fresher","tags":["fullstack"],"skills":["java","python","javascript","react"],"link":"https://careers.wipro.com"},
    {"id":"m5","title":"Junior Developer","company":"Accenture","location":"Pune, IN","exp":"Fresher","tags":["fullstack"],"skills":["javascript","react","node","sql"],"link":"https://www.accenture.com/in-en/careers"},
    {"id":"m6","title":"Software Development Engineer","company":"Amazon","location":"Hyderabad, IN","exp":"0-1 yr","tags":["fullstack","ml"],"skills":["python","java","aws","sql"],"link":"https://www.amazon.jobs"},
    {"id":"m7","title":"Data Scientist Trainee","company":"IBM","location":"Bengaluru, IN","exp":"Fresher","tags":["ml"],"skills":["python","ml","ai","sql","tensorflow"],"link":"https://www.ibm.com/in-en/employment"},
    {"id":"m8","title":"Python Developer","company":"Capgemini","location":"Mumbai, IN","exp":"Fresher","tags":["fullstack","ml"],"skills":["python","django","flask","sql"],"link":"https://www.capgemini.com/in-en/careers"},
    {"id":"m9","title":"Full Stack Developer","company":"HCL Technologies","location":"Noida, IN","exp":"Fresher","tags":["fullstack"],"skills":["react","node","javascript","mongodb"],"link":"https://www.hcltech.com/careers"},
    {"id":"m10","title":"React Developer","company":"Tech Mahindra","location":"Pune, IN","exp":"Fresher","tags":["fullstack"],"skills":["react","javascript","html","css"],"link":"https://careers.techmahindra.com"},
    {"id":"m11","title":"ML Engineer","company":"Microsoft","location":"Hyderabad, IN","exp":"0-1 yr","tags":["ml","fullstack"],"skills":["python","ml","ai","azure","tensorflow"],"link":"https://careers.microsoft.com"},
    {"id":"m12","title":"Cloud Engineer","company":"Deloitte","location":"Bengaluru, IN","exp":"Fresher","tags":["fullstack","remote"],"skills":["aws","azure","python","javascript"],"link":"https://careers.deloitte.com"},
    {"id":"m13","title":"Software Engineer","company":"Cognizant","location":"Chennai, IN","exp":"Fresher","tags":["fullstack"],"skills":["java","javascript","sql","python"],"link":"https://careers.cognizant.com"},
    {"id":"m14","title":"Data Engineer","company":"Oracle","location":"Hyderabad, IN","exp":"Fresher","tags":["ml","fullstack"],"skills":["sql","python","java","mongodb"],"link":"https://www.oracle.com/in/corporate/careers"},
    {"id":"m15","title":"Junior Software Engineer","company":"Mindtree","location":"Bengaluru, IN","exp":"Fresher","tags":["fullstack"],"skills":["javascript","react","node","sql"],"link":"https://www.ltimindtree.com/careers"},
    {"id":"m16","title":"Associate Engineer","company":"Zoho","location":"Chennai, IN","exp":"Fresher","tags":["fullstack"],"skills":["javascript","react","python","sql"],"link":"https://careers.zohocorp.com"},
    {"id":"m17","title":"Software Developer","company":"Freshworks","location":"Chennai, IN","exp":"Fresher","tags":["fullstack","ml"],"skills":["python","react","node","sql"],"link":"https://careers.freshworks.com"},
    {"id":"m18","title":"Backend Developer","company":"PhonePe","location":"Bengaluru, IN","exp":"0-1 yr","tags":["fullstack"],"skills":["python","java","node","sql"],"link":"https://phonepe.com/en/careers.html"},
    {"id":"m19","title":"Frontend Developer","company":"Swiggy","location":"Bengaluru, IN","exp":"Fresher","tags":["fullstack"],"skills":["react","javascript","html","css"],"link":"https://careers.swiggy.com"},
    {"id":"m20","title":"ML Research Engineer","company":"Samsung R&D","location":"Bengaluru, IN","exp":"Fresher","tags":["ml"],"skills":["python","ml","tensorflow","ai"],"link":"https://samsung.com/in/careers"},
]

def extract_skills_from_resume(resume_text):
    resume_lower = resume_text.lower()

    all_skills = {
        "react": ["react", "reactjs", "react.js"],
        "python": ["python"],
        "javascript": ["javascript", "js", "es6"],
        "node": ["node", "nodejs", "node.js"],
        "java": ["java"],
        "sql": ["sql", "mysql", "postgresql"],
        "mongodb": ["mongodb", "mongo"],
        "aws": ["aws", "amazon web services"],
        "azure": ["azure", "microsoft azure"],
        "ml": ["machine learning", "ml", "scikit", "sklearn"],
        "ai": ["artificial intelligence", "ai", "deep learning"],
        "tensorflow": ["tensorflow", "keras", "pytorch"],
        "django": ["django"],
        "flask": ["flask"],
        "html": ["html", "html5"],
        "css": ["css", "css3", "tailwind", "bootstrap"],
        "angular": ["angular", "angularjs"],
        "php": ["php"],
        "c": [" c ", "c programming", "c language"],
        "github": ["github", "git"],
    }

    found_skills = []
    for skill, keywords in all_skills.items():
        if any(k in resume_lower for k in keywords):
            found_skills.append(skill)

    return found_skills

def calculate_match_score(user_skills, job_skills):
    if not user_skills or not job_skills:
        return 0, []

    matched = []
    for skill in user_skills:
        if skill in job_skills:
            matched.append(skill)

    # Score = percentage of job skills the user has
    score = int((len(matched) / len(job_skills)) * 100)
    return score, matched

def fetch_remote_jobs():
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {"category": "software-dev", "limit": 20}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        remote_jobs = []
        for i, job in enumerate(data.get("jobs", [])):
            title = job.get("title", "")
            tags_raw = job.get("tags", [])
            description = job.get("description", "")
            if isinstance(tags_raw, list):
                tags_str = " ".join(tags_raw)
            else:
                tags_str = str(tags_raw)
            keywords = (title + " " + tags_str + " " + description).lower()

            tags = []
            job_skills = []
            if any(k in keywords for k in ["react","reactjs"]):
                tags.append("fullstack"); job_skills.append("react")
            if any(k in keywords for k in ["node","nodejs"]):
                tags.append("fullstack"); job_skills.append("node")
            if any(k in keywords for k in ["javascript","js"]):
                tags.append("fullstack"); job_skills.append("javascript")
            if any(k in keywords for k in ["python"]):
                job_skills.append("python")
            if any(k in keywords for k in ["machine learning","ml","ai"]):
                tags.append("ml"); job_skills.append("ml")
            if any(k in keywords for k in ["frontend","backend","full stack"]):
                tags.append("fullstack")
            tags.append("remote")
            if not any(t in ["fullstack","ml"] for t in tags):
                tags.append("fullstack"); job_skills.append("javascript")

            remote_jobs.append({
                "id": 1000 + i,
                "title": title,
                "company": job.get("company_name", ""),
                "location": "Remote, Worldwide",
                "exp": "Fresher – 2 yrs",
                "match": "stretch",
                "score": 0,
                "reason": "",
                "tags": tags,
                "skills": job_skills,
                "link": job.get("url", "#"),
                "is_mnc": False
            })
        return remote_jobs
    except:
        return []

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        remote_jobs = fetch_remote_jobs()
        all_jobs = []

        for job in MNC_JOBS:
            all_jobs.append({
                **job,
                "score": 0,
                "reason": "Upload resume for personalized matching",
                "is_mnc": True
            })

        all_jobs += remote_jobs
        return jsonify(all_jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/resume', methods=['POST'])
def get_jobs_by_resume():
    try:
        resume_text = request.json.get("resume_text", "")
        if not resume_text:
            return jsonify({"error": "No resume provided"}), 400

        # Extract skills from THIS specific resume
        user_skills = extract_skills_from_resume(resume_text)
        print(f"Skills found in resume: {user_skills}")

        remote_jobs = fetch_remote_jobs()
        all_jobs = list(MNC_JOBS) + remote_jobs

        scored_jobs = []
        for job in all_jobs:
            job_skills = job.get("skills", [])
            is_mnc = any(mnc in job["company"].lower() for mnc in [
                "google","amazon","microsoft","tcs","infosys","wipro",
                "accenture","ibm","capgemini","hcl","tech mahindra",
                "deloitte","cognizant","oracle","mindtree","zoho",
                "freshworks","phonepe","swiggy","samsung"
            ])

            score, matched = calculate_match_score(user_skills, job_skills)

            # MNC bonus
            if is_mnc:
                score = min(score + 10, 100)

            # Build reason message
            if matched:
                if score >= 70:
                    match = "strong"
                    reason = f"{'🏢 MNC | ' if is_mnc else ''}✅ Great match: {', '.join(matched[:4])}"
                elif score >= 40:
                    match = "strong"
                    reason = f"{'🏢 MNC | ' if is_mnc else ''}👍 Good match: {', '.join(matched[:3])}"
                else:
                    match = "stretch"
                    reason = f"{'🏢 MNC | ' if is_mnc else ''}⚡ Partial: {', '.join(matched[:2])}"
            else:
                match = "stretch"
                reason = f"{'🏢 MNC | ' if is_mnc else ''}📚 Learn required skills"

            scored_jobs.append({
                **job,
                "score": score,
                "match": match,
                "reason": reason,
                "is_mnc": is_mnc
            })

        # Sort — highest score first, MNCs prioritized
        scored_jobs.sort(key=lambda x: (x["score"], x.get("is_mnc", False)), reverse=True)
        return jsonify(scored_jobs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "Job Hunt API is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)