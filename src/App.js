import { useState, useEffect } from "react";
import "./App.css";

const filters = [
  { label:"All", value:"all" },
  { label:"Remote", value:"remote" },
  { label:"Strong Match", value:"strong" },
  { label:"Stretch", value:"stretch" },
  { label:"Full Stack", value:"fullstack" },
  { label:"ML / AI", value:"ml" },
];

export default function App() {

  const [active, setActive] = useState("all");
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resumeText, setResumeText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  // ✅ No auto fetch — wait for resume upload
  useEffect(() => {
    setLoading(false);
  }, []);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type === "text/plain") {
      const reader = new FileReader();
      reader.onload = (event) => {
        setResumeText(event.target.result);
      };
      reader.readAsText(file);

    } else if (file.type === "application/pdf") {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const typedArray = new Uint8Array(event.target.result);
        const pdfjsLib = window['pdfjs-dist/build/pdf'];
        pdfjsLib.GlobalWorkerOptions.workerSrc =
          "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        let fullText = "";

        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          const pageText = content.items.map(item => item.str).join(" ");
          fullText += pageText + "\n";
        }
        setResumeText(fullText);
      };
      reader.readAsArrayBuffer(file);
    }
  };

  const analyzeResume = async () => {
    if (!resumeText) return;
    setAnalyzing(true);
    try {
      const res = await fetch("http://localhost:5000/api/jobs/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText })
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        setJobs(data);
      } else {
        setJobs([]);
      }
    } catch (err) {
      console.error("Error:", err);
      setJobs([]);
    }
    setAnalyzing(false);
  };

  const filtered = Array.isArray(jobs)
    ? (active === "all" ? jobs : jobs.filter(j => j.tags.includes(active) || j.match === active))
    : [];

  const strongCount = filtered.filter(j => j.match === "strong").length;
  const stretchCount = filtered.filter(j => j.match === "stretch").length;

  if (loading) return <div style={{color:"#fff", padding:"2rem"}}>Loading...</div>;

  return (
    <div className="container">
      <h1 className="heading">Job Hunt Dashboard</h1>
      <p className="subtitle">Filtered for: India + Remote · Fresher / 0–2 yrs exp</p>

      {/* Resume Upload Box */}
      <div className="resume-box">
        <div className="upload-area" onClick={() => document.getElementById('resume-upload').click()}>
          <div className="upload-icon">📄</div>
          <div className="upload-text">
            {resumeText
              ? "✅ Resume uploaded! Click to change"
              : "Click to upload your resume"}
          </div>
          <div className="upload-hint">Supports PDF and TXT files</div>
          <input
            id="resume-upload"
            type="file"
            accept=".pdf,.txt"
            style={{ display: "none" }}
            onChange={handleFileUpload}
          />
        </div>

        {resumeText && (
          <div className="resume-preview">
            <div className="preview-label">📋 Resume Preview:</div>
            <div className="preview-text">{resumeText.slice(0, 300)}...</div>
          </div>
        )}

        <button
          className="analyze-btn"
          onClick={analyzeResume}
          disabled={analyzing || !resumeText}
        >
          {analyzing ? "Analyzing your resume... ⏳" : "Analyze Resume & Find Jobs 🚀"}
        </button>
      </div>

      {/* Empty State — shown before resume upload */}
      {jobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <div className="empty-title">Upload your resume to get started!</div>
          <div className="empty-subtitle">
            We'll analyze your skills and match you with the best jobs
          </div>
        </div>
      ) : (
        <>
          {/* Stat Cards */}
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-num">{filtered.length}</div>
              <div className="stat-label">Total matches</div>
            </div>
            <div className="stat-card">
              <div className="stat-num green">{strongCount}</div>
              <div className="stat-label">Strong match</div>
            </div>
            <div className="stat-card">
              <div className="stat-num amber">{stretchCount}</div>
              <div className="stat-label">Stretch match</div>
            </div>
          </div>

          {/* Filter Buttons */}
          <div className="filters">
            {filters.map(f => (
              <button
                key={f.value}
                className={`filter-btn ${active === f.value ? "active" : ""}`}
                onClick={() => setActive(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Job Table */}
          <table className="job-table">
            <thead>
              <tr>
                <th>Job title & company</th>
                <th>Location</th>
                <th>Experience</th>
                <th>Match</th>
                <th>Apply</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(job => (
                <tr key={job.id} className="job-row">
                  <td>
                    <div className="job-title">{job.title}</div>
                    <div className="job-company">{job.company}</div>
                    {job.reason && (
                      <div style={{fontSize:"11px", color:"#4ade80", marginTop:"3px"}}>
                        {job.reason}
                      </div>
                    )}
                  </td>
                  <td><span className="badge blue">{job.location}</span></td>
                  <td><span className="badge gray">{job.exp}</span></td>
                  <td>
                    <span className={`badge ${job.match === "strong" ? "green" : "amber"}`}>
                      {job.match === "strong" ? "Strong match" : "Stretch"}
                    </span>
                  </td>
                  <td>
                    <button
                      className="apply-btn"
                      onClick={() => window.open(job.link, "_blank")}
                    >
                      Apply ↗
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}