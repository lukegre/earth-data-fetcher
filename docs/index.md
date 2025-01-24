# Earth Data Fetcher

A Python package designed to simplify the process of fetching gridded Earth science data from various sources using appropriate protocols.

## Features

- Support for multiple data access protocols:
    - File-based data: HTTP/HTTPS/S3
    - THREDDS datasets
    - CMEMS datasets (zarr)
    - `zarr` is currently not supported, only indirectly via CMEMS. 
- Configurable data source definitions via YAML


## Quick Start

```bash
pip install earth-data-fetcher
```

Create a `data_sources.yaml` configuration file:

```yaml
sst_cci:
    metadata:
        title: 'ESA Sea Surface Temperature'
        version: v2.1
    storage_options:
        cache_storage: ../data/sst/{t:%Y}/
    url: https://example.com/sst/data_{t:%Y%m%d}.nc
```

Download the data:

```python
import pandas as pd
import earth_data_fetcher as edf

sources = edf.read_data_sources_yaml('../data_sources.yaml')

sst = edf.make_downloader(sources.sst_cci_cdr)

dates = pd.date_range('2010-01-01', '2010-01-31')
flist = sst.download(dates)
```
