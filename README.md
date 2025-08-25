# Master Program — Integrated Desktop Suite (SMT • Firetest • QR)

> A production-grade desktop application that unifies three specialized engineering tools—**SMT (MLCC Design & Buildsheet Automation)**, **Firetest Analytics**, and **QR Code Generator**—into a single, elegant UI. The suite eliminates command‑line friction, captures engineering know‑how, and turns it into a scalable, auditable workflow.

---

## 🔭 What’s inside
This repository is the **parent / master project**. The **MLCC Design Automation** work is embedded here as part of the **SMT module** (see `src/SMT/Design_Automation` and `src/SMT/Buildsheet_Automation`). Two presentations in the repo describe that subsystem in depth:

- **`1. MLCC Automation.pptx`** — High‑level overview and problem framing for MLCC automation.
- **`2. Design Automation Process.pptx`** — Detailed solution methodology, decision flow, inputs/outputs.

For the **desktop application** itself, refer to:

- **`Master Program Documentation.pdf`** — The companion guide that explains the master app’s modules, screens, and end‑to‑end usage.

---

## 🧭 Why this project exists
Engineering teams often juggle disjointed scripts and spreadsheets for **MLCC design**, **test analytics**, and **QR flows**. This master app fuses them into one UI to deliver:

- **Speed & Scale** — Batch processing for MO/PN lists, bulk test analysis, and QR generation.
- **Accuracy & Repeatability** — Deterministic calculations, database‑backed lookups, and guardrails.
- **Usability** — A clean desktop UI (no terminal) with inline validation, theming, and logging.
- **Auditability** — Structured outputs (PDF/PRN/HTML/XLSX) and archival folders for every run.

---

## 🖥️ The Desktop App (UX + Tech)
- **Technology**: Python desktop UI built with Qt (UI defined in `ui/main_window.ui`, auto‑compiled to `ui_main_window.py`).  
- **Single entry point**: `main.py` starts the unified shell where users select a module and run tasks end‑to‑end.  
- **Frictionless interaction**: File pickers, progress messages, theme toggle (dark/white in Firetest), and error prompts.  
- **Config & Styling**: QSS & JSON styles under `qss/` and `json_styles/` (icons and fonts in `assets/`).  
- **User state**: `assets/user_data.json` stores registration and light preferences.  
- **Logging**: `logs/` captures runtime diagnostics; helpful for support and traceability.
- **Shortcuts & UX sugar**: `shortcut_handler.py` and `messagebox.py` standardize app‑wide behaviors.

> The result: **engineers click through complex pipelines without touching code**, while power‑users still benefit from transparent, scriptable components behind the scenes.

---

## 🧩 Modules at a glance

### 1) SMT — MLCC Design & Buildsheet Automation
**Purpose**: Convert **Part Number + MO#** lists into **validated MLCC designs** and **production‑ready buildsheets**.

**Sub‑systems**  
- **Design Automation** (`src/SMT/Design_Automation/`):  
  - Parses **Global/Legacy PNs**, translates **LPN ↔ GPN**, validates obsolescence.  
  - Maps **Subfamily → Dielectric (X7R/X8R/NP0)** and **BME/PME** families.  
  - Pulls constants and constraints from curated Excel sources (active layer thickness limits by voltage and design type, case size tables, dielectric constants *k*, mappings).  
  - Computes design parameters (active area, margins, dielectric thickness within preferred/acceptable limits, number of plates & active layers, print tape thickness), with **shrinkage** and **scale factor** adjustments.  
  - Iterates through **design types and dielectric options** with graceful fallbacks; on success, writes the calculated design file.

- **Buildsheet Automation** (`src/SMT/Buildsheet_Automation/`):  
  - Updates the **NCCDB.xlsx** and runs **Excel macro(s)** in `NCC LAYER BUILD SHEET MAKER.xlsm`.  
  - Exports **BuildSheet** as **PDF** and **PRN** into `SMT Output Folder/`.  
  - Optional: auto‑email or share outputs for approval.

**UX flow (Desktop App)**  
1. Choose the **input `.txt`** containing PN/MO# pairs and select an **output folder**.  
2. Follow prompts (where applicable) for **dielectric options (PME formulas)**, **shrinkage**, and **scale factor**.  
3. Review generated **design files**, then **create the BuildSheet**.  
4. View PDFs/PRNs; send for approval.

> **System requirement**: Microsoft **Excel must be installed** on the machine to run the Buildsheet macro path.

**Where to learn more**  
- See **`1. MLCC Automation.pptx`** and **`2. Design Automation Process.pptx`** for the full algorithm, decision tree, and data sources.


### 2) Firetest — Analysis & Reporting
**Purpose**: Turn raw **fire test** data into **clean analytics**, **tolerance yield**, and **publication‑ready charts**.

**Capabilities**  
- Single‑file run: upload the data sheet and run; view **filtered/unfiltered** outputs and **dark/white** themed charts.  
- Batch runs: point to input/output folders and auto‑generate **HTML reports** for both filtered and unfiltered data in **dark/white** themes.  
- Generate **output tables** and **tolerance yield** tables; archive to an **Excel Database** for history.

**Key scripts**  
- `firetest_handler.py` (UI orchestration)  
- `yield_of_tolerance.py` (yield calculations)  
- `firetest_Final_Dark.py`, `firetest_Final_White.py` (plot pipelines)  
- `src/Firetest/src/batch_testing.py` (large‑scale reporting)


### 3) QR Code Generator — Manufacturing & Traveler Flows
**Purpose**: Generate, compare, and log QR codes for manufacturing travelers and operators.

**Capabilities**  
- One‑shot **QR generation** (outputs to `QR CODE PDFs/`).  
- **Comparison mode**: enter operator + traveler info; on match, update the Excel record.  
- All inputs/outputs tracked in `qr_data.xlsx`; configuration via text/JSON options under `src/QR/assets/`.

---

## 📦 Installation
```bash
pip install -r requirements.txt
python main.py
```

> On first run, verify Excel availability if you plan to use the **SMT Buildsheet** path.

---

## 🚦 Usage (quickstarts)

### SMT
- Choose **PN/MO# `.txt`** + **output folder** → follow prompts → review **design files** → **create BuildSheet** → share PDFs/PRNs.  
- Outputs land under **`SMT Output Folder/`**; design and database updates are handled automatically.

### Firetest
- **Single file**: select the Excel, choose theme (dark/white), and run.  
- **Batch**: select input + output folders; HTML reports are created for filtered/unfiltered data in both themes.  
- Results are saved and consolidated to the project's **Database.xlsx**.

### QR
- Enter required fields; generate the QR PDF.  
- Compare operator/traveler codes; on match, data is appended to **qr_data.xlsx**.

---

## 📁 Repository structure (high‑level)
```
README.md
requirements.txt
main.py
ui/
  └─ main_window.ui
src/
  ├─ SMT/
  │   ├─ Buildsheet_Automation/
  │   │   ├─ buildsheet_automation.py
  │   │   ├─ NCCDB.xlsx
  │   │   └─ NCC LAYER BUILD SHEET MAKER.xlsm
  │   └─ Design_Automation/
  │       ├─ assets/        # reference Excel files for rules, mappings, constants
  │       └─ src/
  │           ├─ design.py
  │           ├─ dielectric.py
  │           ├─ layers.py
  │           ├─ part_information.py
  │           ├─ text_file_processing.py
  │           └─ translation.py
  ├─ QR/
  │   ├─ assets/            # options .txt/.json
  │   ├─ qr_data.xlsx
  │   └─ qr_handler.py
  └─ Firetest/
      ├─ assets/            # Mapping.xlsx for tables/plots
      ├─ src/
      │   ├─ batch_testing.py
      │   ├─ firetest_Final_Dark.py
      │   └─ firetest_Final_White.py
      ├─ data.xlsx
      ├─ Database.xlsx
      └─ firetest_handler.py
qss/ (and icons/)
json_styles/
assets/ (icons/, fonts/, user_data.json)
logs/
generated-files/
SMT Output Folder/
QR CODE PDFs/
text_file.TXT
1. MLCC Automation.pptx
2. Design Automation Process.pptx
Master Program Documentation.pdf
```

---

## 🛡️ Design principles & quality bars
- **Deterministic core + recoverable fallbacks** (no silent failures; iterate over design types/options).  
- **Separation of concerns** (UI orchestrates; module scripts compute; assets store domain data).  
- **Traceability** (logs + structured outputs).  
- **Human‑in‑the‑loop** where it matters (engineer approval for BuildSheets).

---


## ✨ Value at a glance
This suite turns a **maze of expert steps**—MLCC design rules, test analytics, and traveler QR control—into a **one‑click experience**. It preserves domain depth while radically simplifying day‑to‑day work for production, QA, and process engineering teams.
