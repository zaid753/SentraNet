"""Dataset registry for discovery and loading of network security datasets."""

from typing import Dict, Type, List, Optional
from ml.data.base_loader import BaseDatasetLoader
from ml.data.cicids_loader import CICIDS2017Loader
from ml.data.unsw_loader import UNSWNB15Loader
from ml.data.cic_ddos_loader import CICDDoS2019Loader
import logging

logger = logging.getLogger("sentranet.registry")

class DatasetRegistry:
    """Central registry mapping dataset identifiers to adapter implementations."""

    _LOADERS: Dict[str, Type[BaseDatasetLoader]] = {
        "cicids2017": CICIDS2017Loader,
        "unsw_nb15": UNSWNB15Loader,
        "cic_ddos2019": CICDDoS2019Loader,
    }

    _DEFAULT_PATHS: Dict[str, str] = {
        "cicids2017": "data/raw/cicids2017",
        "unsw_nb15": "data/raw/unsw_nb15",
        "cic_ddos2019": "data/raw/cic_ddos2019",
        "sample": "data/samples",
    }

    @classmethod
    def register(cls, name: str, loader_cls: Type[BaseDatasetLoader], default_path: Optional[str] = None) -> None:
        cls._LOADERS[name.lower()] = loader_cls
        if default_path:
            cls._DEFAULT_PATHS[name.lower()] = default_path
        logger.info(f"Registered dataset loader '{name}'")

    @classmethod
    def get_loader(cls, dataset_name: str, raw_path: Optional[str] = None) -> BaseDatasetLoader:
        name_key = dataset_name.lower().replace("-", "_")
        
        # If generic or sample dataset, use CICIDS2017 loader format as standard
        loader_cls = cls._LOADERS.get(name_key, CICIDS2017Loader)
        path = raw_path or cls._DEFAULT_PATHS.get(name_key, f"data/raw/{name_key}")
        
        return loader_cls(path)

    @classmethod
    def list_registered(cls) -> List[str]:
        return list(cls._LOADERS.keys())
