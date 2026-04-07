# 🍕 PizzaSalesIQ – Production-Ready Business Intelligence & Forecasting

**PizzaSalesIQ** is a comprehensive, data-driven business intelligence dashboard and inventory forecasting application. Built for retail food operations, it helps minimize inventory waste and improve demand forecasting by transforming raw Point of Sale (POS) transaction data into actionable operational insights.

This project goes beyond simple data visualization by implementing a production-grade architecture, including decoupled machine learning training, memory-efficient data caching, and a highly optimized Streamlit user interface.

---

## 🚀 Key Features & Business Value

* **Interactive BI Dashboard (`app.py`):** A polished, tabbed dashboard built with Streamlit, offering modular views into Executive Summaries, Trends, Pizza Analytics, and Customer Behavior.
* **Time-Series Forecasting (`predict.py`):** Uses Holt-Winters Exponential Smoothing (`statsmodels`) to predict next week's demand for every specific pizza variant and size.
* **Decoupled ML Architecture:** Separates heavy model training (`train_model.py`) from user-facing inference, ensuring the frontend dashboard remains lightning-fast.
* **Optimized Performance:** Utilizes `@st.cache_data` and `@st.cache_resource` for efficient memory management, preventing redundant data loading and model instantiations.
* **Data-Driven Insights:** Automatically highlights actionable intelligence, such as peak order hours, optimal discount strategies, and high-margin product bundles.

---

## 📌 Business Insights & Actions

This analysis uncovered key sales and operational patterns that can help pizza outlets make smarter business decisions:

| 📊 Metric | 💡 Insight | ✅ Action |
|----------|------------|----------|
| **Most Popular Pizza** | Farmhouse pizza has the highest number of units sold | Ensure adequate inventory of ingredients like capsicum, onions, and cheese |
| **Top Revenue Generator** | Loaded pizza brings in the most revenue, though not most sold | Maintain ingredient stock; offer combo deals or targeted promotions |
| **Most Preferred Size** | Medium-sized pizzas are most frequently ordered | Produce more medium-sized dough and optimize packaging accordingly |
| **Peak Sales Hours** | 12 PM – 2 PM and 6 PM – 12 AM | Schedule extra kitchen & delivery staff during these hours |
| **Best Sales Months** | August and October (festival season) | Stock up in advance; consider premium pricing during high-demand periods |
| **Discount Usage Pattern** | Most discount codes are used on weekends | Design weekend-only campaigns; evaluate ROI from each discount type |
| **Weekend/Festival Trends** | Sales surge on weekends and festivals | Plan staffing, inventory, and marketing around key dates |

---

## 📊 The Dataset

To simulate a real-world enterprise environment, this project utilizes a curated composite dataset containing approximately **1.4 million records**. 

In retail, excess inventory and inaccurate demand forecasting lead to significant food waste. This dataset faithfully represents the granular, item-level transaction data collected daily by Point of Sale (POS) systems. By analyzing these weekly, seasonal, and event-based demand trends, the application accurately estimates upcoming inventory requirements.

### 🧮 Data Dictionary

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `order_id` | String | Unique order ID; multiple pizzas per order |
| `pizza_name` | String | Name of pizza variant (e.g., Farmhouse) |
| `pizza_size` | String | Size of pizza (S, M, L) |
| `quantity` | Integer | Number of pizzas ordered |
| `price` | Float | Unit price per pizza |
| `total_bill_amount` | Float | Total amount for the order |
| `discount` | Float | Discount value applied |
| `discount_type` | String | Type of discount (e.g., weekend, festival) |
| `is_holiday` | Boolean | Flag if the date was a holiday |
| `is_weekend` | Boolean | Flag if the order was on a weekend |
| `is_friday_night`| Boolean | Flag for Friday night orders |
| `is_festival` | Boolean | Flag for festival day |
| `order_date` | Date | Date of the order (YYYY-MM-DD) |
| `order_time` | Time | Time of the order (HH:MM:SS) |

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Frontend / UI:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** Statsmodels (Exponential Smoothing), Scikit-learn
* **Serialization:** Joblib
* **Visualization:** Matplotlib

---

## 📂 Project Architecture

```text
PizzaSalesIQ/
├── data/                       # Contains all aggregated CSV datasets
│   ├── 1.csv                   # Last week's pulse data
│   ├── pizza_sales_data23.csv  # Main overall dataset
│   └── ... (other CSVs)
├── models/
│   ├── train_model.py          # Offline ML training script
│   └── pizza_models.pkl        # Serialized pre-trained forecasting models
├── utils/
│   └── data_loader.py          # Modular data loading with Streamlit caching
├── app.py                      # Main BI Dashboard application
├── predict.py                  # Real-time ML Inference dashboard
└── requirements.txt            # Explicit Python dependencies
```

### 💻 Installation & Local Setup

## To run this project locally, it is highly recommended to use a Python Virtual Environment to manage dependencies cleanly.

## 1. Clone the repository:
```bash
git clone [https://github.com/yourusername/PizzaSalesIQ.git](https://github.com/yourusername/PizzaSalesIQ.git)
cd PizzaSalesIQ
```

## 2. Create and activate a Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 🏃‍♂️ Usage Guide

## Step 1: Train the Forecasting Models

## Before running the prediction dashboard, you must train the machine learning models on the historical data. This script processes the data, trains an Exponential Smoothing model for every pizza/size combination, and saves them to disk.

```bash
cd models
python train_model.py
```

## Step 2: Launch the Dashboards

## Return to the root directory and use Streamlit to launch the applications.

# To view the Business Intelligence Dashboard:
```bash
cd ..
streamlit run app.py
```
# To view the real-time AI Forecasting Tool:
```bash
cd ..
streamlit run predict.py
```

### 📥 Data Download Instructions
Due to GitHub's file size limits, the main dataset (`pizza_sales_data23.csv`) is not hosted in this repository. 

To run this project locally, please download the dataset from the source link below and place it inside the `data/` folder before running the app.

* **Dataset Link:** [pizza_sales_data23.csv](https://drive.google.com/file/d/1O-w4lcOfpSgF9cTy8a9rWrwxZ3yf8AIt/view?usp=drive_link)
* **Expected File Name:** `pizza_sales_data23.csv`

## 🙋‍♀️ Author

<table>
  <tr>
    <td>
      <strong>Ishita Amin</strong><br/>
      👩‍💻 B.Tech CSE @ Navrachana University<br/>
      📬 <a href="mailto:aminishita30@gmail.com">aminishita30@gmail.com</a><br/>
      🔗 <a href="[https://linkedin.com/in/ishitaamin](https://www.linkedin.com/in/ishita-amin-841726253)" target="_blank">LinkedIn</a><br/>
    </td>
  </tr>
</table>

---

