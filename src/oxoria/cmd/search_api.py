import difflib

from oxoria.search.use_vector import UseVector
from oxoria.search.db_operate import SearchBase, FaissIndexBase
from oxoria.cmd.resources_api import ResourcesAPI

class SearchAPI:
    def __init__(self):
        self.use_vector = UseVector()
        self.search_base = SearchBase()
        self.faiss_index_base = FaissIndexBase()

    def append_search_base(self, 
                           kw: str
                           ) -> None:
        np_array = self.use_vector.create_normalized_embedding_np([kw])
        idx = self.faiss_index_base.read_index()
        self.faiss_index_base.add_index(idx, np_array)
        search_base = self.search_base.get_base()
        search_base.append(kw)
        self.search_base.set_base(search_base)
        
    def semantic_search_kw(self,
                  kw: str,
                  return_num: int = 3
                  ) -> list[str]:
        searching_kw = [kw]
        search_base = self.search_base.get_base()
        idx = self.faiss_index_base.read_index()
        if len(search_base) < return_num:
            return_num = len(search_base)
        result = self.use_vector.get_search_results(query_text=searching_kw,
                                                    base_index=idx,
                                                    search_base=search_base,
                                                    k=return_num)
        return result
    
    def semantic_search_kw_to_pointer(self,
                  kw: str,
                  return_num: int = 3
                  ) -> list[str]:
        result = self.semantic_search_kw(kw=kw, 
                                return_num=return_num)
        pointer_list = [None for _ in range(return_num)]
        resources_api = ResourcesAPI()
        profile = resources_api.get_resources_profile()
        for pointer, profile in profile.items():
            memo_content = profile.get("memo", None)
            if memo_content in result:
                location = result.index(memo_content)
                pointer_list[location] = str(pointer)
        return pointer_list
    
    def distance_search_kw(self,
                           kw: str,
                           return_num: int = 3,
                           cutoff: float = 0.5
                           ) -> list[str]:
        resources_api = ResourcesAPI()
        profile = resources_api.get_resources_profile()
        names = []
        pointers = []
        for pointer, profile in profile.items():
            names.append(profile.get("name", None))
            pointers.append(pointer)
        similar_names = difflib.get_close_matches(kw, names, n=return_num, cutoff=0.5) 
        similar_pointers = []
        for name in names:
            if name in similar_names:
                location = names.index(name)
                similar_pointers.append(pointers[location])
        return similar_pointers         