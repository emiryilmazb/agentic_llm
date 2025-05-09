from mcp_server import MCPTool
import requests
import json
from typing import Dict, Any, Optional, List
from utils.wiki_service import WikiService
import re

class GetPresidentTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="get_president",
            description="Retrieves the current president of a given country."
        )
        # Ülke adı varyasyonları için eşleştirme sözlüğü
        self.country_variations = {
            "turkey": ["turkey", "türkiye", "turkiye"],
            "usa": ["usa", "united states", "united states of america", "america"],
            "uk": ["uk", "united kingdom", "great britain", "england"],
            "russia": ["russia", "russian federation"],
            # Diğer ülkeler için varyasyonlar eklenebilir
        }
        
        # Cumhurbaşkanları için manuel veri (API başarısız olduğunda kullanılacak)
        self.president_data = {
            "turkey": "Recep Tayyip Erdoğan",
            "usa": "Joe Biden",
            "uk": "Rishi Sunak",  # Başbakan (Birleşik Krallık'ta cumhurbaşkanı yok)
            "russia": "Vladimir Putin",
            "france": "Emmanuel Macron",
            "germany": "Frank-Walter Steinmeier",
            "china": "Xi Jinping",
            "japan": "Fumio Kishida",  # Başbakan
            "india": "Droupadi Murmu",
            "brazil": "Luiz Inácio Lula da Silva",
            "canada": "Justin Trudeau",  # Başbakan
            "australia": "Anthony Albanese",  # Başbakan
            "italy": "Sergio Mattarella",
            "spain": "Pedro Sánchez",  # Başbakan
            "mexico": "Andrés Manuel López Obrador",
            "south korea": "Yoon Suk Yeol",
            "indonesia": "Joko Widodo",
            "saudi arabia": "Mohammed bin Salman",  # Veliaht Prens
            "south africa": "Cyril Ramaphosa",
            "egypt": "Abdel Fattah el-Sisi"
        }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        country = args.get("country")

        if not country:
            return {"error": "Country name is required."}
        
        # Ülke adını normalleştir
        normalized_country = self._normalize_country_name(country)
        
        # Önce manuel veritabanımızda kontrol et
        if normalized_country in self.president_data:
            president_name = self.president_data[normalized_country]
            return {
                "president": president_name,
                "country": country,
                "source": "Internal database"
            }
        
        # Manuel veritabanında yoksa, Wikipedia'dan almaya çalış
        try:
            # Önce ülke adıyla doğrudan arama yap
            wiki_info = self._get_president_from_wiki(country)
            if wiki_info and "president" in wiki_info:
                return wiki_info
            
            # Normalleştirilmiş ülke adıyla tekrar dene
            if normalized_country != country.lower():
                wiki_info = self._get_president_from_wiki(normalized_country)
                if wiki_info and "president" in wiki_info:
                    return wiki_info
            
            # Başarısız olursa, ülke bulunamadı mesajı döndür
            return {"result": f"Could not find the president for {country}."}
            
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}
    
    def _normalize_country_name(self, country: str) -> str:
        """Ülke adını normalleştir ve bilinen varyasyonları eşleştir"""
        country_lower = country.lower().strip()
        
        # Varyasyon eşleştirmesi
        for standard_name, variations in self.country_variations.items():
            if country_lower in variations:
                return standard_name
        
        return country_lower
    
    def _get_president_from_wiki(self, country: str) -> Dict[str, Any]:
        """Wikipedia'dan ülke cumhurbaşkanı bilgisini al"""
        try:
            # Ülke hakkında Wikipedia'dan bilgi al
            wiki_service = WikiService()
            country_info = wiki_service.fetch_info(country)
            
            if "No information found" in country_info or "No Wikipedia page found" in country_info:
                return {"result": f"Could not find information about {country} on Wikipedia."}
            
            # Cumhurbaşkanı bilgisini çıkarmak için metin analizi yap
            president_name = self._extract_president_from_text(country_info)
            
            if president_name:
                return {
                    "president": president_name,
                    "country": country,
                    "source": "Wikipedia"
                }
            else:
                # Daha detaylı bilgi almak için tam sayfa içeriğini dene
                try:
                    search_results = wiki_service.search(country, results=1)
                    if search_results:
                        page_data = wiki_service.get_page(search_results[0])
                        if page_data and "content" in page_data:
                            president_name = self._extract_president_from_text(page_data["content"])
                            if president_name:
                                return {
                                    "president": president_name,
                                    "country": country,
                                    "source": "Wikipedia (full page)"
                                }
                except Exception as e:
                    print(f"Error getting full page content: {e}")
                
                return {"result": f"Could not extract president information for {country}."}
        
        except Exception as e:
            return {"error": f"Error during Wikipedia search: {e}"}
    
    def _extract_president_from_text(self, text: str) -> Optional[str]:
        """Metinden cumhurbaşkanı bilgisini çıkar"""
        # Cumhurbaşkanı ile ilgili anahtar kelimeler
        president_patterns = [
            r"[Pp]resident(?:\s+is)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5})",
            r"[Cc]urrent\s+[Pp]resident(?:\s+is)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5})",
            r"[Hh]ead\s+of\s+[Ss]tate(?:\s+is)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5})",
            r"[Pp]resident\s+of\s+[^\n.]+\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5})"
        ]
        
        for pattern in president_patterns:
            matches = re.search(pattern, text)
            if matches:
                return matches.group(1).strip()
        
        return None