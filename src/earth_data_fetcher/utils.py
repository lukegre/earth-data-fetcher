# reads files like data/sources.yaml to the munch data type
import munch
from .download_xarray import DownloaderXarray
from .download_https import DownloaderFsspec
from typing import Union
from loguru import logger


def read_sources(fname_yaml:str)->munch.Munch:
    """Reads a yaml file and returns a munch data type"""
    import yaml

    with open(fname_yaml, 'r') as f:
        sources = munch.munchify(yaml.safe_load(f))
    return sources  # type: ignore


def make_downloader(config:dict)->Union[DownloaderFsspec, DownloaderXarray]:
    """
    Make a downloader based on the given configuration. The configuration must contain
    the following

    Parameters
    ----------
    config : dict
        The configuration dictionary that contains at least the following keys
        - url: str, The URL to download data from, or if not url formatted, assume CMEMS dataset ID
        - storage_options: dict, The storage options for the cache storage passed to fsspec
    
    Returns
    -------
    Union[DownloaderFsspec, DownloaderXarray]
        The downloader object that has method Downloader.download(pd.DateTimeIndex)

    Raises
    ------
    ValueError
        If the config does not contain the required keys
    TypeError
        If the URL is not compatible with any known downloader
    """
    import re
    from .download_xarray import cmems_opener, pydap_opener

    if 'url' not in config:
        raise ValueError("config must contain the key 'url'")
    if 'storage_options' not in config:
        raise ValueError("config must contain the key 'storage_options'")
    
    protocol_pattern = re.compile(r'filecache::(http|https|ftp|sftp)+://.*({t:.*}).*')
    is_fsspec_compatible = re.match(protocol_pattern, config['url']) is not None
    is_thredds_compatible = 'thredds' in config['url']
    is_cmems_dataset = '/' not in config['url']

    if is_fsspec_compatible:
        return DownloaderFsspec(**config)
    elif is_thredds_compatible or is_cmems_dataset:
        if is_thredds_compatible:
            logger.info("Opening with pydap")
            return DownloaderXarray(data_opener=pydap_opener, **config)
        elif is_cmems_dataset:
            logger.info("Opening with copernicusmarine")
            return DownloaderXarray(data_opener=cmems_opener, **config)
        else:
            raise ValueError("An impossible situation has occured 😱")
    else:
        raise TypeError(f"URL {config['url']} is not compatible with any known downloader")
