import pathlib
import pandas as pd
import xarray as xr

from loguru import logger
from typing import List, Union, Callable


class DownloaderXarray:
    """
    A superclass for zarr files on S3 and GCS, as well as thread/DAP-based data

    Parameters
    ----------
    data_opener : Callable
        A function that takes a string (the url to the data) and returns an xarray.Dataset
    **kwargs
        Additional keyword arguments to pass to the data opener

    Attributes
    ----------
    data_opener : Callable
        The function that opens the data
    _kwargs : dict
        The additional keyword arguments to pass to the data opener
    _data : xarray.Dataset or None
        The data that has been downloaded, or None if no data has been downloaded
    """

    def __init__(self, data_opener:Callable, **kwargs) -> None:
        """
        Parameters
        ----------
        data_opener : Callable
            A function that takes a string (the url to the data) and returns an xarray.Dataset
        **kwargs
            Additional keyword arguments to pass to the data opener
        """
        self.data_opener = data_opener
        self._kwargs = kwargs

        self._check_cache_storage_path_valid()
        self._data = None

    def _check_cache_storage_path_valid(self)->None:
        """
        Check if the cache storage path is valid.

        This method validates the cache storage path based on the following criteria:
        - Must be a string
        - Must not be empty
        - Must contain '{t:...}' to be formatted with the time
        - Must not contain any '*' characters
        - Must be daily formatted (return a unique file for each day)

        Raises
        ------
        ValueError
            If storage_options is not defined in kwargs or cache_storage is not defined in storage_options.
        AssertionError
            If any of the validation criteria are not met.

        Returns
        -------
        None
        """
        storage_options = self._kwargs.get('storage_options', {})
        if storage_options == {}:
            raise ValueError("storage_options must be defined in the kwargs")
        fname = storage_options.get('cache_storage', '')
        
        assert isinstance(fname, str), "storage_options.cache_storage must be a string"
        assert fname != '', "storage_options.cache_storage must be defined in the kwargs"
        assert '{t:' in fname, "storage_options.cache_storage must contain '{t:...}'"

        dates = pd.date_range('2000-01-01', '2000-01-09', freq='1D')
        # top level and metadata kwargs are passed to the path
        fmt_kwargs = self._kwargs | self._kwargs.get('metadata', {}) 
        flist = set([fname.format(t=t, **fmt_kwargs) for t in dates])
        assert len(flist) == len(dates), "storage_options.cache_storage must return a unique file for each day"
        logger.trace("Cache storage path is valid")
        
    def _make_local_path(self, t:pd.Timestamp)->pathlib.Path:
        """
        Create a local path for the given time and create the 
        directories if they don't exist

        Parameters
        ----------
        t : pd.Timestamp
            The time to create the path for
        
        Returns
        -------
        pathlib.Path
            The local path
        """
        storage_options = self._kwargs.get('storage_options', {})
        if storage_options == {}:
            raise ValueError("storage_options must be defined in the kwargs")
        fname = storage_options.get('cache_storage', '')
        # top level and metadata kwargs are passed to the path
        fmt_kwargs = self._kwargs | self._kwargs.get('metadata', {})  
        fname = fname.format(t=t, **fmt_kwargs)
        
        if fname == '':
            raise ValueError("storage_options.cache_storage must be defined in the kwargs")
        
        fname = pathlib.Path(fname)

        return fname
    
    @property
    def data(self):
        if self._data is None:
            logger.debug("Opening data for the first time, may take some time")
            self._data_all_vars = self.data_opener(self._kwargs['url'])
            vars = list(self._kwargs.get('variables', []))
            assert len(vars) > 0, "variables must be defined in config"
            self._data = self._data_all_vars[vars]
        return self._data
    
    def _get_data(self, t:pd.Timestamp)->xr.Dataset:
        assert isinstance(t, pd.Timestamp), "t must be a pd.Timestamp"
        
        ds = self.data.sel(time=[t], method='nearest')
        
        return ds
    
    def _download_single_timestep(self, t:pd.Timestamp)->str:
        self._previous_fname = ''
        ds = self._get_data(t)
        t_out = ds.time.to_index()[0]

        fname = self._make_local_path(t_out)
        if fname.exists() and (fname != self._previous_fname):
            logger.debug(f"File {fname} already exists")
        else:
            logger.debug(f"Downloading {t_out} to {fname}")
            logger.trace("Downloading data with compute()")
            ds = ds.compute()
            
            logger.debug(f"Saving data to {fname}")
            compress = dict(zlib=True, dtype='float32')
            fname.parent.mkdir(parents=True, exist_ok=True)

            ds.to_netcdf(
                path=fname, 
                encoding={k: compress for k in ds.data_vars}, 
                engine='h5netcdf')
            
            logger.success(f"Downloaded {t_out} to {fname}")

        self._previous_fname = fname
        return str(fname)

    def download(self, times: Union[str, pd.Timestamp, pd.DatetimeIndex, List[pd.Timestamp]])->List[str]:
        """
        Download data for the specified times.

        Parameters
        ----------
        times : Union[str, pd.Timestamp, pd.DatetimeIndex, List[pd.Timestamp]]
            The time(s) for which to download data. This can be a single timestamp as a string, 
            a pandas Timestamp object, a list or tuple of Timestamps, or a pandas DatetimeIndex.

        Returns
        -------
        List[str]
            A list of file paths where the downloaded data is saved.

        Raises
        ------
        ValueError
            If the provided times are not in a valid format.
        """
        
        if isinstance(times, str):
            times = [pd.Timestamp(times)]
        elif isinstance(times, pd.Timestamp):
            times = [times]
        elif isinstance(times, (list, tuple)):
            assert all([isinstance(t, pd.Timestamp) for t in times])
        elif isinstance(times, pd.DatetimeIndex):
            pass
        else:
            raise ValueError("times must be a string, a pd.Timestamp or a list of pd.Timestamp")
        
        flist = []
        for t in times:
            fname = self._download_single_timestep(t)
            flist.append(fname)
        
        return flist
    

def pydap_opener(url: str) -> xr.Dataset:
    """
    Open a dataset with pydap.

    Parameters
    ----------
    url : str
        The URL to the dataset

    Returns
    -------
    xr.Dataset
        The dataset
    """
    return xr.open_dataset(url, engine='pydap')


def cmems_opener(url: str) -> xr.Dataset:
    """
    Open a dataset with pydap.

    Parameters
    ----------
    url : str
        The URL to the dataset

    Returns
    -------
    xr.Dataset
        The dataset
    """
    import copernicusmarine as cm
    import dotenv

    if not dotenv.load_dotenv():
        raise ValueError("No .env file found. Please create `.env` file in project root")
    else:
        env = dotenv.dotenv_values()

    ds = cm.open_dataset(
        username=env['COPERNICUSMARINE_SERVICE_USERNAME'],
        password=env['COPERNICUSMARINE_SERVICE_PASSWORD'],
        dataset_id=url,
        service='geoseries',
        chunk_size_limit=1)
    
    return ds