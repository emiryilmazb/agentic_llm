# Agentic Character.ai Klonu

Bu proje, Character.ai benzeri bir karakter chatbot platformuna agentic yapı ve MCP (Model Context Protocol) özellikleri eklenmiş gelişmiş bir versiyonudur.

## Özellikler

### Temel Chatbot Özellikleri
- Özelleştirilebilir karakterler oluşturma
- Wikipedia'dan otomatik karakter bilgisi çekme
- Karakter kişiliği ve geçmişini tanımlama
- Sohbet geçmişini kaydetme

### Agentic Yapı
- Karakterlere eylemler gerçekleştirme yeteneği
- Kullanıcı isteklerine göre araçlar kullanma
- Akıllı yanıtların yanı sıra gerçek eylemleri gerçekleştirme
- **Dinamik Araç Oluşturma**: İhtiyaç duyulan araçları otomatik olarak oluşturma

### MCP (Model Context Protocol) Araçları
#### Yerleşik Araçlar
- **search_wikipedia**: Wikipedia'da bilgi arama
- **get_current_time**: Güncel tarih/saat bilgisi alma
- **get_weather**: Hava durumu bilgisi (demo)
- **open_website**: Web sitesi açma
- **calculate_math**: Matematiksel hesaplamalar yapma

#### Dinamik Araçlar
- **currency_converter**: Döviz kurları ve para birimi dönüşümleri (örnek)
- *ve daha fazlası*: Sistem, kullanıcı ihtiyaçlarına göre yeni araçlar oluşturabilir

## Kurulum

1. Gerekli bağımlılıkları yükleyin:
```
pip install -r requirements.txt
```

2. API anahtarını ayarlayın:
`.env` dosyasında `GEMINI_API_KEY` değişkenini geçerli bir Google Gemini API anahtarı ile ayarlayın.

3. Uygulamayı çalıştırın:
```
streamlit run app.py
```

## Kullanım

### Karakter Oluşturma
1. Yan menüden "Yeni karakter oluşturun" seçeneğini seçin
2. Karakter adını girin
3. İsterseniz Wikipedia'dan bilgi çekin
4. Karakter geçmişi ve kişiliğini tanımlayın
5. "Agentic Özellikleri Etkinleştir" seçeneğini işaretleyin (araçları kullanabilen karakter için)
6. "Karakteri Oluştur" butonuna tıklayın

### Sohbet Etme
1. Yan menüden "Var olan karakterle konuşun" seçeneğini seçin
2. Bir karakter seçin
3. "Bu karakterle konuş" butonuna tıklayın
4. Mesaj kutusuna yazarak sohbet edin

### Agentic Karakter İle Etkileşim
Agentic özelliği etkinleştirilmiş bir karakterle şu tür isteklerde bulunabilirsiniz:

- "Bugün hava nasıl?"
- "Albert Einstein hakkında bilgi verir misin?"
- "Saat kaç?"
- "2+2*3 hesaplar mısın?"
- "example.com sitesini açar mısın?"
- "1 dolar kaç TL?" (dinamik araç oluşturma örneği)
- "Tokyo'da hava durumu nasıl olacak?" (dinamik araç oluşturma örneği)

## Mimari

Proje dört ana bileşenden oluşur:

1. **app.py**: Ana Streamlit uygulaması ve kullanıcı arayüzü
2. **agentic_character.py**: Eylemleri işleyen ve araçları kullanan karakter modülü
3. **mcp_server.py**: Karakterlerin kullanabileceği araçları sağlayan MCP sunucusu
4. **dynamic_tool_manager.py**: Dinamik araç oluşturma ve yönetim sistemi

## Geliştirme

### Manuel Araç Ekleme

Daha fazla araç eklemek için:

1. `mcp_server.py` dosyasına yeni bir MCPTool sınıfı ekleyin
2. Bu aracı default_server'a kaydedin
3. Aracın işlevselliğini uygun şekilde uygulayın

```python
class YeniArac(MCPTool):
    def __init__(self):
        super().__init__(
            name="yeni_arac",
            description="Yeni aracın açıklaması"
        )
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Aracın işlevselliğini uygulayın
        return {"sonuc": "işlem sonucu"}

# Aracı sunucuya kaydedin
default_server.register_tool(YeniArac())
```

### Dinamik Araç Oluşturma Sistemi

Sistem, kullanıcı ihtiyaçlarına göre otomatik olarak yeni araçlar oluşturabilir:

1. Kullanıcı, mevcut araçlarla karşılanamayan bir istek gönderir (örn. "1 dolar kaç TL?")
2. Sistem, bu isteği analiz eder ve yeni bir araç gerektiğini tespit eder
3. AI modeli kullanılarak yeni aracın kodu otomatik olarak oluşturulur
4. Oluşturulan araç `dynamic_tools` dizinine kaydedilir ve MCP sunucusuna kaydedilir
5. Karakter, yeni oluşturulan aracı kullanarak kullanıcının isteğine yanıt verir

Dinamik araç oluşturma sistemi hakkında daha fazla bilgi için `dynamic_tools/README.md` dosyasına bakın.
