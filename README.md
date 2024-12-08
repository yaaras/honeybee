# HoneyBee: Misconfigured App Generator


HoneyBee is a tool for creating misconfigured environments to test vulnerabilities in technologies like Jenkins, Jupyter Notebook, and more. 

With the help of LLMs, HoneyBee generates:
- **Dockerfiles** to replicate misconfigured applications.
- **Nuclei templates** to detect vulnerabilities.
- **OVAL rules** for detection Host Misconfigurations.

## How It Works
- Choose a technology and a misconfiguration from a curated list of known issues, or write your own.
- HoneyBee uses AI to generate the required files.

![HoneyBee](
images/Honeybee_screenshot.png)

## Try It Out
The app is live and running! Access HoneyBee at [http://16.170.7.44:8501](http://16.170.7.44:8501) (using Twingate VPN)

## Key Features

- **Misconfiguration Generator**:
  - Choose from a list of commonly misconfigured apps (e.g., Jenkins, Jupyter Lab).
  - Select a well-known misconfiguration (e.g., weak authentication, improper access control).
  - Automatically generate Dockerfiles tailored to your selections.

- **Detection Template Generator**:
  - Generate **Nuclei templates** to detect the created misconfiguration.
  - Generate **OVAL templates** for compliance and security testing.

## Getting Started

### Prerequisites

- Python 3.10 or above
- OpenAI API key 

### Installation

1. Clone the repository:
 ```bash
 git clone https://github.com/yaaras/honeybee.git
 cd honeybee
  ```
2.	Install the required dependencies:
 ```bash
 pip install -r requirements.txt
 ```

3.	Run the application:
 ```bash
  streamlit run app.py
 ```

4.	Open your browser and navigate to the URL provided by Streamlit (typically http://localhost:8501).
