# AI-Powered Digital Twin of India's Climate

A comprehensive, data-driven digital twin framework for modeling, monitoring, and forecasting India's climate system across weather, oceanography, hydrology, land use, air quality, and agriculture domains.

***

## 📋 Overview

This project integrates **real-time and historical datasets** from authoritative Indian and global sources (IMD, ISRO, INCOIS, CPCB, NASA, Copernicus, ECMWF) to build a unified, multi-scale digital representation of India's climate. Designed for researchers, data engineers, and policymakers, it enables:

- **High-resolution climate modeling** (0.25°–1° spatial, hourly–daily temporal)
- **Multi-domain data fusion** (meteorology, satellite EO, ocean, groundwater, air quality, crops)
- **AI/ML-ready pipelines** for forecasting, anomaly detection, and scenario analysis
- **Open, reproducible workflows** with direct API/data access links

***

## 🗂️ Data Catalog

The project leverages **7 primary domains** with direct download URLs, API endpoints, and cloud assets:

| Domain | Key Sources | Formats | Access |
|---|---|---|---|
| **Weather & Meteorology** | IMD (0.25° rainfall, 1° temp), MOSDAC (INSAT-3D/3DR), Open-Meteo (ERA5), ECMWF CDS | NetCDF-4, JSON, GRIB2 | Open/No Auth, Free API Key, CDS registration |
| **Satellite EO** | ISRO Bhuvan (WMS/WFS/WCS, Bhoonidhi), NASA LP DAAC (MODIS/VIIRS), Copernicus (Sentinel-2) | GeoTIFF, HDF, NetCDF, SAFE | Free registration, OGC APIs, Earthdata Login |
| **Oceanography** | INCOIS ERDDAP (SST, waves, currents), Copernicus Marine (CMEMS) | NetCDF, CSV | Open/No Auth (ERDDAP), Free registration (CMEMS) |
| **Hydrology & Groundwater** | India-WRIS/NWDP (CWC reservoirs, river discharge), CGWB (groundwater levels, quality) | CSV, API, Shapefile | Open/No Auth |
| **Land Use & Terrain** | CartoDEM (30m), SRTM (30m/90m), FSI (forest cover), SoilGrids (250m) | GeoTIFF, Shapefile, WCS | Open/No Auth, Free registration |
| **Air Quality** | CPCB CCR (real-time PM2.5/PM10), OpenAQ API, SAFAR (forecast) | JSON, CSV | Open/No Auth, Free API Key |
| **Agriculture** | MNCFC (crop forecasts), FASAL (acreage), AgriStack/data.gov.in | PDF, CSV, GeoTIFF, JSON API | Open/No Auth, Free registration |

**Full dataset table with direct URLs**: See [`DATA_CATALOG.md`](./DATA_CATALOG.md) or the project wiki.

***

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/india-climate-digital-twin.git
cd india-climate-digital-twin

# Create virtual environment (Python 3.10+)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

Create a `.env` file for authenticated services:

```bash
# ECMWF CDS API (register at cds.climate.copernicus.eu)
CDS_API_KEY=your_cds_api_key
CDS_API_URL=https://cds.climate.copernicus.eu/api/v2

# OpenAQ API (register at explore.openaq.org)
OPENAQ_API_KEY=your_openaq_api_key

# ISRO Bhuvan (register at bhuvan.nrsc.gov.in)
BHOVAN_USERNAME=your_bhuvan_username
BHOVAN_PASSWORD=your_bhuvan_password
```

### 3. Download Sample Data

```bash
# IMD Gridded Rainfall (2024 NetCDF)
python scripts/download_imd_rainfall.py --year 2024 --output data/imd_rainfall/

# INCOIS SST via ERDDAP (Indian Ocean, Jan 2024)
python scripts/download_incois_sst.py --start 2024-01-01 --end 2024-01-31 --output data/incois_sst/

# OpenAQ India PM2.5 (last 30 days)
python scripts/download_openaq_india.py --days 30 --output data/openaq/
```

***

## 📁 Project Structure

```
india-climate-digital-twin/
├── data/                      # Raw & processed datasets
│   ├── imd_rainfall/          # IMD gridded rainfall (NetCDF)
│   ├── incois_sst/            # INCOIS SST (NetCDF/CSV)
│   ├── openaq/                # OpenAQ air quality (JSON/CSV)
│   └── ...                    # Other domains
├── scripts/                   # Data download & preprocessing
│   ├── download_imd_rainfall.py
│   ├── download_incois_sst.py
│   ├── download_openaq_india.py
│   └── preprocess_*.py
├── notebooks/                 # Exploratory analysis & modeling
│   ├── 01_imd_rainfall_analysis.ipynb
│   ├── 02_sst_anomalies.ipynb
│   └── 03_air_quality_trends.ipynb
├── src/                       # Core modules
│   ├── data_loader.py         # Unified data ingestion API
│   ├── preprocessing.py       # Cleaning, interpolation, regridding
│   ├── models/                # ML/AI models (forecasting, downscaling)
│   └── visualization.py       # Plotting utilities (maps, timeseries)
├── configs/                   # YAML configs for data sources & models
│   ├── data_sources.yaml
│   └── model_config.yaml
├── DATA_CATALOG.md            # Full dataset table with URLs
├── requirements.txt           # Python dependencies
├── .env.example               # Template for API keys
└── README.md                  # This file
```

***

## 🔧 Core Features

### Data Ingestion

- **Unified `data_loader` API**: Load any dataset (IMD, INCOIS, OpenAQ, etc.) with a single function call.
- **Automatic caching**: Downloaded files are cached in `data/` to avoid redundant requests.
- **Regridding & interpolation**: Align disparate resolutions (0.25°–1°) to a common grid.

```python
from src.data_loader import load_dataset

# IMD rainfall (0.25°, 2024)
rainfall = load_dataset("imd_rainfall", year=2024, grid="0.25deg")

# INCOIS SST (ERDDAP, Indian Ocean)
sst = load_dataset("incois_sst", start="2024-01-01", end="2024-01-31", bbox=[60, 0, 100, 30])

# OpenAQ PM2.5 (India, last 30 days)
pm25 = load_dataset("openaq_india", days=30, pollutant="pm25")
```

### Preprocessing

- **Missing value handling**: Temporal interpolation, spatial kriging.
- **Quality control**: Outlier removal, consistency checks (e.g., rainfall ≥ 0).
- **Temporal aggregation**: Hourly → daily → monthly composites.

### Modeling

- **Baseline forecasts**: ARIMA, Prophet for timeseries.
- **Deep learning**: LSTM, ConvLSTM for spatio-temporal prediction.
- **Downscaling**: Statistical (quantile mapping) & dynamical (WRF-ready inputs).

### Visualization

- **Interactive maps**: Folium/Plotly for spatial patterns.
- **Timeseries dashboards**: Streamlit/Plotly Dash for real-time monitoring.
- **Anomaly detection**: Heatmaps, z-score overlays.

***

## 📊 Example Workflows

### 1. Monsoon Rainfall Analysis (IMD + ERA5)

```python
import xarray as xr
from src.visualization import plot_spatial_mean

# Load IMD rainfall (0.25°) and ERA5 (0.25°)
imd = load_dataset("imd_rainfall", year=2024, grid="0.25deg")
era5 = load_dataset("era5_precip", year=2024, grid="0.25deg")

# Compute JJAS (June–September) mean
jjas_imd = imd.sel(time=slice("2024-06-01", "2024-09-30")).mean(dim="time")
jjas_era5 = era5.sel(time=slice("2024-06-01", "2024-09-30")).mean(dim="time")

# Plot comparison
plot_spatial_mean(jjas_imd, title="IMD JJAS 2024")
plot_spatial_mean(jjas_era5, title="ERA5 JJAS 2024")
```

### 2. Air Quality Trends (CPCB + OpenAQ)

```python
from src.preprocessing import aggregate_daily
from src.visualization import plot_timeseries

# Load CPCB CCR (Delhi, PM2.5) and OpenAQ (India)
cpcb = load_dataset("cpcb_ccr", city="Delhi", pollutant="pm25")
openaq = load_dataset("openaq_india", days=90, pollutant="pm25")

# Aggregate to daily mean
cpcb_daily = aggregate_daily(cpcb)
openaq_daily = aggregate_daily(openaq)

# Plot timeseries
plot_timeseries(cpcb_daily, openaq_daily, labels=["CPCB Delhi", "OpenAQ India"])
```

### 3. SST Anomalies (INCOIS ERDDAP)

```python
from src.preprocessing import compute_anomaly
from src.visualization import plot_map

# Load INCOIS SST (Jan 2024)
sst = load_dataset("incois_sst", start="2024-01-01", end="2024-01-31")

# Compute anomaly relative to 2010–2020 climatology
clim = load_dataset("incois_sst", start="2010-01-01", end="2020-12-31").mean(dim="time")
anomaly = compute_anomaly(sst, clim)

# Plot SST anomaly map
plot_map(anomaly, cmap="RdBu_r", title="INCOIS SST Anomaly (Jan 2024)")
```

***

## 🛠️ Installation

### Requirements

- Python 3.10+
- `xarray`, `dask`, `netCDF4`, `pandas`, `numpy`, `requests`, `erddapy`, `cdsapi`, `sentinelhub`, `earthaccess`

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional: GPU Acceleration

For deep learning models:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

***

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](./LICENSE) for details.

**Data Licensing**: Individual datasets retain their original licenses (e.g., IMD: CC BY 4.0, ERA5: CC BY 4.0, Sentinel-2: CC BY-SA 4.0). Always cite sources in publications.

***

## 🙏 Acknowledgments

- **India Meteorological Department (IMD)** for high-resolution gridded rainfall & temperature products.
- **ISRO Bhuvan & MOSDAC** for satellite EO (CartoDEM, INSAT-3D/3DR, FASAL).
- **INCOIS** for oceanographic data (SST, waves, currents) via ERDDAP.
- **CPCB & SAFAR** for real-time air quality monitoring.
- **ECMWF & Copernicus** for ERA5 reanalysis & Sentinel missions.
- **NASA LP DAAC** for MODIS/VIIRS land products.

***

## 📬 Contact & Contributions

- **Issues & Feature Requests**: Use GitHub Issues.
- **Pull Requests**: Welcome! Please follow the [contribution guidelines](./CONTRIBUTING.md).
- **Questions**: Open a Discussion or email `your-email@domain.edu`.

***

## 🗓️ Roadmap

- [ ] **Q4 2026**: Integrate IMDAA regional reanalysis (NCMRWF).
- [ ] **Q1 2027**: Add WRF downscaling pipeline (IMD + ERA5 boundary conditions).
- [ ] **Q2 2027**: Deploy Streamlit dashboard for real-time monitoring.
- [ ] **Q3 2027**: Publish pre-trained models (LSTM, ConvLSTM) on Hugging Face.

***

**Built with ❤️ for India's climate resilience.**#   V a t a v a r n a m -  
 