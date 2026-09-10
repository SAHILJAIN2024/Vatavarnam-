# Multi-Source Geospatial & Environmental Data Ingestion Pipeline

A comprehensive, modular data ingestion and ETL (Extract, Transform, Load) pipeline designed for environmental analytics, hydrometeorological modeling, remote sensing, and agro-ecological risk assessment.

This repository orchestrates automated data extraction, normalization, spatial re-gridding, temporal alignment, and storage across global climate reanalysis, national hydrometeorological portals, earth observation satellite APIs, oceanographic data servers, and global pedological grids.

---

## Table of Contents
- [Pipeline Architecture Overview](#pipeline-architecture-overview)
- [Data Sources & Ingestion Specifications](#data-sources--ingestion-specifications)
  - [1. ECMWF Copernicus Climate Data Store (CDS) - ERA5](#1-ecmwf-copernicus-climate-data-store-cds---era5)
  - [2. NWIC / IMD - Daily Gridded & In-Situ Rainfall](#2-nwic--imd---daily-gridded--in-situ-rainfall)
  - [3. NRSC Bhoonidhi Open API - Satellite Earth Observation](#3-nrsc-bhoonidhi-open-api---satellite-earth-observation)
  - [4. INCOIS Live Access Server (LAS) - Oceanographic & SST](#4-incois-live-access-server-las---oceanographic--sst)
  - [5. NWIC / CWC - River Discharge Telemetry (Hourly)](#5-nwic--cwc---river-discharge-telemetry-hourly)
  - [6. NWIC / CGWB - Groundwater Level Telemetry (Daily)](#6-nwic--cgwb---groundwater-level-telemetry-daily)
  - [7. ISRO Bhuvan - Agricultural Hotspots & Land Use Vector](#7-isro-bhuvan---agricultural-hotspots--land-use-vector)
  - [8. ISRIC SoilGrids - Global Soil Properties & Taxonomy](#8-isric-soilgrids---global-soil-properties--taxonomy)
- [Directory Structure](#directory-structure)
- [Installation & Environment Setup](#installation--environment-setup)
- [Authentication & Credential Configuration](#authentication--credential-configuration)
- [Execution & Pipeline Workflow](#execution--pipeline-workflow)
- [Data Harmonization & Storage Schema](#data-harmonization--storage-schema)
- [Monitoring, Validation & Quality Control](#monitoring-validation--quality-control)
- [License](#license)

---

## Pipeline Architecture Overview

```
                          ┌────────────────────────────────────────────────────────┐
                          │                External Data Sources                   │
                          └────────────────────────────────────────────────────────┘
                                                       │
         ┌───────────────────┬─────────────────────────┼────────────────────────┬───────────────────┐
         ▼                   ▼                         ▼                        ▼                   ▼
   Copernicus CDS       NWIC / IMD / CWC          NRSC Bhoonidhi           INCOIS LAS          ISRIC SoilGrids
   (ERA5 Reanalysis)   (Rain, Flow, GW)         (EO Imagery/Raster)     (Oceanography/SST)   & Bhuvan (Vectors)
         │                   │                         │                        │                   │
         └───────────────────┴─────────────────────────┼────────────────────────┴───────────────────┘
                                                       ▼
                          ┌────────────────────────────────────────────────────────┐
                          │               Raw Ingestion Layer (L0)                 │
                          │   • CDS API Client        • NWIC REST Client           │
                          │   • Bhoonidhi OGC / API   • LAS OPeNDAP / WMS Engine   │
                          │   • WFS / GeoJSON Sync    • SoilGrids REST / Cloud GeoTIFF
                          └────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
                          ┌────────────────────────────────────────────────────────┐
                          │           Data Transformation & QA Layer (L1)          │
                          │   • Temporal Alignment (UTC standardization)           │
                          │   • Coordinate Reference Reprojection (EPSG:4326)      │
                          │   • Spatial Resampling & Regridding (xarray, GDAL)      │
                          │   • Anomaly Detection & Flagging (Range/IQR validation)│
                          └────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
                          ┌────────────────────────────────────────────────────────┐
                          │           Unified Analytical Storage (L2)              │
                          │   • Multi-dimensional Grids: Zarr / NetCDF4             │
                          │   • Geospatial Vectors: PostGIS / GeoParquet            │
                          │   • Time-Series Telemetry: TimescaleDB / Parquet       │
                          └────────────────────────────────────────────────────────┘
```

---

## Data Sources & Ingestion Specifications

### 1. ECMWF Copernicus Climate Data Store (CDS) - ERA5
- **Portal Link:** [ERA5 Single Levels Reanalysis](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#download_format)
- **Domain:** Atmospheric & Surface Reanalysis (Global).
- **Core Parameters:** 2m Temperature, Surface Pressure, Total Precipitation, 10m U/V Wind Components, Solar Radiation, Boundary Layer Height.
- **Access Protocol:** Python `cdsapi` REST Client / CDS Toolbox.
- **Native Format:** GRIB / NetCDF.
- **Pipeline Role:** Baseline synoptic atmospheric conditions for meteorological calibration and physical downscaling.

### 2. NWIC / IMD - Daily Gridded & In-Situ Rainfall
- **Portal Link:** [NWIC IMD Daily Rainfall Dataset](https://nwdp.nwic.gov.in/dataset/rainfall-daily-imd)
- **Domain:** National Hydro-meteorology (India).
- **Core Parameters:** 24-hour cumulative rainfall (mm), station ID, state, district, basin identifier.
- **Access Protocol:** NWDP API / HTTPS Scraper / Scheduled CSV Sync.
- **Native Format:** JSON / CSV / Gridded ASCII.
- **Pipeline Role:** Ground-truth precipitation data used to validate remote-sensing rainfall estimates and force hydrological watershed models.

### 3. NRSC Bhoonidhi Open API - Satellite Earth Observation
- **Portal Link:** [Bhoonidhi NRSC API Portal](https://bhoonidhi.nrsc.gov.in/bhoonidhi-api/)
- **Domain:** Earth Observation & Satellite Remote Sensing.
- **Core Parameters:** Optical & SAR datasets (Resourcesat-2/2A, Cartosat, Oceansat, Sentinel missions), surface reflectance, spectral indices (NDVI, NDWI).
- **Access Protocol:** Bhoonidhi REST Search & Download API (OAuth2 / Token-based).
- **Native Format:** GeoTIFF / SAFE / HDF5.
- **Pipeline Role:** High-resolution spatial land cover, vegetation vitality, surface water dynamics, and terrain observation.

### 4. INCOIS Live Access Server (LAS) - Oceanographic & SST
- **Portal Link:** [INCOIS LAS Interactive Viewer & Data Server](https://las.incois.gov.in/las/UI.vm#panelHeaderHidden=false;differences=false;autoContour=false;xCATID=E7E72FD7130489F6AFC7128DA9263DF3;xDSID=id-61b0ca1169;varid=ASST-id-61b0ca1169;imageSize=auto;over=xy;compute=Nonetoken;tlo=07-Jan-2009%2000:00;thi=07-Jan-2009%2000:00;catid=E7E72FD7130489F6AFC7128DA9263DF3;dsid=id-61b0ca1169;varid=ASST-id-61b0ca1169;avarcount=0;xlo=30;xhi=120;ylo=-30;yhi=30;operation_id=Plot_2D_XY_zoom;view=xy)
- **Domain:** Marine Meteorology & Physical Oceanography (Indian Ocean).
- **Core Parameters:** Advanced Sea Surface Temperature (ASST), Sea Surface Salinity, Significant Wave Height, Ocean Current Vectors.
- **Access Protocol:** OPeNDAP / Ferret-backed Live Access Server API / NetCDF Subsetting.
- **Native Format:** NetCDF-3 / NetCDF-4 / ASCII.
- **Pipeline Role:** Boundary layer heat and moisture flux dynamics influencing monsoon patterns and coastal environmental regimes.

### 5. NWIC / CWC - River Discharge Telemetry (Hourly)
- **Portal Link:** [NWIC CWC Hourly River Discharge](https://nwdp.nwic.gov.in/dataset/river-discharge-telemetry-hourly-central-water-commission-cwc)
- **Domain:** Surface Water Hydrology & In-Situ Gauge Telemetry.
- **Core Parameters:** River discharge rate ($m^3/s$ or cumecs), water level (m above MSL), gauge station metadata, danger level markers.
- **Access Protocol:** RESTful API polling / JSON stream.
- **Native Format:** JSON / Tabular CSV.
- **Pipeline Role:** Real-time hydrodynamic validation, flood hydrograph extraction, and watershed runoff assessment.

### 6. NWIC / CGWB - Groundwater Level Telemetry (Daily)
- **Portal Link:** [NWIC CGWB Groundwater Telemetry (Assam & Regional Basin)](https://nwdp.nwic.gov.in/dataset/ground-water-level-telemetry-daily-cgwb-as-assam)
- **Domain:** Subsurface Hydrogeology.
- **Core Parameters:** Depth to water table (meters below ground level - mbgl), piezometric head, aquifer classification, station location coordinates.
- **Access Protocol:** NWDP Data Portal Automated Client / Scheduled ETL.
- **Native Format:** JSON / GeoJSON / CSV.
- **Pipeline Role:** Aquifer recharge analysis, baseflow estimation, and regional water stress index calculation.

### 7. ISRO Bhuvan - Agricultural Hotspots & Land Use Vector
- **Portal Link:** [Bhuvan Thematic Geospatial Platform - Agricultural Hotspots](https://bhuvan.nrsc.gov.in/ngmaps/science?mode=Vector&theme_name=AGRICULTURAL+HOTSPOT&state_name=MADHYA+PRADESH&district_name=GWALIOR#8.94/26.0345/78.1773)
- **Domain:** Agro-Ecological Mapping & Vector Cadastral Thematics.
- **Core Parameters:** Delineated agricultural hotspots, crop intensity zones, fallow dynamics, land capability polygons.
- **Access Protocol:** OGC WFS / WMS / GeoJSON spatial queries.
- **Native Format:** Shapefile / GeoJSON / KML.
- **Pipeline Role:** Spatial masking, localized ground classification, risk zoning, and crop stress correlation.

### 8. ISRIC SoilGrids - Global Soil Properties & Taxonomy
- **Portal Link:** [ISRIC SoilGrids 250m System](https://soilgrids.org/)
- **Domain:** Global Pedometrics & Soil Profiles.
- **Core Parameters:** Soil organic carbon (SOC), bulk density, pH, clay/sand/silt fraction, cation exchange capacity (CEC) across standard depths (0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm).
- **Access Protocol:** REST API / Cloud Optimized GeoTIFF (COG) via WCS / WebDAV.
- **Native Format:** Cloud Optimized GeoTIFF (COG) / VRT.
- **Pipeline Role:** Static physical parameterization for hydrologic infiltration modeling, nutrient retention, and soil-vegetation-atmosphere transfer (SVAT).

---

## Directory Structure

```text
├── config/
│   ├── config.yaml               # Master pipeline orchestrator configuration
│   ├── credentials.env.example   # Sample environment variables for API keys
│   └── spatial_bounds.geojson    # Default AOI (Area of Interest) bounding boxes
├── src/
│   ├── ingestion/
│   │   ├── era5_collector.py     # CDS API automated retrieval routines
│   │   ├── nwdp_collector.py     # NWIC client (IMD rainfall, CWC flow, CGWB groundwater)
│   │   ├── bhoonidhi_client.py   # NRSC Bhoonidhi catalog query and granule downloader
│   │   ├── incois_las_client.py  # INCOIS Live Access Server OPeNDAP/NetCDF extractor
│   │   ├── bhuvan_collector.py   # Bhuvan WFS/Vector extraction module
│   │   └── soilgrids_client.py   # SoilGrids WCS/COG windowed subset extractor
│   ├── transform/
│   │   ├── regridder.py          # Spatial interpolation & coordinate alignment
│   │   ├── temporal_align.py     # Time-series normalization and UTC standardization
│   │   ├── qa_qc.py              # Outlier detection, missing data handling & quality flags
│   │   └── vector_processor.py   # Spatial intersections and GeoParquet packaging
│   └── storage/
│       ├── zarr_writer.py        # Cloud-native multidimensional array sink
│       └── db_connector.py       # PostGIS & TimescaleDB loader
├── pipelines/
│   ├── daily_met_pipeline.py     # Daily scheduled run (Rainfall, ERA5, Streamflow)
│   ├── telemetry_stream.py       # High-frequency hourly runner (CWC, CGWB)
│   └── static_pedology_sync.py   # Periodic baseline updater (SoilGrids, Bhuvan)
├── tests/
│   ├── test_ingestion.py         # Unit tests for remote endpoint handshakes
│   └── test_transform.py         # Geometry and array shape validation tests
├── environment.yml               # Conda environment definition
├── requirements.txt              # Pip dependency listing
├── docker-compose.yml            # Containerized deployment with PostGIS & LocalStack
└── README.md                     # Pipeline documentation
```

---

## Installation & Environment Setup

### Prerequisites
- Python 3.10+
- GDAL / PROJ / GEOS system libraries
- Docker & Docker Compose (optional, for localized storage testing)

### Setting up via Conda (Recommended)

```bash
git clone https://github.com/your-org/geo-environmental-pipeline.git
cd geo-environmental-pipeline

# Create and activate environment with GDAL & geospatial bindings
conda env create -f environment.yml
conda activate geo-pipeline
```

### Setting up via Pip

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Authentication & Credential Configuration

Create a `.env` file in the root directory by copying `config/credentials.env.example`:

```bash
cp config/credentials.env.example config/credentials.env
```

Populate the required credentials:

```dotenv
# ECMWF CDS (ERA5)
CDSAPI_URL=https://cds.climate.copernicus.eu/api
CDSAPI_KEY=your_cds_api_key_here

# NRSC Bhoonidhi Open API
BHOONIDHI_API_KEY=your_bhoonidhi_token_here
BHOONIDHI_USER_ID=your_registered_username

# National Water Data Portal (NWDP / NWIC)
NWDP_API_KEY=your_nwic_api_key_or_auth_token

# INCOIS Data Gateway
INCOIS_AUTH_TOKEN=your_incois_token_if_required

# Local Target Databases
POSTGIS_CONN_STR=postgresql://user:password@localhost:5432/geodb
TIMESCALE_CONN_STR=postgresql://user:password@localhost:5432/telemetrydb
STORAGE_DATA_DIR=./data
```

---

## Execution & Pipeline Workflow

### 1. Ingest Daily Synoptic Meteorological Data (ERA5 + IMD Rainfall)
```bash
python pipelines/daily_met_pipeline.py --date 2026-09-01 --bbox 25.5 77.5 27.5 79.0
```

### 2. Stream Real-Time Gauge Telemetry (CWC Discharge & CGWB Groundwater)
```bash
# Streams hourly CWC stage data and daily CGWB groundwater levels
python pipelines/telemetry_stream.py --region Assam --sub-basin Brahmaputra
```

### 3. Fetch Remote Sensing & Thematic Vectors (Bhoonidhi, Bhuvan, SoilGrids)
```bash
# Downloads Bhuvan vector hotspots and extracts SoilGrids profile for AOI
python pipelines/static_pedology_sync.py --district Gwalior --state "MADHYA PRADESH"
```

---

## Data Harmonization & Storage Schema

| Source | Parameter Group | Spatial Resolution | Temporal Frequency | Output Storage Format | Target Coordinate System |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Copernicus ERA5** | Reanalysis Met Fields | 0.25° (~31 km) | Hourly / Daily Agg. | Cloud Zarr / NetCDF4 | EPSG:4326 (WGS84) |
| **NWIC / IMD** | Precipitation | Station / 0.25° Grid | Daily (08:30 IST) | TimescaleDB / Parquet | EPSG:4326 |
| **NRSC Bhoonidhi** | Multispectral / SAR | 10m - 30m | 5 - 12 days | Cloud-Optimized GeoTIFF | Target UTM / EPSG:4326 |
| **INCOIS LAS** | Sea Surface Temp (ASST)| 0.1° - 0.25° | Daily / Weekly | NetCDF4 / Zarr | EPSG:4326 |
| **NWIC / CWC** | River Discharge & Level| In-Situ Hydrological Stn | Hourly | TimescaleDB | Point Geometry (EPSG:4326) |
| **NWIC / CGWB** | Groundwater Depth (mbgl)| In-Situ Piezometer Stn | Daily | TimescaleDB | Point Geometry (EPSG:4326) |
| **ISRO Bhuvan** | Agri Hotspots / LU-LC | 1:50,000 Vector | Seasonal / Annual | GeoParquet / PostGIS | EPSG:4326 |
| **ISRIC SoilGrids**| Soil Texture & Chemistry| 250m | Static Baseline | Cloud-Optimized GeoTIFF | EPSG:4326 / Homolosine |

---

## Monitoring, Validation & Quality Control

- **Pre-Ingestion Check:** Automated HTTP/REST status checks and TLS certificate validation.
- **Integrity Verification:** MD5/SHA256 checksum validation for raster granules downloaded from Bhoonidhi and CDS.
- **Physical Plausibility Filters:**
  - Precipitation $\ge 0$ mm, flagging values $> 500$ mm/day as subject to manual anomaly verification.
  - River discharge values validated against physical rating curves and gauge historical maximums.
  - Groundwater depth verified against local sub-surface bedrock boundaries.
- **Automated Logging:** Centralized logging with Loguru (`/var/log/pipeline/pipeline.log`) with Prometheus metrics exported on `:8000/metrics`.

---

## License
Distributed under the Apache 2.0 License. See `LICENSE` for more information.