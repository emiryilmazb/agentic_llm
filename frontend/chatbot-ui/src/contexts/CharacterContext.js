import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
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
  const fetchedRef = useRef(false);

  const fetchCharacters = useCallback(async () => {
    try {
      console.log(
        "fetchCharacters çağrıldı, selectedCharacter:",
        selectedCharacter?.name
      );
      setLoading(true);
      setError("");

      const response = await axios.get("/api/v1/characters/");
      const data = response.data;

      console.log("API yanıtı:", data);

      // API yanıt yapısına göre karakterleri ayarla
      if (data && Array.isArray(data.characters)) {
        console.log("Karakterler ayarlanıyor:", data.characters);

        // Geçerli karakter nesnelerini filtrele
        const validCharacters = data.characters.filter(
          (char) => char && typeof char === "object"
        );
        console.log("Geçerli karakterler:", validCharacters);
        setCharacters(validCharacters);

        // Eğer henüz bir karakter seçilmemişse ve karakter listesi boş değilse, ilkini seç
        if (!selectedCharacter && validCharacters.length > 0) {
          setSelectedCharacter(validCharacters[0]);
        }
      } else if (data && Array.isArray(data)) {
        // Eğer data doğrudan bir dizi ise
        console.log("Karakterler doğrudan dizi olarak ayarlanıyor:", data);

        // Geçerli karakter nesnelerini filtrele
        const validCharacters = data.filter(
          (char) => char && typeof char === "object"
        );
        console.log("Geçerli karakterler:", validCharacters);
        setCharacters(validCharacters);

        // Eğer henüz bir karakter seçilmemişse ve karakter listesi boş değilse, ilkini seç
        if (!selectedCharacter && validCharacters.length > 0) {
          setSelectedCharacter(validCharacters[0]);
        }
      } else {
        console.log("API yanıtı beklenen formatta değil:", data);
        // Hiçbir şey bulunamazsa boş dizi kullan
        setCharacters([]);
      }
    } catch (err) {
      console.error("Karakterler getirilirken hata oluştu:", err);
      setError("Karakterler yüklenemedi. Lütfen daha sonra tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  }, []); // selectedCharacter bağımlılığını kaldırdık

  // Uygulama başladığında karakterleri getir
  useEffect(() => {
    // Sadece bir kez çağrılmasını sağla (Strict Mode'da bile)
    if (!fetchedRef.current) {
      fetchedRef.current = true;
      fetchCharacters();
    }
  }, []); // Boş bağımlılık dizisi, sadece bileşen ilk render edildiğinde çalışır

  const createCharacter = async (characterData) => {
    try {
      setError("");

      // API'nin beklediği formata dönüştür
      const apiCharacterData = {
        name: characterData.name,
        personality: characterData.personality,
        background: characterData.description,
        use_wiki: true, // Varsayılan olarak Wikipedia'dan bilgi alınsın
        use_agentic: true, // Varsayılan olarak agentic özellikler etkinleştirilsin
      };

      const response = await axios.post(
        "/api/v1/characters/",
        apiCharacterData
      );
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

      const response = await axios.get(
        `/api/v1/characters/${encodeURIComponent(name)}`
      );
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

      await axios.delete(`/api/v1/characters/${encodeURIComponent(name)}`);

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
