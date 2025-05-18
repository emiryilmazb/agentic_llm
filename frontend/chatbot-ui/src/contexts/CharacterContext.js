import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const CharacterContext = createContext(null);

export const useCharacter = () => {
  return useContext(CharacterContext);
};

export const CharacterProvider = ({ children }) => {
  const [characters, setCharacters] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Uygulama başladığında karakterleri getir
  useEffect(() => {
    fetchCharacters();
  }, []);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get("/api/v1/characters/");
      const charactersData = response.data;

      setCharacters(charactersData);

      // Eğer henüz bir karakter seçilmemişse, ilkini seç
      if (!selectedCharacter && charactersData.length > 0) {
        setSelectedCharacter(charactersData[0]);
      }
    } catch (err) {
      console.error("Karakterler getirilirken hata oluştu:", err);
      setError("Karakterler yüklenemedi. Lütfen daha sonra tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  const createCharacter = async (characterData) => {
    try {
      setError("");

      const response = await axios.post("/api/v1/characters/", characterData);
      const newCharacter = response.data;

      setCharacters((prev) => [...prev, newCharacter]);
      return newCharacter;
    } catch (err) {
      console.error("Karakter oluşturulurken hata oluştu:", err);
      setError("Karakter oluşturulamadı. Lütfen tekrar deneyin.");
      return null;
    }
  };

  const getCharacter = async (name) => {
    try {
      setError("");

      const response = await axios.get(`/api/v1/characters/${name}`);
      const character = response.data;

      return character;
    } catch (err) {
      console.error("Karakter getirilirken hata oluştu:", err);
      setError("Karakter getirilemedi. Lütfen tekrar deneyin.");
      return null;
    }
  };

  const deleteCharacter = async (name) => {
    try {
      setError("");

      await axios.delete(`/api/v1/characters/${name}`);

      // Karakter listesinden silinen karakteri kaldır
      setCharacters((prev) => prev.filter((char) => char.name !== name));

      // Eğer silinen karakter şu anda seçiliyse, başka bir karakter seç
      if (selectedCharacter?.name === name) {
        const remainingCharacters = characters.filter(
          (char) => char.name !== name
        );
        if (remainingCharacters.length > 0) {
          setSelectedCharacter(remainingCharacters[0]);
        } else {
          setSelectedCharacter(null);
        }
      }

      return true;
    } catch (err) {
      console.error("Karakter silinirken hata oluştu:", err);
      setError("Karakter silinemedi. Lütfen tekrar deneyin.");
      return false;
    }
  };

  const selectCharacter = (character) => {
    setSelectedCharacter(character);
  };

  const value = {
    characters,
    selectedCharacter,
    loading,
    error,
    fetchCharacters,
    createCharacter,
    getCharacter,
    deleteCharacter,
    selectCharacter,
  };

  return (
    <CharacterContext.Provider value={value}>
      {children}
    </CharacterContext.Provider>
  );
};
