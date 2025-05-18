import React, { createContext, useContext, useState, useEffect } from "react";
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
  const { tools, executeTool } = useTool();

  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Seçili karakter değiştiğinde konuşmaları getir
  useEffect(() => {
    if (selectedCharacter) {
      fetchConversations(selectedCharacter.name);
    } else {
      setConversations([]);
      setActiveConversation(null);
      setMessages([]);
    }
  }, [selectedCharacter]);

  // Aktif konuşma değiştiğinde mesajları getir
  useEffect(() => {
    if (activeConversation) {
      fetchMessages(activeConversation.id);
    } else {
      setMessages([]);
    }
  }, [activeConversation]);

  // Belirli bir karakter için konuşmaları getir
  const fetchConversations = async (characterName) => {
    try {
      setLoading(true);
      setError("");

      console.log("fetchConversations çağrıldı:", characterName);

      const response = await axios.get(
        `/api/v1/conversations/?character_name=${characterName}`
      );
      console.log("API yanıtı:", response.data);
      const conversationsData = response.data.conversations;

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
  };

  // Bir konuşmanın mesaj geçmişini getir
  const fetchMessages = async (conversationId) => {
    try {
      setLoading(true);
      setError("");

      console.log("fetchMessages çağrıldı:", conversationId);

      const response = await axios.get(
        `/api/v1/chat/${conversationId}/history`
      );
      console.log("Mesaj geçmişi API yanıtı:", response.data);
      const messagesData = response.data.history || [];

      console.log("Alınan mesajlar:", messagesData);

      setMessages(messagesData);
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

      await axios.patch(`/api/v1/conversations/${conversationId}`, {
        title: newTitle,
      });

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

      await axios.delete(`/api/v1/conversations/${conversationId}/history`);
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

      // EventSource ile streaming bağlantısı kur
      const eventSource = new EventSource(
        `/api/v1/chat/${
          activeConversation.id
        }/stream?message=${encodeURIComponent(
          content
        )}&attachments=${encodeURIComponent(JSON.stringify(attachments))}`
      );

      let receivedContent = "";

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("EventSource mesajı:", data);

        if (data.type === "stream") {
          receivedContent += data.content;
          // UI'daki placeholder mesajı güncelle
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessagePlaceholder.id
                ? { ...msg, content: receivedContent }
                : msg
            )
          );
        } else if (data.type === "tool_code") {
          // Araç kodu geldiğinde, bunu mesaj içeriğine ekleyebilir veya ayrı bir şekilde gösterebilirsiniz.
          // Şimdilik mesaj içeriğine ekleyelim.
          receivedContent += `\n\`\`\`tool_code\n${data.content}\n\`\`\``;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessagePlaceholder.id
                ? { ...msg, content: receivedContent }
                : msg
            )
          );
        } else if (data.type === "tool_output") {
          // Araç çıktısı geldiğinde, bunu mesaj içeriğine ekleyebilir veya ayrı bir şekilde gösterebilirsiniz.
          // Şimdilik mesaj içeriğine ekleyelim.
          receivedContent += `\n\`\`\`tool_output\n${data.content}\n\`\`\``;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessagePlaceholder.id
                ? { ...msg, content: receivedContent }
                : msg
            )
          );
        } else if (data.type === "end") {
          // Akış tamamlandı
          console.log("Akış tamamlandı.");
          setIsTyping(false);
          eventSource.close();

          // Konuşma listesini güncelle (son mesaj zamanı)
          setConversations((prev) => {
            const updatedConversations = prev.map((conv) =>
              conv.id === activeConversation.id
                ? { ...conv, lastMessageTimestamp: new Date().toISOString() }
                : conv
            );
            console.log("Güncellenmiş konuşmalar:", updatedConversations);
            return updatedConversations;
          });
        }
      };

      eventSource.onerror = (err) => {
        console.error("EventSource hatası:", err);
        setError("Mesaj alınırken bir hata oluştu.");
        setIsTyping(false);
        eventSource.close();
      };

      // EventSource bağlantısı açıldığında
      eventSource.onopen = () => {
        console.log("EventSource bağlantısı açıldı.");
      };
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
