import pickle
import json

from PIL import Image
import imagehash

class ImageHashing:
    def __init__(self,  
                 hash_mode: str, 
                 hash_size: int,
                 hash_set_path: str
                 ):
        self.hash_mode = hash_mode
        self.hash_size = hash_size
        self.hash_set_path = hash_set_path

    def generate_hash(self, 
                      image_path: str
                      ) -> str | None:
        try:
            with Image.open(image_path) as img:
                return str(imagehash.dhash(img, hash_size=self.hash_size))
        except Exception as e:
            return None
    
    def hamming_distance(hash1: str, 
                         hash2: str
                         ) -> int:
        hamming_dist = bin(int(hash1, 16) ^ int(hash2, 16)).count("1")
        return hamming_dist

    def compare_hash(self, 
                     my_hash: str, 
                     target_hash: str, 
                     tolerance: int=2
                     ) -> bool:
        if my_hash is None or target_hash is None:
            return
    
        hamming_dist = self.hamming_distance(my_hash, target_hash)
        return hamming_dist <= tolerance
    
    def match_hash(self, 
                   my_hash: str, 
                   target_hash_set: set
                   ) -> bool:
        return my_hash in target_hash_set
    
    def get_hash_set(self) -> set:
        try:
            with open(self.hash_set_path, "rb") as f:
                hash_set = pickle.load(f)
                return hash_set
        except Exception as e:
            return set()
    
    def write_hash(self, 
                   hash_value: str, 
                   hash_set: set
                   ) -> None:
        hash_set.add(hash_value)
        with open(self.hash_set_path, "wb") as f:
            pickle.dump(hash_set, f)
        
