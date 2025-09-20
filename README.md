# 📦 Streamlit PIM Lite

A lightweight **Product Information Management (PIM)** dashboard built with **Streamlit**, designed for exploring and validating product metadata (SKU, URLs, images, materials, etc.).  
This repo demonstrates:
- a data science project turned into an interactive Streamlit app
- proper testing of data import/filter utilities
- containerization with Docker
- automated CI/CD via GitHub Actions

---

## 🚀 Features

- Upload an Excel file or reopen the last used file  
- Automatic data cleaning:
  - removes ghost/empty columns  
  - coerces columns into correct datatypes  
  - formats `Added` date column  
- Completeness check (`Macro Material_`, `Main Color_`, `Shape_`, `Carry_`)  
- Interactive grid with:
  - editable cells
  - dropdowns with highlights
  - image previews
  - clickable URLs
- Containerized with Docker for easy deployment  

---

## 📂 Project Structure

```
Streamlit-PIM/
│
├── tool/
│   └── pim_app/
│       ├── __init__.py
│       ├── io_utils.py        # Excel reading + cleaning
│       └── metrics.py         # Completeness metrics
│
├── tests/                     # Unit tests (pytest)
│   ├── test_io_utils.py
│   ├── test_metrics.py
│   ├── test_imports.py
│   └── test_smoke.py
│
├── streamlit_app.py           # Main Streamlit application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── pytest.ini                 # Test discovery config
└── .github/workflows/ci.yml   # CI pipeline (tests + Docker build)
```

---

## 🖥️ Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/Streamlit-PIM.git
cd Streamlit-PIM
```

### 2. Install dependencies
It’s best to use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run streamlit_app.py
```

Go to 👉 http://localhost:8501

---

## ✅ Running Tests

We use `pytest` for data import/cleaning/metric utilities.

```bash
pytest -q
```

All tests must pass before merging. Example output:
```
collected 4 items

tests/test_io_utils.py ..    [ 50%]
tests/test_metrics.py .      [ 75%]
tests/test_smoke.py .        [100%]

4 passed in 0.23s
```

---

## 🐳 Running with Docker

### 1. Build the image
```bash
docker build -t streamlit-pim .
```

### 2. Run the container
```bash
docker run -p 8501:8501 streamlit-pim
```

Now visit 👉 http://localhost:8501

---

## ☁️ DockerHub (Optional)

If you push your image to Docker Hub, others can run it directly:

```bash
docker pull <your-dockerhub-username>/streamlit-pim:latest
docker run -p 8501:8501 <your-dockerhub-username>/streamlit-pim:latest
```

---

## ⚙️ Continuous Integration (CI/CD)

We use **GitHub Actions** to ensure code quality and automate Docker builds.

- On every push / pull request → run tests (`pytest`)  
- On creating a tag like `v1.0.0` → build & push Docker image to Docker Hub  

See: `.github/workflows/ci.yml`

### Triggering a release
```bash
git tag v1.0.0
git push origin v1.0.0
```

This will publish:
- `your-dockerhub-username/streamlit-pim:v1.0.0`
- `your-dockerhub-username/streamlit-pim:latest`

---

## 📖 Assignment Deliverables

- **GitHub Repo**: [https://github.com/ChloeeFan/Streamlit-PIM]
- **Dockerhub Repo**: [https://hub.docker.com/repository/docker/13987133805fjy/streamlit-pim/general]

---

## 📝 License

MIT License — feel free to use, modify, and share.
