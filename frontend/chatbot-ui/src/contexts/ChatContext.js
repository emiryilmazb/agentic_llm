import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import { useCharacter } from "./CharacterContext";
import { useTool } from "./ToolContext";

const ChatContext = createContext(null);

export const useChat = () => {
  return useContext(ChatContext);
};

export const ChatProvider = ({ children }) => {
  const { selectedCharacter } = useCharacter();
  // eslint-disable-next-line no-unused-vars
  const { tools } = useTool();

  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fetchedCharactersRef = useRef({});

  // Konuşmaları getir fonksiyonu
  const fetchConversations = useCallback(
    async (characterName) => {
      try {
        setLoading(true);
        setError("");

        console.log("fetchConversations çağrıldı:", characterName);

        // API kılavuzuna göre sorgu parametrelerini ayarla
        const response = await axios.get(
          `/api/v1/conversations/?character_name=${encodeURIComponent(
            characterName
          )}&limit=100`
        );
        console.log("API yanıtı:", response.data);
        const conversationsData = response.data.conversations || [];

        console.log("Alınan konuşmalar:", conversationsData);

        setConversations(conversationsData);

        // Eğer konuşma varsa ilk konuşmayı aktif olarak ayarla
        if (conversationsData.length > 0 && !activeConversation) {
          console.log(
            "İlk konuşma aktif olarak ayarlanıyor:",
            conversationsData[0]
          );
          setActiveConversation(conversationsData[0]);
        }
      } catch (err) {
        console.error("Konuşmalar getirilirken hata oluştu:", err);
        setError("Konuşmalar yüklenemedi. Lütfen daha sonra tekrar deneyin.");
      } finally {
        setLoading(false);
      }
    },
    [] // activeConversation bağımlılığını kaldırdık
  );

  // Seçili karakter değiştiğinde konuşmaları getir
  useEffect(() => {
    if (selectedCharacter) {
      // Bu karakter için daha önce istek yapılmadıysa yap
      if (!fetchedCharactersRef.current[selectedCharacter.name]) {
        fetchedCharactersRef.current[selectedCharacter.name] = true;
        fetchConversations(selectedCharacter.name);
      }
    } else {
      setConversations([]);
      setActiveConversation(null);
      setMessages([]);
    }
  }, [selectedCharacter]); // fetchConversations bağımlılığını kaldırdık

  // Aktif konuşma değiştiğinde mesajları getir
  useEffect(() => {
    if (activeConversation) {
      fetchMessages(activeConversation.id);
    } else {
      setMessages([]);
    }
  }, [activeConversation]);

  // Bir konuşmanın mesaj geçmişini getir
  const fetchMessages = async (conversationId) => {
    try {
      setLoading(true);
      setError("");

      console.log("fetchMessages çağrıldı:", conversationId);

      // API kılavuzuna göre konuşma geçmişini al
      const response = await axios.get(
        `/api/v1/chat/${conversationId}/history?limit=1000`
      );
      console.log("Mesaj geçmişi API yanıtı:", response.data);
      const messagesData = response.data.history || [];

      console.log("Alınan mesajlar:", messagesData);

      // Mesajları UI için uygun formata dönüştür
      const formattedMessages = messagesData.map((msg, index) => ({
        id: index.toString(), // Backend ID dönmüyorsa index kullan
        role: msg.role,
        content: msg.content,
        timestamp: new Date().toISOString(), // Backend timestamp dönmüyorsa şu anki zamanı kullan
      }));

      setMessages(formattedMessages);
    } catch (err) {
      console.error("Mesaj geçmişi getirilirken hata oluştu:", err);
      setError("Mesaj geçmişi yüklenemedi. Lütfen daha sonra tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  // Yeni bir konuşma oluştur
  const createConversation = async (title = "Yeni Konuşma") => {
    try {
      setLoading(true);
      setError("");

      console.log("createConversation çağrıldı:", title);

      if (!selectedCharacter) {
        throw new Error("Konuşma için seçili karakter yok");
      }

      console.log("Seçili karakter:", selectedCharacter);

      // API kılavuzuna göre yeni konuşma oluştur
      const response = await axios.post("/api/v1/conversations/", {
        character_name: selectedCharacter.name,
        title: title,
      });

      console.log("Yeni konuşma API yanıtı:", response.data);

      const newConversation = response.data;

      // Yeni konuşmayı listeye ekle
      setConversations((prev) => {
        console.log("Önceki konuşmalar:", prev);
        return [newConversation, ...prev];
      });

      // Yeni konuşmayı aktif olarak ayarla
      console.log("Yeni konuşma aktif olarak ayarlanıyor:", newConversation);
      setActiveConversation(newConversation);

      // Mesajları temizle
      setMessages([]);

      return newConversation;
    } catch (err) {
      console.error("Konuşma oluşturulurken hata oluştu:", err);
      setError("Konuşma oluşturulamadı. Lütfen tekrar deneyin.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Bir konuşmayı sil
  const deleteConversation = async (conversationId) => {
    try {
      setError("");

      // API kılavuzuna göre konuşmayı sil
      await axios.delete(`/api/v1/conversations/${conversationId}`);

      // Konuşmayı listeden kaldır
      setConversations((prev) =>
        prev.filter((conv) => conv.id !== conversationId)
      );

      // Eğer silinen konuşma aktif konuşma ise, aktif konuşmayı sıfırla
      if (activeConversation && activeConversation.id === conversationId) {
        const remainingConversations = conversations.filter(
          (conv) => conv.id !== conversationId
        );
        if (remainingConversations.length > 0) {
          setActiveConversation(remainingConversations[0]);
        } else {
          setActiveConversation(null);
          setMessages([]);
        }
      }

      return true;
    } catch (err) {
      console.error("Konuşma silinirken hata oluştu:", err);
      setError("Konuşma silinemedi. Lütfen tekrar deneyin.");
      return false;
    }
  };

  // Bir konuşmanın başlığını güncelle
  const renameConversation = async (conversationId, newTitle) => {
    try {
      setError("");

      // API kılavuzuna göre konuşma başlığını güncelle
      // eslint-disable-next-line no-unused-vars
      const response = await axios.patch(
        `/api/v1/conversations/${conversationId}`,
        {
          title: newTitle,
        }
      );

      // const updatedConversation = response.data;

      // Konuşma başlığını güncelle
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === conversationId ? { ...conv, title: newTitle } : conv
        )
      );

      // Eğer aktif konuşma ise, aktif konuşmayı da güncelle
      if (activeConversation && activeConversation.id === conversationId) {
        setActiveConversation((prev) => ({ ...prev, title: newTitle }));
      }

      return true;
    } catch (err) {
      console.error("Konuşma başlığı güncellenirken hata oluştu:", err);
      setError("Konuşma başlığı güncellenemedi. Lütfen tekrar deneyin.");
      return false;
    }
  };

  // Bir konuşmanın geçmişini temizle
  const clearConversation = async (conversationId) => {
    try {
      setError("");

      // API kılavuzuna göre konuşma geçmişini temizle
      await axios.delete(`/api/v1/conversations/${conversationId}/history`);

      // Mesajları temizle
      setMessages([]);

      return true;
    } catch (err) {
      console.error("Konuşma geçmişi temizlenirken hata oluştu:", err);
      setError("Konuşma geçmişi temizlenemedi. Lütfen tekrar deneyin.");
      return false;
    }
  };

  // Bir konuşmaya mesaj gönder
  const sendMessage = async (content, attachments = []) => {
    // Boş mesajları gönderme
    if (!content.trim() && attachments.length === 0) return;

    try {
      setError("");

      console.log("sendMessage çağrıldı:", content, attachments);

      if (!activeConversation) {
        throw new Error("Aktif konuşma yok");
      }

      console.log("Aktif konuşma:", activeConversation);

      // Kullanıcı mesajını oluştur
      const userMessage = {
        id: uuidv4(),
        role: "user",
        content,
        attachments,
        timestamp: new Date().toISOString(),
      };

      console.log("Kullanıcı mesajı oluşturuldu:", userMessage);

      // Kullanıcı mesajını UI'a ekle
      setMessages((prev) => {
        console.log("Önceki mesajlar:", prev);
        return [...prev, userMessage];
      });

      // Yazma göstergesini başlat
      setIsTyping(true);

      // AI mesajı için placeholder oluştur
      const aiMessagePlaceholder = {
        id: uuidv4(),
        role: "assistant",
        content: "", // Başlangıçta boş
        timestamp: new Date().toISOString(),
      };

      // Placeholder'ı UI'a ekle
      setMessages((prev) => [...prev, aiMessagePlaceholder]);

      try {
        // API kılavuzuna göre streaming yanıt için POST isteği
        const response = await fetch(
          `/api/v1/chat/${activeConversation.id}/stream`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: content }),
          }
        );

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let receivedContent = "";

        // Yanıtı parça parça oku
        const readChunk = async () => {
          try {
            const { done, value } = await reader.read();

            if (done) {
              console.log("Akış tamamlandı.");
              setIsTyping(false);

              // Konuşma listesini güncelle (son mesaj zamanı)
              setConversations((prev) => {
                const updatedConversations = prev.map((conv) =>
                  conv.id === activeConversation.id
                    ? { ...conv, updated_at: new Date().toISOString() }
                    : conv
                );
                console.log("Güncellenmiş konuşmalar:", updatedConversations);
                return updatedConversations;
              });

              return;
            }

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n\n");

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = line.substring(6);

                if (data === "[DONE]") {
                  console.log("Akış tamamlandı.");
                  setIsTyping(false);
                  return;
                }

                try {
                  // Veriyi JSON olarak ayrıştırmaya çalış
                  const parsedData = JSON.parse(data);

                  if (parsedData.message) {
                    const newContent = receivedContent + parsedData.message;
                    receivedContent = newContent;
                    // UI'daki placeholder mesajı güncelle
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessagePlaceholder.id
                          ? { ...msg, content: newContent }
                          : msg
                      )
                    );
                  } else if (parsedData.data) {
                    // Agentic yanıtlar için
                    const dataContent = parsedData.data.content || "";
                    const displayText = parsedData.data.display_text || "";

                    const newContent =
                      receivedContent +
                      `\n\`\`\`${parsedData.data.type}\n${dataContent}\n\`\`\`\n${displayText}`;
                    receivedContent = newContent;

                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMessagePlaceholder.id
                          ? { ...msg, content: newContent }
                          : msg
                      )
                    );
                  }
                } catch (e) {
                  // JSON ayrıştırma hatası, düz metin olarak ekle
                  const newContent = receivedContent + data;
                  receivedContent = newContent;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === aiMessagePlaceholder.id
                        ? { ...msg, content: newContent }
                        : msg
                    )
                  );
                }
              }
            }

            // Bir sonraki parçayı oku
            return readChunk();
          } catch (error) {
            console.error("Streaming okuma hatası:", error);
            setError("Mesaj alınırken bir hata oluştu.");
            setIsTyping(false);
          }
        };

        // Okuma işlemini başlat
        readChunk();
      } catch (error) {
        console.error("Fetch hatası:", error);
        setError("Mesaj gönderilemedi.");
        setIsTyping(false);

        // Hata durumunda placeholder mesajı kaldır
        setMessages((prev) =>
          prev.filter((msg) => msg.id !== aiMessagePlaceholder.id)
        );
      }
    } catch (err) {
      console.error("Mesaj gönderilirken hata oluştu:", err);
      setError("Mesaj gönderilemedi. Lütfen tekrar deneyin.");
      setIsTyping(false);
      return null;
    }
  };

  // Bir konuşmayı seç
  const selectConversation = (conversation) => {
    console.log("selectConversation çağrıldı:", conversation);
    setActiveConversation(conversation);
  };

  const value = {
    conversations,
    activeConversation,
    messages,
    isTyping,
    loading,
    error,
    fetchConversations,
    fetchMessages,
    createConversation,
    deleteConversation,
    renameConversation,
    clearConversation,
    sendMessage,
    selectConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
