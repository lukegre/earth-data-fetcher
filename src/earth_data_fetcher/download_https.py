import fsspec
import pandas as pd
import xarray as xr

from loguru import logger
from typing import List, Tuple, Union, Callable


class DownloaderFsspec:
    """
    A class for downloading data from a URL using fsspec.

    Attributes
    ----------
    url : str
        The URL for downloading data.
    _kwargs : dict
        Additional keyword arguments.
    _fs : fsspec.AbstractFileSystem
        The file system for the URL.
    _url : str
        The formatted URL.
    """

    def __init__(self, url: str, **kwargs) -> None:
        """
        Initialize the DownloaderFsspec class.

        Parameters
        ----------
        url : str
            The URL for downloading data.
        **kwargs
            Additional keyword arguments.

        Raises
        ------
        AssertionError
            If the URL does not meet the validation criteria.
        """
        self.url = url
        
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._kwargs = kwargs
        self._fs, self._url = self._get_fs(url)
        self._check_url_valid(url)

    def _check_url_valid(self, url: str) -> None:
        """
        Validate the given URL based on specific criteria:
        - Must be a non-empty string.
        - Must contain '{t:...}' for time formatting.
        - Must follow the format: filecache::[protocol]://[path]

        Parameters
        ----------
        url : str
            The URL to validate.

        Raises
        ------
        AssertionError
            If the URL does not meet the validation criteria.

        Returns
        -------
        None
            Returns None if the URL is valid.
        """
        import re

        assert isinstance(url, str), "url must be a string"
        assert url != '', "url must be defined in the kwargs"
        
        pattern = re.compile(r'(^filecache::)(http|https|ftp|sftp)+://.*({t:.*}).*')
        assert pattern.match(url) is not None, "url must have the format filecache::[protocol]://[path that contains {t:...}]"

    def _get_fs(self, url: str) -> Tuple[fsspec.AbstractFileSystem, str]:
        """
        Retrieve the file system and formatted URL based on the provided URL.

        Parameters
        ----------
        url : str
            The URL for which to get the file system.

        Returns
        -------
        Tuple[fsspec.AbstractFileSystem, str]
            A tuple containing the file system and the formatted URL.
        """
        from copy import deepcopy

        storage_options = deepcopy(self._kwargs.get('storage_options', {}))
        
        fs, urlpath = fsspec.url_to_fs(url, **storage_options)

        return fs, urlpath

    def _make_path(self, t: pd.Timestamp, check_exists: bool = False) -> Tuple[Union[str, None], str]:
        """
        Construct the remote and local paths for the given time.
        The remote path is generated based on the provided URL and the time, while the local path is determined by the cache storage options.

        Parameters
        ----------
        t : pd.Timestamp
            The time for which to construct the paths.
        check_exists : bool, optional
            Whether to check if the remote path exists, by default False.

        Returns
        -------
        Tuple[Union[str, None], str]
            A tuple containing the remote path (or None if it does not exist) and the local path.
        """
        
        # top level and metadata kwargs are passed to the path
        fmt_kwargs = self._kwargs | self._kwargs.get('metadata', {})
        remote = self.url.format(t=t, **fmt_kwargs).replace('filecache::', '')
        remote = self._get_remote_path_if_exists(remote, prefix="filecache::", force_check=check_exists)

        storage_options = self._kwargs.get('storage_options', {})
        if storage_options == {}:
            raise ValueError("storage_options must be defined in the kwargs")
        local = storage_options.get('cache_storage', '').format(t=t, **fmt_kwargs)
        
        if local == '':
            raise ValueError("storage_options.cache_storage must be defined in the kwargs")
        
        logger.trace(f"Remote path: {remote}")
        return remote, local
    
    def _get_remote_path_if_exists(self, url: str, prefix: str = 'filecache::', force_check: bool = False) -> Union[str, None]:
        """
        Check if the given URL exists in the file system and return the prefixed URL if it does.
        The method checks for the existence of the URL and can enforce a check if specified by force_check.

        Parameters
        ----------
        url : str
            The URL to check.
        prefix : str, optional
            The prefix to add to the URL if it exists, by default 'filecache::'.
        force_check : bool, optional
            Whether to force a check for the URL's existence, by default False.

        Returns
        -------
        Union[str, None]
            The prefixed URL if it exists, otherwise None.
        """
        if '*' in url:
            flist = list(self._fs.glob(url))
            if len(flist) == 0:
                return None
            else:
                url = str(flist[0])
                return prefix + url
        elif force_check:
            if self._fs.exists(url):
                return prefix + url
            else:
                return None
        else:
            return prefix + url
    
    def _make_times_strided(self, t0: pd.Timestamp, t1: pd.Timestamp) -> pd.DatetimeIndex:
        """
        Construct a list of times that are strided based on the given frequency.

        Parameters
        ----------
        t0 : pd.Timestamp
            The starting time.
        t1 : pd.Timestamp
            The ending time.

        Returns
        -------
        pd.DatetimeIndex
            A list of strided times.
        """

        time_props = self._kwargs.get('time', None)
        if 'freq' not in time_props:
            raise ValueError("time.freq must be defined in the kwargs")
        else:
            freq = pd.to_timedelta(time_props['freq'])

        if freq < pd.Timedelta('1D'):
            raise ValueError("time.freq must be at least 1 day")
        elif freq == pd.Timedelta('1D'):
            logger.trace("Time frequency is 1 day")
            return pd.date_range(start=t0, end=t1, freq='1D')
        else:
            logger.trace(f"Time frequency is {freq}, searching for starting date")
            t0 = self._get_t0_for_strided_dates(t0)
            return pd.date_range(start=t0, end=t1, freq=freq)
        
    def _get_t0_for_strided_dates(self, t0: pd.Timestamp) -> pd.Timestamp:
        """
        Find the starting date for strided times based on the given time.

        Parameters
        ----------
        t0 : pd.Timestamp
            The time from which to find the starting date.

        Returns
        -------
        pd.Timestamp
            The starting date for strided times.
        """

        if not isinstance(t0, pd.Timestamp):
            raise ValueError("t0 must be a pd.Timestamp")

        if (time_props := self._kwargs.get('time', None)) is None:
            raise ValueError("time must be defined in the kwargs")
        else:
            if (freq := time_props.get('freq', None)) is None:
                raise ValueError("time.freq must be defined in the kwargs")

        dt = pd.to_timedelta(freq) * 2
        dates = pd.date_range(start=t0, end=t0 + dt, freq='1D')
        for t in dates:
            remote, _ = self._make_path(t, check_exists=True)
            if remote is not None:
                logger.debug(f"Found data at {t}")
                return t
            else:
                logger.trace(f"No data found at {t}")
            
        raise ValueError(f"No data found between {t0} and {t0 + dt}")
    
    def _download_batches(self, batches: dict) -> List[str]:
        """
        Download batches of files based on the provided batches.

        Parameters
        ----------
        batches : dict
            A dictionary containing the batches to download.

        Returns
        -------
        List[str]
            A list of downloaded files.
        """
        from copy import deepcopy
        
        storage_options = deepcopy(self._kwargs.get('storage_options'))
        if storage_options is None:
            raise ValueError("storage_options must be defined in the kwargs")

        # set a default
        storage_default = {'same_names': True}
        # replace the default with the user-defined options
        storage_options = storage_default | storage_options

        n_local = len(batches.keys())
        n_remote = sum([len(v) for v in batches.values()])
        logger.info(f"Downloading {n_remote} files to {n_local} locations")

        flist = []
        for local in batches.keys():
            urls = batches[local]
            storage_options['cache_storage'] = local
            flist += fsspec.open_local(urls, **storage_options)
            logger.success(f"Fetched {len(urls)} files to {local}")

        return flist
    
    def _make_batch(self, times: Union[str, pd.Timestamp, List[pd.Timestamp], pd.DatetimeIndex]) -> dict:
        """
        Construct batches of files to download based on the provided times.
        The batches are organized into folders, with each folder containing files for a specific time period.

        Parameters
        ----------
        times : Union[str, pd.Timestamp, List[pd.Timestamp], pd.DatetimeIndex]
            The times for which to construct batches.

        Returns
        -------
        dict
            A dictionary containing the batches to download, with folder paths as keys.
        """
        from collections import defaultdict

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
        
        times = self._make_times_strided(times[0], times[-1])

        logger.debug("Making folder-batches for download")
        batch = defaultdict(tuple)
        for t in times:
            remote, local = self._make_path(t)
            if remote is not None:
                batch[local] = batch[local] + (remote,)

        batch = dict(batch)

        return batch
    
    def download(self, times: Union[str, pd.Timestamp, List[pd.Timestamp]]) -> List[str]:
        """
        Download files based on the provided times.

        Parameters
        ----------
        times : Union[str, pd.Timestamp, List[pd.Timestamp]]
            The times for which to download files.

        Returns
        -------
        List[str]
            A list of downloaded files.
        """
        batch = self._make_batch(times)
        flist = self._download_batches(batch)
        return flist