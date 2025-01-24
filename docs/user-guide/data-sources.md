# Defining Data Sources

Earth Data Fetcher supports various gridded data sources and protocols. Data are saved as netCDF files

The following data sources are currently supported:

- [HTTP/HTTPS/FTP/S3](#httphttpsftps3)
- [THREDDS datasets](#thredds-datasets)
- [CMEMS datasets](#cmems-datasets)

## Basic configuration

Each data source is defined as a top-level entry in the YAML file:

```yaml
dataset_name:
    metadata:
        title: 'Dataset Title'
        version: 'v1.0'
    storage_options:
        cache_storage: path/to/storage/{t:%Y}/
        same_names: true
    url: https://example.com/data_{t:%Y%m%d}.nc
    variables:
        variable_name: output_name
```
### Accepted Fields
Bold values are required, italic are required for some sources.

- **`url`**: The URL template for accessing the data
- **`storage_options`**: Configuration for local storage that is passed to `fsspec` - can add more options if login is required
    - **`cache_storage`**: Path template for storing downloaded files. For `fsspec`-based storage, only the directory is required. For `xarray`-based storage, the full path is required. Supports using string formatting with time denoted by `{t:%Y%m%d}` where `%Y` is the year, `%m` is the month, and `%d` is the day. Any top-level and metadata arguments will be passed to the string formatting.
- *`variables`*: required for THREDDS and CMEMS datasets.
    - the `variable_name: output_name`. The variables are currently not renamed, but allows for renaming further down the pipeline. 
- *`time`*: Configuration for the time range of the dataset - required for file-based sources (FTP, HTTP, HTTPS, S3)
    - `start`: Start date of the dataset (YYYY-MM-DD)
    - `end`: End date of the dataset (YYYY-MM-DD)
    - `freq`: Frequency of the dataset, with support for `n[DMY]`, where `n` is an integer, `D` is day, `M` is month, and `Y` is year. e.g., `8D` = 8-day
- `metadata`: Metadata about the dataset
    - `title`: Title of the dataset
    - `version`: Version of the dataset
    - `doi`: DOI of the dataset - highly recommended

## Configurations for supported protocols
The sections below show the configuration for supported protocols including the conditional required fields.

### HTTP/HTTPS/FTP/S3

For file-based sources, `fsspec` is used to download the data. Ensure that you pass the appropriate `fsspec` options in the `storage_options` field.
I've given an example for an FTP source below but the same principle would apply for S3 for example. At the moment, sessions + cookies are not supported. 

```yaml
fsspec_data_source_key:
    # url must have the following: start with 'filecache::', 
    url: filecache::ftp://example.com/variable/product/remote_fname_{t:%Y%m%d}.nc
    # fsspec is used to download files, so any fsspec options can be passed
    storage_options:  
        # items given at the main level are used for 'filecache', 
        # while subsequent protocols have to be specified (see 'ftp' below)
        cache_storage: ../data/sst/{t:%Y}/  # only the folder should be given
        same_names: true  # in this case 'remote_fname_{t:%Y%m%d}.nc'
        ftp:  # an example of ftp options
            username: myusername
            password: mypassword
    metadata:  # optional
        title: 'Copy this from the website'
        version: 'v1.0'
        doi: https://doi.org/10....  # much easier later
    time:  # to specify the time range of the data
        start: 1980-01-01
        end: 2024-01-01
        freq: 1D  # the frequency of the data ('8D' = 8-day, etc.)
```


### THREDDS datasets

For both thredds and CMEMS datasets, the same approach is used. The data is loaded using xarray, and the nearest time step to the requested time is selected. 
This means that if the requested time is not available, the nearest available time step is selected (e.g., 1990-01-01 requested, but only 1997-09-01 is available).

For THREDDS datasets that can be accessed through the `thredds::` protocol:

```yaml
thredds_based_data_source_key:  # in the output dictionary
    # the url must contain `thredds::`, to be recognized as a THREDDS dataset
    url: https://rsg.pml.ac.uk/thredds/dodsC/CCI_ALL-v6.0-8DAY  
    storage_options:  # we keep the same nomenclature as fsspec (a bit clunky)
        # for the local storage, file path AND name are required for thredds
        cache_storage: ../data/variable/product/{t:%Y}/filename_{t:%Y%m%d}.nc  
    time:
        start: 1997-09-01
        end: 2024-01-01
        freq: 8D
```

### CMEMS datasets
For CMEMS (Copernicus Marine Service) datasets:

```yaml
cmems_data_source_key:  # will be used as the key in the output dictionary
    # only pass the dataset ID as copied from the CMEMS website 
    # if not recognized as a url, then assume it's a CMEMS dataset ID
    url: <copernicusmarine_dataset_id>
    metadata:
        doi: https://doi.org/10....
    storage_options:  # to be consistent with fsspec nomenclature
        # for the local storage, file path AND name are required for CMEMS
        cache_storage: ../data/variable/product/{t:%Y}/filename_{t:%Y%m%d}.nc  
    variables:
        variable_name: output_name  # currently variable is not renamed
```

