# 📊 eSocial XML to Excel Processor

Python automation for reading, processing, and transforming eSocial XML files into a structured dataset ready for analysis in Excel.

---

## 📌 Overview

This project was built to automate the conversion of eSocial XML files into a structured dataset, reducing manual work and making fiscal data easier to analyze.

The script performs:
- XML parsing with namespace handling
- Extraction of relevant data per company (CNPJ)
- Financial calculations
- Data transformation and aggregation
- Excel report generation with multiple sheets

---

## ⚙️ Technologies Used

- Python 3.x  
- xml.etree.ElementTree (XML parsing)  
- pandas (data manipulation and analysis)  
- numpy (numerical operations)  
- openpyxl (Excel export)  

---

## 📥 Input

eSocial XML file containing:
- Company data (ideEstab)
- Tax codes (tpCR)
- Assessed values (vrCR)
- Suspended values (vrSuspCR)
- Indicators such as:
  - RAT
  - FAP
  - Adjusted RAT rate

---

## 📤 Output

An Excel file automatically generated with two sheets:

### 1. XML
Contains raw extracted data:
- Formatted CNPJ  
- Tax code  
- Assessed and suspended values  
- Difference  
- RAT, FAP, and adjusted rate  

### 2. Base by Code and Company
Processed dataset with:
- Data grouped by CNPJ  
- Pivoted tax codes (columns)  
- Aggregated totals  
- Calculated indicators  

---

## 🔄 Processing Steps

### 1. XML Parsing
- Reads the XML file with error handling
- Uses namespace to correctly navigate nodes
- Extracts data from ideEstab elements

### 2. Data Extraction
For each company:
- Formats the CNPJ
- Extracts:
  - Tax codes
  - Financial values
  - Fiscal indicators

### 3. Data Transformation
- Builds a DataFrame using pandas
- Calculates the difference: difference = assessed_value - suspended_value
- Filters relevant tax codes

### 4. Data Structuring
- Pivots data (rows → columns)
- Groups by CNPJ
- Handles missing values

### 5. Business Logic
Creates aggregated fields:

- Company  
  Sum of selected tax codes (e.g., 1082-01, 1138-01)

- Third Parties  
  Sum of multiple related tax codes

- RAT  
  Aggregation of specific charges

### 6. Export
- Writes Excel file with multiple sheets using openpyxl
- Separates raw and processed data

---

## 🧠 Key Features

- Handles complex XML structures with namespaces  
- Resilient to missing data  
- Transforms data into an analysis-ready format  
- Fully automates a manual process  
- Ready for integration with BI tools (Power BI, etc.)

---

## 🚀 How to Run

1. Install dependencies:
- pip install pandas numpy openpyxl

2. Place your XML file in the same directory as the script

3. Update the file name in the code:
- arquivo_xml = 'your_file.xml'
  
4. Run the script:
- python script.py

---

## 📁 Project Structure
project/
│
├── script.py
├── eSocial_xxx.xml
└── XML_Convertido.xlsx


---

## ⚠️ Notes

- The XML must follow the eSocial structure  
- The namespace must be correctly defined in the code  
- Tax codes can be adjusted based on requirements  

---

## 💡 Possible Improvements

- Web interface for XML upload  
- Database integration  
- Automated dashboard (Power BI / Streamlit)  
- Advanced data validation  
- Batch processing for multiple files  

---

## 📌 Use Cases

- Fiscal process automation  
- Accounting and tax analysis  
- Reducing manual spreadsheet work  
- Preparing data for BI tools  

---

## 👨‍💻 Author

Developed by Filipe Mendes  
Focused on process automation and data analysis  
