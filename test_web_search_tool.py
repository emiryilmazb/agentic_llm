from dynamic_tools.web_search_tool import WebSearchTool

def test_web_search_tool():
    """Web arama aracını test eder"""
    # Aracı oluştur
    tool = WebSearchTool()
    
    # Aracın adını ve açıklamasını yazdır
    print(f"Araç adı: {tool.name}")
    print(f"Araç açıklaması: {tool.description}")
    print()
    
    # Kullanılabilir arama motorlarını yazdır
    print("Kullanılabilir arama motorları:")
    for engine in tool.get_available_engines():
        print(f"- {engine['name']}: {engine['description']}")
    print()
    
    # Örnek bir arama yap
    query = "Python programlama"
    print(f"Arama sorgusu: {query}")
    print()
    
    # Tüm motorlarda ara
    print("Tüm motorlarda arama sonuçları:")
    results = tool.execute({"query": query})
    for result in results["results"]:
        print(f"- {result['engine']}: {result['search_url']}")
    print()
    
    # Belirli bir motorda ara
    engine = "google"
    print(f"{engine.capitalize()} motorunda arama sonuçları:")
    results = tool.execute({"query": query, "engine": engine})
    for result in results["results"]:
        print(f"- {result['engine']}: {result['search_url']}")

if __name__ == "__main__":
    test_web_search_tool()