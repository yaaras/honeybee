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
- Optional features
  - Docker compose
  - [Jina API token](https://jina.ai/)

### ⚡ Quick Setup ⚡

1. Run these commands:

    ```bash
    # Installs the latest release
    pip install pyhoneybee
    # Runs the honeybee server
    honeybee
    ```

Open your browser and navigate to the URL provided by Streamlit (typically http://localhost:8501).


### Developer Installation

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

5. Setup Jina API Token (Optional):

    To enable automatic extraction of misconfigurations from blogs or articles you need to provide a [Jina API token](https://jina.ai/)

    You can then set the token in the settings page or add it to your environment:

    ```bash
    export JINA_API_TOKEN=your_jina_api_key
    ```

### Usage

Simply run the honeybee command

   ```bash
    honeybee
   ```

Open your browser and navigate to the URL provided by Streamlit (typically http://localhost:8501).

## Examples

### 1. PostgreSQL - No Password Set

**Input:**
Misconfiguration: PostgreSQL with no password set

**Output:**

```yaml
services:
  db:
    container_name: 'db'
    environment:
      POSTGRES_DB: 'mydatabase'
      POSTGRES_PASSWORD:
      POSTGRES_USER: 'admin'
    image: 'postgres:13'
    logging:
      driver: 'json-file'
      options:
        max-file: '3'
        max-size: '10m'
    ports:
      - '5432:5432'
    restart: 'always'
    volumes:
      - 'db_data:/var/lib/postgresql/data'
version: '3.8'
volumes:
  db_data:
```

### 2. Grafana - Multiple Misconfigurations

**Input:**
Misconfigurations:

* Weak Admin Password
* Anonymous Access Enabled
* User Sign-Up Allowed
* Exposed Grafana Port

**Output:**

```yaml
services:
  grafana:
    container_name: 'grafana'
    environment:
      - 'GF_SECURITY_ADMIN_USER=admin'
      - 'GF_SECURITY_ADMIN_PASSWORD=admin'
      - 'GF_AUTH_ANONYMOUS_ENABLED=true'
      - 'GF_USERS_ALLOW_SIGN_UP=true'
    image: 'grafana/grafana:8.2.5'
    ports:
      - '3000:3000'
    volumes:
      - 'grafana_data:/var/lib/grafana'
version: '3.8'
volumes:
  grafana_data:
    driver: 'local'
```

