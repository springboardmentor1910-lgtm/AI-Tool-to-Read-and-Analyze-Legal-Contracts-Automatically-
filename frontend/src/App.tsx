import React, { useState, useRef } from 'react';
import axios from 'axios';
import {
  Upload,
  FileText,
  ShieldCheck,
  TrendingUp,
  Activity,
  Download,
  Star,
  CheckCircle2,
  X,
  Loader2,
  Zap,
  ChevronRight,
  Command,
  FileSearch,
  CheckCircle,
  ArrowLeft,
  History,
  Clock,
  Shield
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Variants } from 'framer-motion';
import './App.css';

const API_BASE = 'http://localhost:8001';

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 }
  }
};

const itemVariants: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: { y: 0, opacity: 1, transition: { duration: 0.5, ease: "easeOut" } }
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [docId, setDocId] = useState<string | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [showReport, setShowReport] = useState(false);
  const [feedback, setFeedback] = useState({ rating: 0, comment: '' });
  const [submittedFeedback, setSubmittedFeedback] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [history, setHistory] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);


  // Customization state
  const [tone, setTone] = useState('formal');
  const [focus, setFocus] = useState('full');
  const [structure, setStructure] = useState('structured');

  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  React.useEffect(() => {
    fetchHistory();
    // Poll for history updates every 30 seconds
    const interval = setInterval(fetchHistory, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setLoading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Simulate progress for visual appeal
      const interval = setInterval(() => {
        setUploadProgress(prev => (prev < 90 ? prev + 10 : prev));
      }, 100);

      const res = await axios.post(`${API_BASE}/upload`, formData);
      clearInterval(interval);
      setUploadProgress(100);
      setTimeout(() => {
        setDocId(res.data.doc_id);
        setLoading(false);
        fetchHistory();
      }, 500);
    } catch (err) {
      console.error(err);
      alert('Upload failed. Ensure backend is running.');
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!docId) return;
    setAnalyzing(true);

    try {
      const res = await axios.post(`${API_BASE}/analyze`, null, {
        params: { doc_id: docId, tone, focus, structure }
      });
      setAnalysisData(res.data.analysis);
      setReport(res.data.final_report);
      fetchHistory();
    } catch (err) {
      console.error(err);
      alert('Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFeedback = async () => {
    if (!docId) return;
    try {
      await axios.post(`${API_BASE}/feedback`, null, {
        params: { doc_id: docId, rating: feedback.rating, comments: feedback.comment }
      });
      setSubmittedFeedback(true);
      fetchHistory();
    } catch (err) {
      console.error(err);
    }
  };

  const downloadReport = () => {
    if (!report) return;
    const element = document.createElement("a");
    const file = new Blob([report], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `ClauseSense_Report_${docId?.slice(0, 8)}.txt`;
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="app-container">
      {/* Premium Navbar */}
      <nav className="navbar">
        <div className="nav-left">
          <div className="logo-icon">
            <Shield color="#fff" size={20} fill="rgba(255,255,255,0.2)" />
          </div>
          <div className="logo-text">ClauseSense AI</div>
        </div>

        <div className="nav-right">
          <div className="system-status">
            <div className="status-dot"></div>
            <span className="status-text">Backend Online</span>
          </div>
          <button
            className={`history-toggle-inline ${showHistory ? 'active' : ''}`}
            onClick={() => setShowHistory(!showHistory)}
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              padding: '0.6rem',
              borderRadius: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.8rem',
              fontWeight: 600
            }}
          >
            <History size={18} /> HISTORY
          </button>
        </div>
      </nav>
      <div className="bg-mesh"></div>

      {/* Background Decorative Blobs */}
      <div className="blob-container">
        <motion.div
          animate={{ x: [0, 100, 0], y: [0, 50, 0] }}
          transition={{ duration: 20, repeat: Infinity }}
          className="light-blob blob-1"
        ></motion.div>
        <motion.div
          animate={{ x: [0, -80, 0], y: [0, 120, 0] }}
          transition={{ duration: 15, repeat: Infinity }}
          className="light-blob blob-2"
        ></motion.div>
      </div>

      {/* History Sidebar */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ x: 400 }}
            animate={{ x: 0 }}
            exit={{ x: 400 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="history-sidebar"
          >
            <div className="history-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <History className="text-primary-red" />
                <h2>Recent Activity</h2>
              </div>
              <button className="close-btn" onClick={() => setShowHistory(false)}><X size={20} /></button>
            </div>
            <div className="history-list">
              {history.length === 0 ? (
                <div className="empty-history">
                  <p>No past actions recorded.</p>
                </div>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-item-header">
                      <span className={`action-type ${item.type.toLowerCase()}`}>{item.type}</span>
                      <span className="timestamp"><Clock size={10} /> {new Date(item.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="history-details">
                      {item.type === 'UPLOAD' && (
                        <p>Uploaded <strong>{item.details.filename}</strong></p>
                      )}
                      {item.type === 'ANALYZE' && (
                        <p>Analyzed contract (Doc: {item.details.doc_id.slice(0, 8)})</p>
                      )}
                      {item.type === 'FEEDBACK' && (
                        <p>Feedback: {item.details.rating} Stars</p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {!analysisData ? (
          <div className="landing-wrapper">
            <div className="landing-left">
              <motion.div
                key="landing"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                exit={{ opacity: 0, y: -20 }}
                className="hero-section"
              >
                <motion.h1 variants={itemVariants}>
                  AI to Read and <br />
                  <span>Analyze Legal Contract</span>
                </motion.h1>

                <motion.p variants={itemVariants}>
                  Advanced multi-agent semantic engine for high-fidelity legal reasoning, recursive risk extraction, and autonomous compliance auditing.
                </motion.p>


                <motion.div
                  variants={itemVariants}
                  className={`upload-card ${loading ? 'uploading' : ''}`}
                  onClick={() => fileInputRef.current?.click()}
                  style={{ margin: '0 0 2rem 0' }}
                >
                  {loading && <div className="upload-scanner"></div>}
                  <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleUpload}
                    accept=".pdf"
                  />
                  {loading ? (
                    <div style={{ position: 'relative' }}>
                      <Loader2 className="upload-icon loading animate-spin" />
                      <div className="progress-bar" style={{ width: '200px', margin: '0 auto' }}>
                        <motion.div
                          className="progress-fill"
                          initial={{ width: 0 }}
                          animate={{ width: `${uploadProgress}%` }}
                        ></motion.div>
                      </div>
                    </div>
                  ) : (
                    <Upload className="upload-icon" />
                  )}
                  <h3>{file ? file.name : "Upload PDF Contract"}</h3>
                  <p>{file ? (loading ? "Extracting document structure..." : "Document ready for processing") : "Support for Service Agreements, NDAs, and Leases"}</p>

                  {docId && !loading && !analyzing && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="upload-success-badge"
                    >
                      <CheckCircle2 size={16} /> READY TO ANALYZE
                    </motion.div>
                  )}
                </motion.div>

                {docId && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="analysis-action-container"
                  >
                    <motion.button
                      whileHover={{ scale: 1.02, boxShadow: '0 0 30px var(--primary-red-glow)' }}
                      whileTap={{ scale: 0.98 }}
                      className="generate-btn ultra-glow"
                      onClick={handleAnalyze}
                      disabled={analyzing}
                    >
                      {analyzing ? <Loader2 className="animate-spin" /> : <Zap size={20} fill="currentColor" />}
                      {analyzing ? 'ANALYZING DOCUMENT...' : 'GENERATE FULL REPORT'}
                    </motion.button>
                    <p className="helper-text">This will initiate the multi-agent reasoning phase</p>
                  </motion.div>
                )}
              </motion.div>
            </div>

            <motion.div
              className="landing-right"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 1 }}
            >
              <div className="neural-viz">
                <div className="neural-core"></div>
                <div className="neural-ring ring-1"></div>
                <div className="neural-ring ring-2"></div>

                {/* Random Neural Nodes */}
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="neural-node"
                    animate={{
                      opacity: [0.2, 1, 0.2],
                      scale: [1, 1.5, 1],
                    }}
                    transition={{
                      duration: 2 + Math.random() * 2,
                      repeat: Infinity,
                      delay: Math.random() * 2
                    }}
                    style={{
                      top: `${Math.random() * 100}%`,
                      left: `${Math.random() * 100}%`,
                    }}
                  />
                ))}

                <motion.div
                  className="doc-float"
                  animate={{ y: [0, -20, 0] }}
                  transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                >
                  <div className="scan-line"></div>
                  <FileText size={32} color="#ff3333" />
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>LEGAL_AGREEMENT.PDF</div>
                  <div style={{ height: 4, width: '100%', background: 'rgba(255,255,255,0.1)', borderRadius: 2 }}></div>
                  <div style={{ height: 4, width: '60%', background: 'rgba(255,51,51,0.3)', borderRadius: 2 }}></div>
                  <div style={{ height: 4, width: '80%', background: 'rgba(255,255,255,0.1)', borderRadius: 2 }}></div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="dashboard-grid"
          >
            <div className="analysis-main">
              <motion.div
                layout
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="analysis-domain-card"
              >
                <div className="domain-header"><ShieldCheck /> Legal Framework</div>
                <ul className="findings-list">
                  {analysisData.legal.key_findings.map((f: string, i: number) => (
                    <motion.li initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }} key={i}>{f}</motion.li>
                  ))}
                </ul>
                <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', background: 'rgba(255, 51, 51, 0.05)', borderRadius: '0.75rem', borderLeft: '3px solid #ff3333' }}>
                  <FileSearch size={18} color="#ff3333" />
                  <span style={{ fontSize: '0.9rem', color: '#ff7b7b', fontWeight: 600 }}>RISKS: {analysisData.legal.risks.join(', ')}</span>
                </div>
              </motion.div>

              <motion.div
                layout
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="analysis-domain-card"
              >
                <div className="domain-header"><TrendingUp /> Financial Exposure</div>
                <ul className="findings-list">
                  {analysisData.finance.financial_risks.map((f: string, i: number) => (
                    <motion.li initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }} key={i}>{f}</motion.li>
                  ))}
                </ul>
              </motion.div>

              <motion.div
                layout
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="analysis-domain-card"
              >
                <div className="domain-header"><CheckCircle2 /> Compliance Validation</div>
                <ul className="findings-list">
                  {analysisData.compliance.checks_performed.map((f: string, i: number) => (
                    <motion.li initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }} key={i}>{f}</motion.li>
                  ))}
                </ul>
              </motion.div>

              <motion.div
                layout
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="analysis-domain-card"
              >
                <div className="domain-header"><Activity /> Operational Continuity</div>
                <ul className="findings-list">
                  {analysisData.operations.optimization_suggestions.map((f: string, i: number) => (
                    <motion.li initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }} key={i}>{f}</motion.li>
                  ))}
                </ul>
              </motion.div>

              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="feedback-section glass"
              >
                <h3 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Service Quality Feedback</h3>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Help us maintain accuracy by rating the quality of this analysis.</p>
                {!submittedFeedback ? (
                  <>
                    <div className="stars">
                      {[1, 2, 3, 4, 5].map(n => (
                        <Star
                          key={n}
                          className={`star ${feedback.rating >= n ? 'active' : ''}`}
                          onClick={() => setFeedback({ ...feedback, rating: n })}
                          fill={feedback.rating >= n ? "gold" : "none"}
                          size={28}
                          style={{ cursor: 'pointer' }}
                        />
                      ))}
                    </div>
                    <textarea
                      placeholder="Any specific comments on accuracy..."
                      className="feedback-input"
                      rows={3}
                      value={feedback.comment}
                      onChange={e => setFeedback({ ...feedback, comment: e.target.value })}
                    />
                    <button className="generate-btn" style={{ maxWidth: '200px', margin: '0 auto' }} onClick={handleFeedback}>SUBMIT DATA</button>
                  </>
                ) : (
                  <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} style={{ color: 'gold', fontWeight: 700, marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
                    <CheckCircle /> FEEDBACK SUBMITTED
                  </motion.div>
                )}
              </motion.div>
            </div>

            <aside>
              <motion.div
                initial={{ x: 30, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="sidebar-card"
              >
                <button className="back-btn" onClick={() => {
                  setAnalysisData(null);
                  setDocId(null);
                  setFile(null);
                  setReport(null);
                }}>
                  <ArrowLeft size={16} /> BACK TO ENGINE
                </button>

                <div className="sidebar-section">
                  <div className="sidebar-title"><Command size={14} /> Report Tone</div>
                  <div className="option-group">
                    {['formal', 'concise', 'executive', 'risk-focused'].map(t => (
                      <button key={t} className={`option-btn ${tone === t ? 'active' : ''}`} onClick={() => setTone(t)}>
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="sidebar-section">
                  <div className="sidebar-title"><ChevronRight size={14} /> Structure</div>
                  <div className="option-group">
                    {['structured', 'bulleted'].map(s => (
                      <button key={s} className={`option-btn ${structure === s ? 'active' : ''}`} onClick={() => setStructure(s)}>
                        {s.charAt(0).toUpperCase() + s.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="sidebar-section">
                  <div className="sidebar-title"><ChevronRight size={14} /> Extraction Focus</div>
                  <div className="option-group">
                    {['full', 'legal', 'finance', 'compliance', 'operations'].map(f => (
                      <button key={f} className={`option-btn ${focus === f ? 'active' : ''}`} onClick={() => setFocus(f)}>
                        {f.charAt(0).toUpperCase() + f.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                <button className="generate-btn" onClick={() => { handleAnalyze(); setShowReport(true); }}>
                  RE-GENERATE BUFFER
                </button>

                {report && (
                  <motion.button
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="option-btn active"
                    style={{ marginTop: '1rem', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}
                    onClick={() => setShowReport(true)}
                  >
                    <FileText size={18} /> OPEN REPORT CONSOLE
                  </motion.button>
                )}
              </motion.div>
            </aside>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showReport && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="report-modal"
          >
            <motion.div
              initial={{ y: 100, scale: 0.9, rotateX: 20 }}
              animate={{ y: 0, scale: 1, rotateX: 0 }}
              exit={{ y: 100, scale: 0.9 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="report-content"
            >
              <button className="close-btn" onClick={() => setShowReport(false)} style={{ color: '#fff', padding: '10px' }}><X /></button>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
                <div>
                  <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Contract Analysis Report</h2>
                  <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Detailed breakdown and multi-domain extraction completed.</p>
                </div>
                <button className="generate-btn" style={{ padding: '0.75rem 1.5rem', width: 'auto' }} onClick={downloadReport}>
                  <Download size={18} /> Download RAW .txt
                </button>
              </div>

              <textarea
                readOnly
                className="report-textarea"
                value={report || ''}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Analysis Visualization BG for Dashboard */}
      {analysisData && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
          className="analysis-viz-bg"
        >
          <div className="data-core-pulse"></div>

          <div className="data-node-float dn-1">
            <ShieldCheck size={18} color="#34d399" /> <span>COMPLIANCE_OK</span>
          </div>

          <div className="data-node-float dn-2">
            <TrendingUp size={18} color="#fbbf24" /> <span>RISK_MATRIX_LOADED</span>
          </div>

          <div className="data-node-float dn-3">
            <Activity size={18} color="#60a5fa" /> <span>OPS_OPTIMIZED</span>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default App;
