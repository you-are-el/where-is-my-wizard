# Where Is My Wizard

This repository offers some python and web based tools for learning about how inscriptions are encoded on the Bitcoin blockchain. It consists of multiple individual python scripts that can be run using the instructions below as well as a Streamlit application that can be run locally or at www.whereismywizard.xyz.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install and set up the project, follow these steps:

1. Clone the repository: `git clone https://github.com/you-are-el/where-is-my-wizard.git`
2. Navigate to the project directory: `cd where-is-my-wizard`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment:
    - On macOS and Linux: `source venv/bin/activate`
    - On Windows: `venv\Scripts\activate.bat`
5. Install the required dependencies: `pip install -r requirements.txt`

## Usage

### Streamlit Application
To run the Streamlit application locally, follow these steps:

1. Make sure you have completed the installation steps mentioned above.
2. Activate the virtual environment: 
    - On macOS and Linux: `source venv/bin/activate`
    - On Windows: `venv\Scripts\activate.bat`
3. Run the Streamlit app: `streamlit run streamlit_app.py`
4. Open your web browser and navigate to `http://localhost:8501` to access the application.

### CLI Inscription Extraction Tool
You can run `python3 tx_id_to_file.py` to convert any kind of inscription data into a file and safe it to the project folder. The script will prompt you for a transaction id (e.g. `0301e0480b374b32851a9462db29dc19fe830a7f7d7a88b81612b9d42099c0ae`). It supports almost any file type except for recursive inscriptions and some 3D model files.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the [LICENSE](LICENSE) file for more details.


## Contact

If you have questions or ideas, I'd be happy to hear them. Just send me a DM on X [@you_are_el](https://twitter.com/you_are_el).
