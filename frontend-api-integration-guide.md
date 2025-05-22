# Backend API Entegrasyon Kılavuzu

Bu doküman, backend API endpointlerinin frontend'de kullanılması için detaylı bir kılavuzdur. Backend, FastAPI ile geliştirilmiş ve `/api/v1` prefix'i altında çeşitli endpointler sunmaktadır.

## API Genel Yapısı

API, dört ana kategoride endpointler sunmaktadır:

1. **Characters API** (`/api/v1/characters`): Karakter oluşturma, listeleme, görüntüleme ve silme işlemleri
2. **Chat API** (`/api/v1/chat`): Belirli bir konuşma içinde mesaj gönderme ve yanıt alma işlemleri
3. **Conversations API** (`/api/v1/conversations`): Konuşma oluşturma, listeleme, güncelleme ve silme işlemleri
4. **Tools API** (`/api/v1/tools`): Kullanılabilir araçları listeleme ve yönetme işlemleri

## 1. Characters API

### 1.1. Tüm Karakterleri Listeleme

```
GET /api/v1/characters/
```

**Yanıt Modeli:**
```typescript
interface CharacterList {
  characters: string[];  // Karakter isimlerinin listesi
}
```

**Frontend Kullanımı:**
```javascript
async function getCharacters() {
  try {
    const response = await fetch('/api/v1/characters/');
    if (!response.ok) {
      throw new Error('Karakterler alınamadı');
    }
    const data = await response.json();
    return data.characters;
  } catch (error) {
    console.error('Karakterler alınırken hata oluştu:', error);
    throw error;
  }
}
```

### 1.2. Yeni Karakter Oluşturma

```
POST /api/v1/characters/
```

**İstek Modeli:**
```typescript
interface CharacterCreate {
  name: string;           // Karakter adı
  personality: string;    // Karakter kişiliği
  background?: string;    // Karakter geçmişi (opsiyonel)
  use_wiki: boolean;      // Wikipedia'dan bilgi alınsın mı?
  use_agentic: boolean;   // Agentic özellikler etkinleştirilsin mi?
}
```

**Yanıt Modeli:**
```typescript
interface CharacterResponse {
  name: string;
  personality: string;
  background?: string;
  prompt: string;
  wiki_info?: string;
  use_agentic: boolean;
  chat_history: Array<{role: string, content: string}>;
  created_at?: string;
  updated_at?: string;
}
```

**Frontend Kullanımı:**
```javascript
async function createCharacter(characterData) {
  try {
    const response = await fetch('/api/v1/characters/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(characterData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Karakter oluşturulamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Karakter oluşturulurken hata oluştu:', error);
    throw error;
  }
}

// Örnek kullanım
const newCharacter = {
  name: "Albert Einstein",
  personality: "Meraklı, zeki ve mizah anlayışı yüksek",
  background: "20. yüzyılın en önemli fizikçilerinden biri",
  use_wiki: true,
  use_agentic: true
};

createCharacter(newCharacter)
  .then(character => console.log('Karakter oluşturuldu:', character))
  .catch(error => console.error(error));
```

### 1.3. Belirli Bir Karakteri Görüntüleme

```
GET /api/v1/characters/{character_name}
```

**Yanıt Modeli:** `CharacterResponse` (1.2'deki ile aynı)

**Frontend Kullanımı:**
```javascript
async function getCharacter(characterName) {
  try {
    const response = await fetch(`/api/v1/characters/${encodeURIComponent(characterName)}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Karakter bulunamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Karakter alınırken hata oluştu:', error);
    throw error;
  }
}
```

### 1.4. Karakter Silme

```
DELETE /api/v1/characters/{character_name}
```

**Frontend Kullanımı:**
```javascript
async function deleteCharacter(characterName) {
  try {
    const response = await fetch(`/api/v1/characters/${encodeURIComponent(characterName)}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Karakter silinemedi');
    }
    
    return true; // Başarılı silme işlemi
  } catch (error) {
    console.error('Karakter silinirken hata oluştu:', error);
    throw error;
  }
}
```

## 2. Chat API

### 2.1. Konuşmada Mesaj Gönderme

```
POST /api/v1/chat/{conversation_id}
```

**İstek Modeli:**
```typescript
interface ChatMessage {
  message: string;  // Kullanıcı mesajı
}
```

**Yanıt Modeli:**
```typescript
interface ChatResponse {
  character: string;       // Yanıt veren karakterin adı
  message: string;         // Karakterin yanıtı
  data?: {                 // Ek yanıt verileri (agentic yanıtlar için)
    type: string;
    content: string;
    display_text: string;
  };
}
```

**Frontend Kullanımı:**
```javascript
async function sendMessage(conversationId, message) {
  try {
    const response = await fetch(`/api/v1/chat/${conversationId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Mesaj gönderilemedi');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Mesaj gönderilirken hata oluştu:', error);
    throw error;
  }
}
```

### 2.2. Streaming Mesaj Gönderme

```
POST /api/v1/chat/{conversation_id}/stream
```

**İstek Modeli:** `ChatMessage` (2.1'deki ile aynı)

**Yanıt:** Server-Sent Events (SSE) formatında streaming yanıt

**Frontend Kullanımı:**
```javascript
function streamMessage(conversationId, message, onChunk, onComplete, onError) {
  const eventSource = new EventSource(`/api/v1/chat/${conversationId}/stream?message=${encodeURIComponent(message)}`);
  
  let fullResponse = '';
  
  eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
      eventSource.close();
      onComplete(fullResponse);
      return;
    }
    
    const chunk = event.data;
    fullResponse += chunk;
    onChunk(chunk);
  };
  
  eventSource.onerror = (error) => {
    eventSource.close();
    onError(error);
  };
  
  // POST isteği için alternatif yöntem (bazı tarayıcılarda EventSource POST desteklemez)
  fetch(`/api/v1/chat/${conversationId}/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function readChunk() {
      return reader.read().then(({ done, value }) => {
        if (done) {
          onComplete(fullResponse);
          return;
        }
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            const data = line.substring(6);
            if (data === '[DONE]') {
              onComplete(fullResponse);
              return;
            }
            fullResponse += data;
            onChunk(data);
          }
        });
        
        return readChunk();
      });
    }
    
    return readChunk();
  })
  .catch(error => {
    onError(error);
  });
}

// Örnek kullanım
streamMessage(
  1, // conversation_id
  "Merhaba, nasılsın?",
  (chunk) => {
    console.log('Alınan parça:', chunk);
    // UI'ı güncelle
    document.getElementById('response').textContent += chunk;
  },
  (fullResponse) => {
    console.log('Tam yanıt:', fullResponse);
    // Yanıt tamamlandığında yapılacak işlemler
  },
  (error) => {
    console.error('Streaming sırasında hata:', error);
  }
);
```

### 2.3. Konuşma Geçmişini Alma

```
GET /api/v1/chat/{conversation_id}/history
```

**Sorgu Parametreleri:**
- `limit`: Döndürülecek maksimum mesaj sayısı (varsayılan: 100, maksimum: 1000)

**Yanıt Modeli:**
```typescript
interface ChatHistoryResponse {
  character: string;                          // Karakterin adı
  history: Array<{role: string, content: string}>;  // Konuşma geçmişi
}
```

**Frontend Kullanımı:**
```javascript
async function getChatHistory(conversationId, limit = 100) {
  try {
    const response = await fetch(`/api/v1/chat/${conversationId}/history?limit=${limit}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşma geçmişi alınamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Konuşma geçmişi alınırken hata oluştu:', error);
    throw error;
  }
}
```

## 3. Conversations API

### 3.1. Yeni Konuşma Oluşturma

```
POST /api/v1/conversations/
```

**İstek Modeli:**
```typescript
interface ConversationCreate {
  character_name: string;           // Konuşulacak karakterin adı
  title?: string;                   // Konuşma başlığı (varsayılan: "New Conversation")
}
```

**Yanıt Modeli:**
```typescript
interface ConversationResponse {
  id: number;                       // Konuşma ID'si
  character_id: number;             // Karakter ID'si
  character_name: string;           // Karakter adı
  title: string;                    // Konuşma başlığı
  chat_history: Array<{role: string, content: string}>;  // Konuşma geçmişi
  created_at: string;               // Oluşturulma zamanı
  updated_at: string;               // Son güncelleme zamanı
}
```

**Frontend Kullanımı:**
```javascript
async function createConversation(characterName, title = "Yeni Konuşma") {
  try {
    const response = await fetch('/api/v1/conversations/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        character_name: characterName,
        title: title
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşma oluşturulamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Konuşma oluşturulurken hata oluştu:', error);
    throw error;
  }
}
```

### 3.2. Konuşmaları Listeleme

```
GET /api/v1/conversations/
```

**Sorgu Parametreleri:**
- `character_name`: Belirli bir karaktere ait konuşmaları filtrelemek için (opsiyonel)
- `limit`: Döndürülecek maksimum konuşma sayısı (varsayılan: 10, maksimum: 100)
- `offset`: Atlanacak konuşma sayısı, sayfalama için (varsayılan: 0)

**Yanıt Modeli:**
```typescript
interface ConversationList {
  conversations: ConversationResponse[];  // Konuşmaların listesi
}
```

**Frontend Kullanımı:**
```javascript
async function getConversations(characterName = null, limit = 10, offset = 0) {
  try {
    let url = `/api/v1/conversations/?limit=${limit}&offset=${offset}`;
    if (characterName) {
      url += `&character_name=${encodeURIComponent(characterName)}`;
    }
    
    const response = await fetch(url);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşmalar alınamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Konuşmalar alınırken hata oluştu:', error);
    throw error;
  }
}
```

### 3.3. Belirli Bir Konuşmayı Görüntüleme

```
GET /api/v1/conversations/{conversation_id}
```

**Yanıt Modeli:** `ConversationResponse` (3.1'deki ile aynı)

**Frontend Kullanımı:**
```javascript
async function getConversation(conversationId) {
  try {
    const response = await fetch(`/api/v1/conversations/${conversationId}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşma bulunamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Konuşma alınırken hata oluştu:', error);
    throw error;
  }
}
```

### 3.4. Konuşma Başlığını Güncelleme

```
PATCH /api/v1/conversations/{conversation_id}
```

**İstek Modeli:**
```typescript
interface ConversationUpdate {
  title: string;  // Yeni konuşma başlığı
}
```

**Yanıt Modeli:** `ConversationResponse` (3.1'deki ile aynı)

**Frontend Kullanımı:**
```javascript
async function updateConversationTitle(conversationId, newTitle) {
  try {
    const response = await fetch(`/api/v1/conversations/${conversationId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title: newTitle }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşma güncellenemedi');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Konuşma güncellenirken hata oluştu:', error);
    throw error;
  }
}
```

### 3.5. Konuşma Silme

```
DELETE /api/v1/conversations/{conversation_id}
```

**Frontend Kullanımı:**
```javascript
async function deleteConversation(conversationId) {
  try {
    const response = await fetch(`/api/v1/conversations/${conversationId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşma silinemedi');
    }
    
    return true; // Başarılı silme işlemi
  } catch (error) {
    console.error('Konuşma silinirken hata oluştu:', error);
    throw error;
  }
}
```

### 3.6. Konuşma Geçmişini Temizleme

```
DELETE /api/v1/conversations/{conversation_id}/history
```

**Yanıt Modeli:** `ConversationResponse` (3.1'deki ile aynı)

**Frontend Kullanımı:**
```javascript
async function clearConversationHistory(conversationId) {
  try {
    const response = await fetch(`/api/v1/conversations/${conversationId}/history`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Konuşma geçmişi temizlenemedi');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Konuşma geçmişi temizlenirken hata oluştu:', error);
    throw error;
  }
}
```

## 4. Tools API

### 4.1. Kullanılabilir Araçları Listeleme

```
GET /api/v1/tools/
```

**Yanıt Modeli:**
```typescript
interface ToolsResponse {
  built_in_tools: Array<{
    name: string;
    description: string;
    // Diğer araç özellikleri
  }>;
  dynamic_tools: Array<{
    name: string;
    description: string;
    // Diğer araç özellikleri
  }>;
}
```

**Frontend Kullanımı:**
```javascript
async function getAvailableTools() {
  try {
    const response = await fetch('/api/v1/tools/');
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Araçlar alınamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Araçlar alınırken hata oluştu:', error);
    throw error;
  }
}
```

### 4.2. Belirli Bir Aracın Detaylarını Görüntüleme

```
GET /api/v1/tools/{tool_name}
```

**Yanıt Modeli:**
```typescript
interface ToolInfo {
  name: string;
  description: string;
  // Diğer araç özellikleri
}
```

**Frontend Kullanımı:**
```javascript
async function getToolDetails(toolName) {
  try {
    const response = await fetch(`/api/v1/tools/${encodeURIComponent(toolName)}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Araç detayları alınamadı');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Araç detayları alınırken hata oluştu:', error);
    throw error;
  }
}
```

### 4.3. Dinamik Araç Silme

```
DELETE /api/v1/tools/{tool_name}
```

**Frontend Kullanımı:**
```javascript
async function deleteTool(toolName) {
  try {
    const response = await fetch(`/api/v1/tools/${encodeURIComponent(toolName)}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Araç silinemedi');
    }
    
    return true; // Başarılı silme işlemi
  } catch (error) {
    console.error('Araç silinirken hata oluştu:', error);
    throw error;
  }
}
```

## Frontend Entegrasyonu İçin Öneriler

1. **API İstek Yönetimi**: Tüm API isteklerini merkezi bir serviste toplayın. Örneğin:

```javascript
// api.js
const API_BASE_URL = '/api/v1';

export const CharactersAPI = {
  getAll: () => fetch(`${API_BASE_URL}/characters/`).then(res => res.json()),
  getOne: (name) => fetch(`${API_BASE_URL}/characters/${encodeURIComponent(name)}`).then(res => res.json()),
  create: (data) => fetch(`${API_BASE_URL}/characters/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(res => res.json()),
  delete: (name) => fetch(`${API_BASE_URL}/characters/${encodeURIComponent(name)}`, {
    method: 'DELETE'
  }).then(res => res.status === 204)
};

export const ChatAPI = {
  // Benzer şekilde Chat API metodları
};

// Diğer API'ler...
```

2. **Hata Yönetimi**: Tüm API isteklerinde tutarlı hata yönetimi uygulayın:

```javascript
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || `HTTP error! status: ${response.status}`);
    }
    
    if (response.status === 204) {
      return null; // No content
    }
    
    return await response.json();
  } catch (error) {
    console.error('API isteği sırasında hata:', error);
    throw error;
  }
}
```

3. **Streaming Yanıtlar İçin Yardımcı Fonksiyon**:

```javascript
function handleStreamingResponse(conversationId, message, callbacks) {
  const { onChunk, onComplete, onError } = callbacks;
  
  // SSE kullanarak streaming
  const eventSource = new EventSource(`/api/v1/chat/${conversationId}/stream?message=${encodeURIComponent(message)}`);
  
  let fullResponse = '';
  
  eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
      eventSource.close();
      onComplete && onComplete(fullResponse);
      return;
    }
    
    const chunk = event.data;
    fullResponse += chunk;
    onChunk && onChunk(chunk);
  };
  
  eventSource.onerror = (error) => {
    eventSource.close();
    onError && onError(error);
  };
  
  // Bağlantıyı kapatmak için fonksiyon döndür
  return () => {
    eventSource.close();
  };
}
```

4. **React Hooks Kullanımı**: React kullanıyorsanız, API istekleri için custom hook'lar oluşturun:

```javascript
// useCharacters.js
import { useState, useEffect } from 'react';
import { CharactersAPI } from '../api';

export function useCharacters() {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function fetchCharacters() {
      try {
        setLoading(true);
        const data = await CharactersAPI.getAll();
        setCharacters(data.characters);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    
    fetchCharacters();
  }, []);
  
  return { characters, loading, error };
}
```

5. **Konuşma Yönetimi**: Aktif konuşmayı ve mesajları yönetmek için bir context veya state yönetimi çözümü kullanın:

```javascript
// ChatContext.js
import React, { createContext, useState, useContext } from 'react';
import { ChatAPI, ConversationsAPI } from '../api';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  async function startConversation(characterName, title) {
    setLoading(true);
    try {
      const conversation = await ConversationsAPI.create(characterName, title);
      setActiveConversation(conversation);
      setMessages(conversation.chat_history || []);
      return conversation;
    } catch (error) {
      console.error('Konuşma başlatılırken hata:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }
  
  async function sendMessage(message) {
    if (!activeConversation) {
      throw new Error('Aktif konuşma bulunamadı');
    }
    
    // Kullanıcı mesajını ekle
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const response = await ChatAPI.sendMessage(activeConversation.id, message);
      
      // Karakter yanıtını ekle
      const assistantMessage = { role: 'assistant', content: response.message };
      setMessages(prev => [...prev, assistantMessage]);
      
      return response;
    } catch (error) {
      console.error('Mesaj gönderilirken hata:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }
  
  // Diğer fonksiyonlar...
  
  return (
    <ChatContext.Provider value={{
      activeConversation,
      messages,
      loading,
      startConversation,
      sendMessage,
      // Diğer değerler ve fonksiyonlar...
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  return useContext(ChatContext);
}
```

## Dikkat Edilmesi Gereken Noktalar

1. **Hata Yönetimi**: Tüm API isteklerinde uygun hata yönetimi yapın. Backend, hata durumlarında detaylı bilgi içeren JSON yanıtları döndürür.

2. **Streaming Yanıtlar**: Streaming yanıtlar için SSE (Server-Sent Events) kullanılmaktadır. Tarayıcı desteği kontrol edilmeli ve gerekirse alternatif yöntemler uygulanmalıdır.

3. **Karakter İsimleri**: Karakter isimlerini URL'lerde kullanırken `encodeURIComponent()` ile kodlayın.

4. **Sayfalama**: Konuşma listesi gibi potansiyel olarak büyük veri setleri için sayfalama parametrelerini (`limit` ve `offset`) kullanın.

5. **Yanıt Yapıları**: Backend yanıtlarının yapısını anlamak ve doğru şekilde işlemek için model tanımlarını dikkate alın.

6. **Güvenlik**: Kullanıcı girdilerini her zaman doğrulayın ve XSS saldırılarına karşı önlem alın.

Bu kılavuz, backend API'lerini frontend'de kullanmak için gereken tüm bilgileri içermektedir. Her endpoint için açıklamalar, istek/yanıt modelleri ve örnek kullanımlar verilmiştir. Bu bilgiler doğrultusunda frontend uygulamanızı geliştirerek backend ile sorunsuz bir entegrasyon sağlayabilirsiniz.