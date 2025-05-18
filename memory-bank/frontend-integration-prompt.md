# Agentic LLM Frontend Integration Prompt

## Görev Tanımı
Agentic LLM projesinin backend kısmında karakterler ve konuşma geçmişi arasında ayrım yapacak şekilde değişiklikler yapıldı. Artık bir karakter ile birden fazla konuşma yapılabilecek. Frontend kodunu yeni API endpoint'leri ile çalışacak şekilde güncellemen gerekiyor.

## Erişimin Olan Dosyalar
- `frontend/chatbot-ui/src/contexts/ChatContext.js` - Sohbet yönetimi için ana context
- `frontend/chatbot-ui/src/components/chat/ConversationList.jsx` - Konuşma listesi komponenti
- Backend kaynak koduna da erişim sağlayabilirsin (gerekirse)

## Yapılması Gereken Değişiklikler

### 1. API Endpoint'leri
Aşağıdaki yeni endpoint'leri kullanan kodları yazman gerekiyor:

#### Konuşma Yönetimi Endpoint'leri:
- **Konuşma Listesi**: `GET /api/v1/conversations/?character_name={characterName}`
- **Konuşma Oluşturma**: `POST /api/v1/conversations/` 
  ```json
  {
    "character_name": "Karakter Adı",
    "title": "Konuşma Başlığı"
  }
  ```
- **Konuşma Detayı**: `GET /api/v1/conversations/{conversationId}`
- **Konuşma Güncelleme**: `PATCH /api/v1/conversations/{conversationId}`
  ```json
  {
    "title": "Yeni Başlık"
  }
  ```
- **Konuşma Silme**: `DELETE /api/v1/conversations/{conversationId}`

#### Sohbet Mesajları Endpoint'leri:
- **Mesaj Gönderme**: `POST /api/v1/chat/{conversationId}`
  ```json
  {
    "message": "Merhaba, nasılsın?"
  }
  ```
- **Mesaj Geçmişi**: `GET /api/v1/chat/{conversationId}/history`
- **Mesaj Geçmişini Temizleme**: `DELETE /api/v1/conversations/{conversationId}/history`

### 2. ChatContext.js Güncellemeleri
`ChatContext.js` dosyasında aşağıdaki fonksiyonları güncellemelisin:

- `fetchConversations`: Belirli bir karakter için konuşmaları getirmeli
- `fetchMessages`: Bir konuşmanın mesaj geçmişini getirmeli
- `createConversation`: Yeni bir konuşma oluşturmalı
- `deleteConversation`: Bir konuşmayı silmeli
- `sendMessage`: Bir konuşmaya mesaj göndermeli
- `clearConversation`: Bir konuşmanın geçmişini temizlemeli
- `renameConversation`: Bir konuşmanın başlığını güncellemeli

### 3. Veri Yapıları
Response veri yapıları şu şekildedir:

#### Konuşma Listesi Yanıtı:
```json
{
  "conversations": [
    {
      "id": 1,
      "character_id": 2,
      "character_name": "Karakter Adı",
      "title": "Konuşma Başlığı",
      "chat_history": [],
      "created_at": "2025-05-18T09:12:34.567Z",
      "updated_at": "2025-05-18T09:12:34.567Z"
    }
  ]
}
```

#### Konuşma Detayı Yanıtı:
```json
{
  "id": 1,
  "character_id": 2,
  "character_name": "Karakter Adı",
  "title": "Konuşma Başlığı",
  "chat_history": [
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Size nasıl yardımcı olabilirim?"}
  ],
  "created_at": "2025-05-18T09:12:34.567Z",
  "updated_at": "2025-05-18T09:12:34.567Z"
}
```

#### Mesaj Geçmişi Yanıtı:
```json
{
  "character": "Karakter Adı",
  "history": [
    {"role": "user", "content": "Merhaba"},
    {"role": "assistant", "content": "Size nasıl yardımcı olabilirim?"}
  ]
}
```

#### Mesaj Gönderme Yanıtı:
```json
{
  "character": "Karakter Adı",
  "message": "Size nasıl yardımcı olabilirim?",
  "data": null
}
```

## İpuçları ve Öneriler
1. Şu anki kod mock data kullanıyor, gerçek API çağrılarıyla değiştirilmeli
2. Frontend'de şu an zaten konuşma listesi yönetimi için gerekli UI komponentleri var
3. Karakterden konuşma ID'sine geçiş yapılması gerekiyor
4. Axios kütüphanesi ile API çağrıları yapılıyor
5. Error handling eklendiğinden emin ol
6. User deneyimini geliştirmek için loading state'leri kullan

## Örnek Kullanım Senaryoları
1. Kullanıcı bir karakter seçer
2. Kullanıcı "New Chat" butonuna tıklar
3. Sistem seçili karakterle yeni bir konuşma oluşturur
4. Kullanıcı konuşmada mesaj gönderir ve cevap alır
5. Kullanıcı sol panelden başka bir konuşmaya geçebilir
6. Kullanıcı bir konuşmayı yeniden adlandırabilir veya silebilir
