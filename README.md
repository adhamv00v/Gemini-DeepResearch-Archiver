English | [日本語 (Japanese)](README.ja.md)

# Gemini-DeepResearch-Archiver
Capture & archive Google Gemini Deep Research as local Markdown (Obsidian-ready)

**Gemini-DeepResearch-Archiver** is an open-source archiver designed to locally save  
Google Gemini's *Deep Research* output — including the parts that cannot be retrieved  
via browser extensions or DOM scraping.

Since Gemini renders Deep Research through batched RPC responses, the content is not  
accessible from the webpage itself. This project bypasses that limitation by using  
**mitmproxy** to capture raw network traffic and extract the final research report  
directly from the response payload.

All extracted data is automatically converted into clean Markdown with YAML  
frontmatter, optimized for tools like **Obsidian**. Additionally, the archiver creates  
**bi-directional links** between chat sessions and Deep Research notes.

---

## 🚀 Features

### ✔ Extracts the *final* Deep Research report
- Parses Gemini's `batchexecute` network calls
- Identifies and decodes `wrb.fr` payloads
- Extracts only the *final report* (not intermediate reasoning)
- Removes duplicate H1 titles for clean Markdown formatting

### ✔ Obsidian-ready Markdown output
- Adds YAML frontmatter (`title`, `date`, `tags`, `source_chat`)
- Preserves the structure and sections of the Gemini report
- Clean formatting for easy reading and further processing

### ✔ Chat note generation with bi-directional links
- Creates a chat session note for each capture session
- Links each Deep Research file back to its originating session
- Links chat → DR and DR → chat

### ✔ Batch processing from raw logs
- Reads all captured mitmproxy logs in `captured_data/`
- Parses multiple Deep Research blocks per session
- Handles filename conflicts automatically

---

## 📁 Project Structure


```
Gemini-DeepResearch-Archiver/
├ addon_raw_logger.py        # mitmproxy addon for raw log capture
├ dr_chat_batch_parse.py     # Deep Research + Chat parser
│
├ captured_data/             # raw mitmproxy logs (input)
├ dr_output/                 # generated Deep Research notes (output)
├ chat_output/               # generated chat session notes (output)
│
├ setup/
│ ├ setup_windows.bat        # initial environment setup
│ ├ start_capture.bat        # starts mitmproxy + opens Gemini automatically
│ └ stop_capture.bat         # stops mitmproxy
│
├ docs/                      # optional diagrams or documentation
├ example/                   # anonymized sample logs
│
├ LICENSE                    # MIT License
└ README.md                  # (this file)
```
---

## 🛠 Installation

### 1. Install Python (3.9–3.12 recommended)

Verify:
```
python --version
```
### 2. Install dependencies
```
pip install mitmproxy
```
### 3. Install mitmproxy root certificate (required for HTTPS decryption)
Run:
```
mitmproxy
```
Open the following URL:
```
http://mitm.it
```
Then install the certificate for your OS and browser.
---
## 🧪 Usage
### Step 1: Start capture
```
mitmweb -s addon_raw_logger.py
```
Or simply run:
```
setup/start_capture.bat
```
This will:
- Start mitmproxy  
- Automatically open Google Gemini in your browser  

### Step 2: Perform a Deep Research query  
Once the final Deep Research report is displayed, the raw network logs will be stored in `captured_data/`.

### Step 3: Parse logs & generate Markdown

```
python dr_chat_batch_parse.py
```

This produces:

- `dr_output/` — Deep Research notes  
- `chat_output/` — Chat session notes with links  

### Step 4: Import into Obsidian  
Move or link these folders into your Obsidian Vault.
---
## 📄 Example Output (Deep Research Note)

```
---
title: Workflow from 3DCG to 3D Printing
date: 2025-11-30
tags: [DeepResearch, Gemini]
source_chat: [[2025-11-30_18-09-35_993_batchexecute-Session]]
---

# Workflow from 3DCG to 3D Printing

## 1. Overview of Modeling Requirements
（content）

---

## Source Chat
[[2025-11-30_18-09-35_993_batchexecute-Session]]
```

---

## 🔒 Security Notice (IMPORTANT)

Because this project uses **HTTPS interception (MITM)** via mitmproxy:

- The mitmproxy root certificate allows decryption of *all* HTTPS traffic  
- Never use this tool on shared computers or public networks  
- Only run it in trusted local environments  
- Only use it on your *own* Gemini account  
- You are responsible for any legal or security risk associated with HTTP interception

---

## 📌 Roadmap

- [ ] Fully automated workflow (Chrome Extension + Local Server + mitmproxy)
- [ ] Extract chat transcripts in addition to Deep Research
- [ ] Optional export for RAG systems (JSON / chunked text)
- [ ] Optional Obsidian autosync
- [ ] GitHub Actions for tests & linting
- [ ] Package distribution via PyPI

---

## 🤝 Contributing

Contributions are welcome!  
Please submit an Issue or Pull Request if you want to help improve this project.

---

## 📄 License

This project is licensed under the **MIT License**.  
See `LICENSE` for details.