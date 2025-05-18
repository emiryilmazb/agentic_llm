import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const ToolContext = createContext(null);

export const useTool = () => {
  return useContext(ToolContext);
};

export const ToolProvider = ({ children }) => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Uygulama başladığında araçları getir
  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get("/api/v1/tools/");
      const toolsData = response.data;

      setTools(toolsData);
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

      const response = await axios.get(`/api/v1/tools/${toolName}`);
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

      await axios.delete(`/api/v1/tools/${toolName}`);

      // Araç listesinden silinen aracı kaldır
      setTools((prev) => prev.filter((tool) => tool.name !== toolName));

      return true;
    } catch (err) {
      console.error("Araç silinirken hata oluştu:", err);
      setError("Araç silinemedi. Lütfen tekrar deneyin.");
      return false;
    }
  };

  const executeTool = async (id, params) => {
    try {
      setError("");

      // Find the tool
      const tool = tools.find((t) => t.id === id);
      if (!tool) {
        throw new Error("Tool not found");
      }

      // In a real implementation, this would call the API
      // const response = await axios.post(`${tool.endpoint}`, params);
      // return response.data;

      // Mock execution until API endpoints are provided
      // This is a simple simulation - in real app we'd call the actual backend
      if (tool.name === "Weather Tool") {
        return {
          success: true,
          data: {
            location: params.location,
            temperature: Math.floor(Math.random() * 30) + 5,
            condition: ["Sunny", "Cloudy", "Rainy", "Windy"][
              Math.floor(Math.random() * 4)
            ],
            humidity: Math.floor(Math.random() * 100),
            units: params.units || "metric",
          },
        };
      } else if (tool.name === "Search Tool") {
        return {
          success: true,
          data: {
            query: params.query,
            results: [
              {
                title: "Result 1 for " + params.query,
                url: "https://example.com/1",
              },
              {
                title: "Result 2 for " + params.query,
                url: "https://example.com/2",
              },
              {
                title: "Result 3 for " + params.query,
                url: "https://example.com/3",
              },
            ].slice(0, params.limit || 5),
          },
        };
      } else {
        return {
          success: true,
          data: {
            message: `Mock execution for tool: ${tool.name}`,
            params: params,
          },
        };
      }
    } catch (err) {
      console.error("Failed to execute tool:", err);
      setError(`Failed to execute tool: ${err.message}`);
      return {
        success: false,
        error: err.message,
      };
    }
  };

  const value = {
    tools,
    loading,
    error,
    fetchTools,
    getToolDetails,
    deleteTool,
    executeTool,
  };

  return <ToolContext.Provider value={value}>{children}</ToolContext.Provider>;
};
