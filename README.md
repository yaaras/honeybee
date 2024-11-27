# HoneyBee: Misconfigured App Generator

HoneyBee is a simple web application designed to streamline the creation of **misconfigured applications** for testing and educational purposes. Using Docker, HoneyBee allows you to select an application and a misconfiguration from a curated list of well-known vulnerabilities. With the power of GPT, the tool generates a Dockerfile that recreates the chosen misconfiguration. Additionally, HoneyBee provides templates for **Nuclei** and **OVAL** to help detect and manage the misconfiguration.

## Key Features

- **Misconfiguration Generator**:
  - Choose from a list of commonly misconfigured apps (e.g., Jenkins, Jupyter Lab).
  - Select a well-known misconfiguration (e.g., weak authentication, improper access control).
  - Automatically generate Dockerfiles tailored to your selections.

- **Detection Template Generator**:
  - Generate **Nuclei templates** to detect the created misconfiguration.
  - Generate **OVAL templates** for compliance and security testing.

- **Powered by GPT**:
  - Utilize GPT to craft accurate Dockerfile configurations and detection templates.

## Use Cases

- **Security Education**: Learn how misconfigurations arise and how to detect them.
- **Penetration Testing Practice**: Set up intentionally misconfigured environments for testing.
- **Tool Development**: Validate the effectiveness of security tools by running them against known misconfigurations.

## Getting Started

### Prerequisites

- Python 3.10 or above
- OpenAI API key 

### Installation

1. Clone the repository:
 ```bash
 git clone https://github.com/yaaras/HoneyBee.git
 cd HoneyBee
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
