# AI-Driven Drug Discovery Platform for Neglected Diseases

A comprehensive, cross-platform AI-driven drug discovery web application focused on neglected diseases, integrating molecular analysis, visualization, and predictive technologies.

## Features

- **Compound Database:** Search and explore a database of chemical compounds with detailed molecular information
- **Molecular Visualization:** 2D and 3D visualization of molecular structures
- **Target Identification and Validation:** Find potential drug targets based on disease and other criteria
- **Compound Screening and Ranking:** Screen and rank compounds against specific disease targets
- **ADMET Prediction:** Predict Absorption, Distribution, Metabolism, Excretion, and Toxicity properties
- **Binding Affinity Prediction:** Predict binding affinity between compounds and targets
- **Interactive Dashboard:** Visualize data trends and distributions in the database
- **Lipinski's Rule Analysis:** Check drug-likeness with Lipinski's Rule of Five

## Technology Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** PostgreSQL 
- **Cheminformatics:** RDKit
- **Machine Learning:** scikit-learn, NumPy
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Visualization:** Chart.js, RDKit.js

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 13+
- RDKit
- Git

### Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/drug-discovery-platform.git
   cd drug-discovery-platform
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file with the following variables:
     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/drug_discovery
     SESSION_SECRET=your_secret_key
     ```

6. Initialize the database:
   ```
   python data_seeder.py
   ```

7. Run the application:
   ```
   python main.py
   ```

8. Access the application at `http://localhost:5000`

## Packaging for Windows

### Creating a Windows Executable

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --name DrugDiscoveryPlatform --onefile --add-data "templates;templates" --add-data "static;static" --icon=icon.ico main.py
   ```

3. The executable will be created in the `dist` directory.

4. For a complete Windows installer, you can use tools like NSIS (Nullsoft Scriptable Install System) or Inno Setup to create an installer package.

### Running on Windows

1. Install PostgreSQL on your Windows system
2. Set up the required database and environment variables
3. Run the executable file

## Packaging for Android

### Method 1: Using Termux (Command Line)

1. Install Termux from Google Play Store or F-Droid
2. Install Python and dependencies:
   ```
   pkg update && pkg upgrade
   pkg install python postgresql git
   git clone https://github.com/yourusername/drug-discovery-platform.git
   cd drug-discovery-platform
   pip install -r requirements.txt
   ```
3. Configure PostgreSQL and run the application

### Method 2: Packaging as a WebView App

1. Install Android Studio and create a new project
2. Add a WebView to your main activity to display the web interface:
   ```java
   WebView webView = findViewById(R.id.webView);
   webView.getSettings().setJavaScriptEnabled(true);
   webView.loadUrl("http://your-server-address:5000");
   ```
3. Alternatively, use frameworks like Cordova or Capacitor to wrap your web application

### Method 3: Using Python-for-Android

1. Use [Python-for-Android](https://python-for-android.readthedocs.io/en/latest/) to package your Flask app:
   ```
   pip install python-for-android
   ```
2. Create a spec file (app.spec) defining your app requirements
3. Build your app:
   ```
   p4a create --requirements=flask,sqlalchemy,rdkit --bootstrap=webview --orientation=portrait --permission=INTERNET
   ```

## API Documentation

The platform offers several API endpoints for integration with other systems:

- `GET /api/compounds` - Get a filtered list of compounds
- `GET /api/compound/{id}/structure` - Get structure information for a compound

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- RDKit team for the cheminformatics toolkit
- scikit-learn team for the machine learning tools
- Flask and SQLAlchemy for the web framework and ORM