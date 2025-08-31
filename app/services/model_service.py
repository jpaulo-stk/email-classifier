from pathlib import Path
from joblib import load
from typing import Optional
import time

class ModelService:
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model = None
        self._loaded_at_epoch: Optional[float] = None

    def load(self):
        self._model = load(self.model_path)
        self._loaded_at_epoch = time.time()
    
    @property
    def is_loaded(self) -> bool:
        return self._model is not None
    
    @property
    def loaded_at(self) -> bool:
        return self._loaded_at_epoch
    
    @property
    def mtime(self) -> Optional[float]:
        try:
            return self.model._path.stat().st_mtime
        except FileNotFoundError:
            return None
        
    @property
    def path_str(self) -> str:
        return str(self.model._path)
    
    def predict_one(self,  text: str):
        proba_vec = self._model
        pred = self._model.predict([text])[0]
        confidence = float(max(proba_vec))
        return pred, confidence