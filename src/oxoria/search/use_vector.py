from __future__ import annotations
import os
import shutil
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from typing import TYPE_CHECKING
from pathlib import Path

import numpy as np
import faiss
if TYPE_CHECKING:
    from torch import Tensor
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForFeatureExtraction

from oxoria.global_var import GBVar

class UseVector:
    def __init__(self):
        self.data_dir = GBVar.DATA_DIR

    def drop_model_and_tokenizer(self) -> None:
        if hasattr(self, "model") and hasattr(self, "tokenizer"):
            return
        model_dir = Path(self.data_dir) / "language_model" / "model"
        cache_dir = Path(self.data_dir) / "language_model" / "cache_model"
        model_config_path = model_dir / "config.json"
        if model_dir.exists() and model_config_path.exists():
            return
        model_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        tmp_tokenizer = AutoTokenizer.from_pretrained(
            "shinonome-MiDUki/paraphrase-multilingual-MiniLM-based-quantumized-model-forOXORIA",
            cache_dir=str(cache_dir),
            fix_mistral_regex=True)
        tmp_model = ORTModelForFeatureExtraction.from_pretrained(
            "shinonome-MiDUki/paraphrase-multilingual-MiniLM-based-quantumized-model-forOXORIA",
            file_name="model_quantized.onnx",
            cache_dir=str(cache_dir)
            )
        tmp_tokenizer.save_pretrained(str(model_dir))
        tmp_model.save_pretrained(str(model_dir))
        self.tokenizer = tmp_tokenizer
        self.model = tmp_model
        shutil.rmtree(cache_dir)

    def setup_model_and_tokenizer(self) -> None:
        if hasattr(self, "model") and hasattr(self, "tokenizer"):
            return
        model_dir = Path(self.data_dir) / "language_model" / "model"
        model_config_path = model_dir / "config.json"
        if not model_dir.exists() or not model_config_path.exists():
            self.drop_model_and_tokenizer()
            return
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(model_dir),
            fix_mistral_regex=True,
            local_files_only=True)
        self.model = ORTModelForFeatureExtraction.from_pretrained(
            str(model_dir),
            file_name="model_quantized.onnx",
            local_files_only=True
            )
        
    def average_pool(self, 
                     last_hidden_states: Tensor, 
                     attention_mask: Tensor
                     ) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def create_normalized_embedding_np(self, 
                            input_texts: list[str]
                            ) -> np.ndarray:
        self.setup_model_and_tokenizer()
        batch_dict = self.tokenizer(input_texts, 
                                    max_length=512, 
                                    padding=True, 
                                    truncation=True,  
                                    return_tensors='pt')
        outputs = self.model(**batch_dict)

        embeddings = self.average_pool(outputs.last_hidden_state, 
                                       batch_dict['attention_mask'])
        embeddings_np = embeddings.cpu().detach().numpy().astype(np.float32)
        normalized_embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
        return normalized_embeddings_np

    def search_vector(self, 
                      query_text: list[str], 
                      base_index: faiss.Index, 
                      k: int = 5
                      ) -> tuple[np.ndarray, np.ndarray]:
        normalized_query_embeddings_np = self.create_normalized_embedding_np(query_text)
        if k == -1:
            k = base_index.ntotal
        D_l2, I_l2 = base_index.search(normalized_query_embeddings_np, k)

        return D_l2, I_l2
    
    def get_search_results(self, 
                           query_text: list[str], 
                           base_index: faiss.Index, 
                           search_base: list[str],
                           k: int = 5
                           ) -> list[str]:
        I_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=k)[1]
        search_results = []
        for i in range(k):
            search_results.append(search_base[I_l2[0][i].item()])
        return search_results
    
    def get_distance_result(self,
                            query_text: list[str], 
                            base_index: faiss.Index, 
                            k: int | None = 5
                            ) -> list[float]:
        D_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=k)[0]
        search_distance_results = []
        for i in range(k):
            search_distance_results.append(D_l2[0][i])
            
        return search_distance_results
    
    def get_search_results_by_distance(self, 
                                   query_text: list[str], 
                                   base_index: faiss.Index, 
                                   search_base: list[str],
                                   cutoff: float = 0.6,
                                   max_output: int = 5
                                   ) -> list[tuple[str, float]]:
        D_l2, I_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=-1)
        search_results_with_distance = []
        counter = 0
        for i in range(len(I_l2[0])):
            if D_l2[0][i] <= cutoff:
                search_results_with_distance.append(search_base[I_l2[0][i].item()])
                counter += 1
                if counter >= max_output:
                    break
        return search_results_with_distance