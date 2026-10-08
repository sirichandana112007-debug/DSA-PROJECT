# Intelligent Healthcare Resource Allocation & Appointment Optimization System

A complete full-stack web application for automated patient triage, hospital bed allocation, and multi-criteria optimization under capacity constraints.

---

## 📋 Mapping to Project Reviews

### Review 1: Problem Definition & Data Modeling
- **Entities**:
  - `Patient`: Clinical acuity score (1–5), required specialty, care tier, slot preference.
  - `Bed`: Department (Cardiology, Neurology, etc.), Care tier (ICU, Telemetry, Isolation, Standard), real-time status.
- **Database**: SQLite with SQLAlchemy ORM models (`app/models.py`).

### Review 2: System Architecture & Proposed Algorithm Engine
- **REST API**: FastAPI backend with automated OpenAPI/Swagger documentation (`/docs`).
- **Algorithms Evaluated** (`app/algorithms.py`):
  1. **Manual / FCFS**: First-come first-served baseline.
  2. **Greedy Only**: Immediate local best-fit allocation.
  3. **Exact Match Only**: Rigid attribute filtering with fallback.
  4. **Our Pipeline**: Priority-weighted Bipartite Matching using the Hungarian algorithm (`linear_sum_assignment`) with rolling-window optimization and cascading fallback.

### Review 3: Performance Validation & Comparative Benchmarks
- **Results on 10,000 Records**:
  - Appointment match rate: **93%** (Our pipeline) vs **83%** (Greedy), **60%** (Exact Match), **57%** (FCFS).
  - Bed utilization: **98%** (Optimal capacity maintained).
  - Admission rate: **76%** (Capacity-constrained).
- **Interactive Visualizations**: Embedded Chart.js grouped bar charts and downloadable publication-grade figures.

---

## 🚀 How to Run the Web Application

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Web Server
```bash
python run_server.py
```

### Step 3: Open in Web Browser
Open your browser and navigate to:
```
http://localhost:8000
```
- **Web UI Dashboard**: `http://localhost:8000`
- **Interactive API Swagger Docs**: `http://localhost:8000/docs`

---

## 🎯 Viva & Review Demo Workflow
1. **Show Bed Inventory**: Navigate to the *Hospital Bed Inventory* tab to show active beds categorized by specialty and tier (ICU, Telemetry, Isolation, Standard).
2. **Add / Generate Patients**: Click `+25 Sample Patients` or use the `Add Patient` modal to admit patients with different triage acuity levels.
3. **Run Allocation Comparison**:
   - Choose `Manual / FCFS` and run allocation. Note the lower match rate (~57%).
   - Click `Reset Beds` and switch to `Our Pipeline (Priority Bipartite Hungarian)`. Run allocation to show the jump to ~93% match rate!
4. **Present Review 3 Benchmark**: Navigate to the *Review 3: Benchmark & Evaluation* tab to show the grouped bar chart and comparative analysis table.
