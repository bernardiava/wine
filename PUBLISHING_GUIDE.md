# 🍷 Global Wine Markets Dashboard (1835-2024)

A comprehensive Streamlit dashboard for analyzing global wine market data with integrated 5-level economic analysis framework.

## 📊 Features

### Interactive Analysis Modules
1. **Overview & Key Metrics** - Global KPIs, choropleth maps, top producers/consumers
2. **Production Analysis** - Historical trends, regional breakdowns, market share evolution
3. **Trade Analysis** - Export/import volumes, unit values, trade balance
4. **Consumption Patterns** - Total and per capita consumption analysis
5. **Vineyard Area & Land Use** - Area trends, productivity/yield analysis
6. **Regional Economic Analysis** - Regional aggregates, GDP correlations
7. **Comparative Advantage** - RCA index, trade specialization patterns
8. **Time Series Trends** - Multi-variable analysis, growth rates
9. **Country Comparison Tool** - Radar charts, statistical summaries

### 🎓 Five-Level Expert Economic Analysis Framework

Each analysis module includes integrated expert commentary following this framework:

#### Level 1: Descriptive Analysis
Document regional production, consumption, and trade patterns over time with clear visualizations of historical trends and current states.

#### Level 2: Production Economics
Analyze factor productivity, technological change, cost structures, volatility patterns, and policy impacts across regions and time periods.

#### Level 3: Trade Economics
Examine comparative advantage (RCA), intra-industry trade patterns, regional integration effects, and export orientation dynamics.

#### Level 4: Consumption Economics
Assess income elasticities, cultural factors, demographic influences, urbanization effects, and demand shifts on regional consumption patterns.

#### Level 5: Structural Transformation
Evaluate the wine sector's role in broader agricultural development, economic diversification, value chain upgrading, and long-term structural change pathways.

## 🚀 Quick Start

### Local Deployment

```bash
# Clone the repository
git clone <your-repo-url>
cd global-wine-markets-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment

1. **Push to GitHub** (if not already done):
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository and branch
   - Set Main file path: `app.py`
   - Click "Deploy!"

3. **Optional Configuration**:
   - Add secrets in Streamlit Cloud UI if needed
   - Configure advanced settings for larger datasets

## 📁 Project Structure

```
global-wine-markets-dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── megafile_of_global_wine_data_1835_to_2024-0425.xlsx  # Data source
├── .streamlit/
│   ├── config.toml                # App configuration
│   └── secrets.toml               # Secrets template (not committed)
└── .gitignore                     # Git ignore rules
```

## 📊 Data Source

Data from: **"Annual Database of Global Wine Markets, 1835 to 2024"**
- Authors: Kym Anderson and Vicente Pinilla
- Institution: Wine Economics Research Centre, University of Adelaide
- Coverage: 54+ countries, 96+ tables, nearly 200 years of historical data
- Variables: Production, trade (volume & value), consumption, vineyard area

## 🎨 Customization

### Theme Configuration
Edit `.streamlit/config.toml` to customize:
- Primary/secondary colors
- Font family
- Base theme (light/dark)

### Adding New Analyses
Extend `app.py` by:
1. Adding new functions following the existing pattern
2. Registering them in the sidebar navigation
3. Including 5-level analysis commentary

## 🔧 Requirements

- Python 3.8+
- streamlit>=1.28.0
- pandas>=2.0.0
- plotly>=5.14.0
- openpyxl>=3.0.0

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit | Powered by Wine Economics Research**
