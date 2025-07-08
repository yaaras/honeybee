# HoneyBee: Misconfigured App Generator


HoneyBee is a tool for creating misconfigured environments to test vulnerabilities in technologies like Jenkins, Jupyter Notebook, and more. 

With the help of LLMs, HoneyBee generates:
- **Dockerfiles** and **Docker-compose** files to replicate misconfigured applications.
- **Nuclei templates** to detect vulnerabilities (credit to a great template from the project [Fabric](https://github.com/danielmiessler/fabric)).
- **README files** with instructions on how to use the generated files.

## How It Works
- Choose a technology and a misconfiguration from a curated list of known issues, or write your own.
- HoneyBee uses LLMs to generate the required files and instructions to use them.

![HoneyBee](
images/img.png)

## Key Features

- **Misconfiguration Generator**:
  - Choose from a list of commonly misconfigured apps (e.g., Jenkins, Jupyter Lab).
  - Select a well-known misconfiguration (e.g., weak authentication, improper access control).
  - Automatically generate Dockerfiles and Docker-compose files tailored to your selections.

- **Detection Template Generator**:
  - Generate **Nuclei templates** to detect the created misconfiguration.

- **One-click test deployment**:
  - Deploy generated **docker-compose** files with one click and without leaving the browser.

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

2. Install using pip:

      ```bash
      pip install -e .
      ```

3. Set up your OpenAI API key:

    For OpenAI:

    ```bash
    export OPENAI_API_KEY=your_openai_api_key
    ```

    For Azure OpenAI:

    ```bash
    export AZURE_OPENAI_API_KEY=your_azure_api_key
    export AZURE_OPENAI_ENDPOINT=your_azure_endpoint
    ```

4. Setup docker compose (Optional):

    To enable the use of the local deployment feature simply [Install Docker Compose](https://docs.docker.com/compose/install/).


### Usage
Simply run the honeybee command
   ```bash
    honeybee
   ```
Open your browser and navigate to the URL provided by Streamlit (typically http://localhost:8501).
