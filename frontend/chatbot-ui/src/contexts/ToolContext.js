import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
} from "react";
import axios from "axios";

const ToolContext = createContext(null);

export const useTool = () => {
  return useContext(ToolContext);
};

export const ToolProvider = ({ children }) => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const fetchedRef = useRef(false);

  // Uygulama başladığında araçları getir
  useEffect(() => {
    // Sadece bir kez çağrılmasını sağla (Strict Mode'da bile)
    if (!fetchedRef.current) {
      fetchedRef.current = true;
      fetchTools();
    }
  }, []); // Boş bağımlılık dizisi, sadece bileşen ilk render edildiğinde çalışır

  const fetchTools = async () => {
    try {
      console.log("fetchTools çağrıldı");
      setLoading(true);
      setError("");

      const response = await axios.get("/api/v1/tools/");
      const toolsData = response.data;

      console.log("Tools API yanıtı:", toolsData);

      // API yanıt yapısını kontrol et
      if (toolsData && typeof toolsData === "object") {
        // API yanıt yapısına göre araçları birleştir
        const allTools = [
          ...(toolsData.built_in_tools || []),
          ...(toolsData.dynamic_tools || []),
        ];

        console.log("Birleştirilmiş araçlar:", allTools);

        // Araçların geçerli olduğundan emin ol
        const validTools = allTools.filter(
          (tool) => tool && typeof tool === "object"
        );
        console.log("Geçerli araçlar:", validTools);

        setTools(validTools);
      } else if (Array.isArray(toolsData)) {
        // Eğer doğrudan bir dizi dönerse
        console.log("Araçlar doğrudan dizi olarak alındı:", toolsData);
        const validTools = toolsData.filter(
          (tool) => tool && typeof tool === "object"
        );
        setTools(validTools);
      } else {
        console.log("API yanıtı beklenen formatta değil:", toolsData);
        setTools([]);
      }
    } catch (err) {
      console.error("Araçlar getirilirken hata oluştu:", err);
      setError("Araçlar yüklenemedi. Lütfen daha sonra tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  const getToolDetails = async (toolName) => {
    try {
      setError("");

      const response = await axios.get(
        `/api/v1/tools/${encodeURIComponent(toolName)}`
      );
      const toolDetails = response.data;

      return toolDetails;
    } catch (err) {
      console.error("Araç detayları getirilirken hata oluştu:", err);
      setError("Araç detayları getirilemedi. Lütfen tekrar deneyin.");
      return null;
    }
  };

  const deleteTool = async (toolName) => {
    try {
      setError("");

      await axios.delete(`/api/v1/tools/${encodeURIComponent(toolName)}`);

      // Araç listesinden silinen aracı kaldır
      setTools((prev) => prev.filter((tool) => tool.name !== toolName));

      return true;
    } catch (err) {
      console.error("Araç silinirken hata oluştu:", err);
      setError("Araç silinemedi. Lütfen tekrar deneyin.");
      return false;
    }
  };

  // Not: API kılavuzunda araç çalıştırma için doğrudan bir endpoint bulunmamaktadır.
  // Araçlar, sohbet API'si üzerinden kullanılmaktadır.

  const value = {
    tools,
    loading,
    error,
    fetchTools,
    getToolDetails,
    deleteTool,
  };

  return <ToolContext.Provider value={value}>{children}</ToolContext.Provider>;
};
