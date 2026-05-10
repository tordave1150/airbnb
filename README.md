# 🏠 Airbnb Analytics Dashboard

A multi-page Streamlit dashboard powered by MongoDB's **sample_airbnb** dataset.

## Pages

| Page | Description |
|------|-------------|
| 🏠 **Overview** | KPIs, global distribution, room types, price & review summaries |
| 💰 **Price Analysis** | Pricing by geography, property type, bedrooms, fee breakdown |
| ⭐ **Reviews & Ratings** | Category scores radar, superhost impact, rating distributions |
| 👤 **Host Analysis** | Superhost vs regular, multi-listing strategies, response rates |
| 🌍 **Geographic Analysis** | Choropleth maps, market treemaps, scatter geo, availability |
| 🏡 **Amenities & Features** | Top amenities, price premium analysis, bed/capacity specs |

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB connection
The dashboard connects to MongoDB Atlas using the sample dataset connection.
Update the connection string in each file if using your own Atlas cluster:

```python
# Replace this line in each page file:
pymongo.MongoClient("mongodb+srv://m001-student:m001-mongodb-basics@sandbox.mongodb.net/")

# With your Atlas connection string:
pymongo.MongoClient("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/")
```

Make sure the `sample_airbnb` database with `listingsAndReviews` collection is loaded.
You can load it from MongoDB Atlas → Browse Collections → Load Sample Dataset.

### 3. Run the dashboard
```bash
streamlit run Overview.py
```

## Project Structure

```
airbnb_dashboard/
├── Overview.py                      # Main page
├── requirements.txt
├── README.md
└── pages/
    ├── 1_💰_Price_Analysis.py
    ├── 2_⭐_Reviews_&_Ratings.py
    ├── 3_👤_Host_Analysis.py
    ├── 4_🌍_Geographic_Analysis.py
    └── 5_🏡_Amenities_&_Features.py
```

## Features
- **Global sidebar filters** on each page (country, room type, price range, etc.)
- **Interactive Plotly charts** — hover, zoom, click
- **Cached MongoDB queries** (5-min TTL) for performance
- **Responsive layout** using Streamlit columns
- Custom CSS with Airbnb-inspired color palette
