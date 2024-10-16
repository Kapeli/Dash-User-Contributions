Azure Resource Manager Template Reference
=======================

**Author: Milad Beigi**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/miladbeigi/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-lightgrey)](https://github.com/your-github-username)

Use [this](https://github.com/miladbeigi/azure-arm-docset-gen) repository to get the latest versions of HTML docs for the Azure Resource Manager template reference. The script also processes the HTML files to create a docset for use in Dash.

## Prerequisites
- Python 3.10.9 or later

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/miladbeigi/azure-arm-docset-gen.git
    ```
2. Run the following command to install the required Python packages and save the HTML files:
    ```bash
    make install
    ```
3. Run the following command to generate the docset:
    ```bash
    make build
    ```