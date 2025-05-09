from mcp_server import MCPTool
from typing import Dict, Any, List
import urllib.parse

class WebSearchTool(MCPTool):
    """Statik web arama aracı"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Statik web arama aracı. Belirli web sitelerinde arama yapar ve arama URL'lerini döndürür."
        )
        # Arama yapılacak statik web siteleri listesi
        self.search_engines = {
            "google": {
                "name": "Google",
                "url": "https://www.google.com/",
                "search_url": "https://www.google.com/search?q={query}",
                "description": "Dünyanın en popüler arama motoru"
            },
            "yandex": {
                "name": "Yandex",
                "url": "https://yandex.com.tr/",
                "search_url": "https://yandex.com.tr/search/?text={query}",
                "description": "Rusya'nın en büyük arama motoru"
            },
            "bing": {
                "name": "Bing",
                "url": "https://www.bing.com/",
                "search_url": "https://www.bing.com/search?q={query}",
                "description": "Microsoft'un arama motoru"
            },
            "wikipedia": {
                "name": "Wikipedia",
                "url": "https://tr.wikipedia.org/wiki/",
                "search_url": "https://tr.wikipedia.org/w/index.php?search={query}",
                "description": "Özgür ansiklopedi"
            },
            "eksi": {
                "name": "Ekşi Sözlük",
                "url": "https://eksisozluk.com/",
                "search_url": "https://eksisozluk.com/?q={query}",
                "description": "Türkiye'nin en büyük sosyal medya platformu"
            },
            "tdk": {
                "name": "TDK Sözlük",
                "url": "https://sozluk.gov.tr/",
                "search_url": "https://sozluk.gov.tr/?kelime={query}",
                "description": "Türk Dil Kurumu Sözlükleri"
            },
            "github": {
                "name": "GitHub",
                "url": "https://github.com/",
                "search_url": "https://github.com/search?q={query}",
                "description": "Yazılım geliştirme platformu"
            },
            "youtube": {
                "name": "YouTube",
                "url": "https://www.youtube.com/",
                "search_url": "https://www.youtube.com/results?search_query={query}",
                "description": "Video paylaşım platformu"
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Arama işlemini gerçekleştirir"""
        query = args.get("query", "")
        engine = args.get("engine", "all").lower()  # Varsayılan olarak tüm motorlarda ara
        
        if not query:
            return {"error": "Arama sorgusu gereklidir."}
        
        # Arama motorlarını belirle
        engines_to_search = []
        if engine == "all":
            engines_to_search = list(self.search_engines.keys())
        elif engine in self.search_engines:
            engines_to_search = [engine]
        else:
            return {"error": f"Geçersiz arama motoru: {engine}. Kullanılabilir motorlar: {', '.join(self.search_engines.keys())} veya 'all'"}
        
        # Arama sonuçlarını topla
        results = []
        for engine_key in engines_to_search:
            engine_info = self.search_engines[engine_key]
            search_url = engine_info["search_url"].format(query=urllib.parse.quote(query))
            
            # Arama URL'sini sonuçlara ekle
            result = {
                "engine": engine_info["name"],
                "description": engine_info["description"],
                "search_url": search_url
            }
            
            results.append(result)
        
        return {
            "query": query,
            "results": results
        }
    
    def get_available_engines(self) -> List[Dict[str, str]]:
        """Kullanılabilir arama motorlarını döndürür"""
        return [
            {"key": key, "name": info["name"], "description": info["description"]}
            for key, info in self.search_engines.items()
        ]