from __future__ import annotations
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from typing import TYPE_CHECKING
from pathlib import Path

import numpy as np
import faiss
if TYPE_CHECKING:
    from torch import Tensor
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForFeatureExtraction

from oxoria.search.langugae_processing_variables import LanguageProcessingVariables as LPVar

class UseVector:
    def __init__(self):
        current_root = Path(__file__).resolve().parents[1]
        self.model_dir = current_root / LPVar.MODEL_DIR

    def setup_model_and_tokenizer(self) -> None:
        if hasattr(self, "model") and hasattr(self, "tokenizer"):
            return
        print(f"Loading model and tokenizer from {self.model_dir}...")
        model_path = os.path.abspath(self.model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, 
                                                       fix_mistral_regex=True,
                                                       local_files_only=True)
        self.model = ORTModelForFeatureExtraction.from_pretrained(
            model_path, 
            file_name=LPVar.MODEL_NAME
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
        D_l2, I_l2 = base_index.search(normalized_query_embeddings_np, k)

        return D_l2, I_l2
    
    def get_search_results(self, 
                           query_text: list[str], 
                           base_index: faiss.Index, 
                           search_base: list[str],
                           k: int = 5
                           ) :
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
                            k: int | None = None
                            ) -> list[float]:
        D_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=k)[0]
        search_distance_results = []
        for i in range(k):
            search_distance_results.append(D_l2[0][i])
            
        return search_distance_results