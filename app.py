import streamlit as st
import json
import os
from pathlib import Path

from agentic_character import AgenticCharacter
from mcp_server import get_default_server
from utils.ai_service import AIService
from utils.character_service import CharacterService
from utils.wiki_service import WikiService
from utils.config import (
    DATA_DIR,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_CHAT_TOKENS,
    APPLICATION_TITLE,
    APPLICATION_ICON,
    APPLICATION_DESCRIPTION
)

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

def get_character_response(character_data, user_message, use_agentic=False):
    """
    Karakter cevabını al, normal veya agentic modda.
    
    Args:
        character_data: Karakter verileri
        user_message: Kullanıcı mesajı
        use_agentic: Agentic mod kullanılsın mı
        
    Returns:
        Tuple of (character_response, response_data)
    """
    try:
        if use_agentic:
            # Agentic karakter oluştur ve cevap al
            character = AgenticCharacter(character_data)
            response = character.get_response(user_message)
            
            # Karakter verilerini güncellenmiş sohbet geçmişiyle kaydet
            character_data["chat_history"] = character.chat_history
            character_data["prompt"] = character.prompt
            
            # Güncellenmiş karakter verilerini hemen kaydet
            CharacterService.save_character_data(character_data["name"], character_data)
            
            # Cevabı dönüştür
            return response["display_text"], response
        else:
            # Normal mod - CharacterService ve AIService kullan
            prompt = character_data["prompt"]
            
            # Son 10 konuşmayı içeren bir metin oluştur
            history_text = CharacterService.format_chat_history(
                character_data["chat_history"], 
                character_data["name"]
            )
            
            # Tam promptu oluştur
            full_prompt = f"""{prompt}

Sohbet geçmişi:
{history_text}

Kullanıcı: {user_message}
{character_data['name']}:"""
            
            # AIService kullanarak cevap al
            response_text = AIService.generate_response(
                prompt=full_prompt,
                model_name=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_CHAT_TOKENS,
                top_p=DEFAULT_TOP_P
            )
            
            return response_text, None
    except Exception as e:
        error_msg = f"Bir hata oluştu: {str(e)}"
        return error_msg, None

def update_character_history(character_name, user_message, character_response, response_data=None):
    """
    Sohbet geçmişini güncelle.
    
    Args:
        character_name: Karakter adı
        user_message: Kullanıcı mesajı
        character_response: Karakter cevabı
        response_data: Ekstra yanıt verileri (agentic mod için)
    """
    # CharacterService kullanarak geçmişi güncelle
    CharacterService.update_chat_history(
        character_name, 
        user_message, 
        character_response, 
        response_data
    )

def delete_dynamic_tool(tool_name):
    """
    Dinamik bir aracı sil
    
    Args:
        tool_name: Silinecek aracın adı
    
    Returns:
        bool: Silme işlemi başarılı ise True, değilse False
    """
    try:
        # MCP sunucusundan aracı kaldır
        mcp_server = get_default_server()
        success = mcp_server.unregister_tool(tool_name)
        
        if success:
            # Araç dosyasını bul ve sil
            tool_filename = ''.join(['_' + c.lower() if c.isupper() else c for c in tool_name]).lstrip('_')
            if not tool_filename.endswith('_tool'):
                tool_filename += '_tool'
            
            tool_path = Path(f"dynamic_tools/{tool_filename}.py")
            module_name = f"dynamic_tools.{tool_filename}"
            
            # Python'un sys.modules önbelleğinden modülü kaldır
            import sys
            if module_name in sys.modules:
                del sys.modules[module_name]
                print(f"Removed module from sys.modules: {module_name}")
            
            # Silinen araçları takip etmek için bir dosya oluştur veya güncelle
            deleted_tools_path = Path("dynamic_tools/deleted_tools.json")
            deleted_tools = []
            
            if deleted_tools_path.exists():
                try:
                    with open(deleted_tools_path, "r", encoding="utf-8") as f:
                        deleted_tools = json.load(f)
                except json.JSONDecodeError:
                    deleted_tools = []
            
            if tool_name not in deleted_tools:
                deleted_tools.append(tool_name)
                
            with open(deleted_tools_path, "w", encoding="utf-8") as f:
                json.dump(deleted_tools, f, ensure_ascii=False, indent=4)
            
            if tool_path.exists():
                tool_path.unlink()  # Dosyayı sil
                print(f"Deleted tool file: {tool_path}")
            
            return True
        return False
    except Exception as e:
        print(f"Error deleting tool: {str(e)}")
        return False

def main():
    st.set_page_config(page_title=APPLICATION_TITLE, page_icon=APPLICATION_ICON, layout="wide")
    
    st.title(f"{APPLICATION_ICON} Agentic Karakter Chatbot")
    st.markdown(APPLICATION_DESCRIPTION)
    
    # Yan menü
    with st.sidebar:
        st.header("Karakter Yönetimi")
        
        # Karakter seçimi
        characters = CharacterService.get_all_characters()
        selected_option = st.radio(
            "Ne yapmak istersiniz?",
            ["Var olan karakterle konuşun", "Yeni karakter oluşturun"]
        )
        
        # MCP sunucu bilgisi
        with st.expander("🛠️ Kullanılabilir Araçlar"):
            mcp_server = get_default_server()
            tools_info = mcp_server.get_tools_info()
            
            # Yerleşik araçlar ve dinamik araçları ayır
            built_in_tools = []
            dynamic_tools = []
            
            for tool in tools_info:
                if tool['name'] in ['search_wikipedia', 'get_current_time', 'get_weather', 'open_website', 'calculate_math']:
                    built_in_tools.append(tool)
                else:
                    dynamic_tools.append(tool)
            
            # Yerleşik araçları göster
            st.subheader("Yerleşik Araçlar")
            for tool in built_in_tools:
                st.markdown(f"**{tool['name']}**: {tool['description']}")
            
            # Dinamik araçları göster (varsa)
            if dynamic_tools:
                st.subheader("Dinamik Oluşturulan Araçlar")
                for tool in dynamic_tools:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{tool['name']}**: {tool['description']}")
                    with col2:
                        if st.button("🗑️ Sil", key=f"delete_{tool['name']}"):
                            if delete_dynamic_tool(tool['name']):
                                st.success(f"{tool['name']} aracı başarıyla silindi!")
                                st.rerun()  # Sayfayı yenile
                            else:
                                st.error(f"{tool['name']} aracı silinirken bir hata oluştu.")
                st.info("Dinamik araçlar, kullanıcı ihtiyaçlarına göre otomatik olarak oluşturulur.")
        
        if selected_option == "Var olan karakterle konuşun":
            if characters:
                selected_character = st.selectbox("Karakter seçin", characters)
                if st.button("Bu karakterle konuş"):
                    st.session_state.active_character = selected_character
                    st.session_state.chat_started = True
            else:
                st.warning("Henüz kaydedilmiş karakter bulunmuyor. Lütfen önce bir karakter oluşturun.")
        
        elif selected_option == "Yeni karakter oluşturun":
            st.subheader("Yeni Karakter Oluştur")
            
            character_name = st.text_input("Karakter Adı (örn. Atatürk, Harry Potter, vb.)")
            
            use_wiki = st.checkbox("Wikipedia'dan bilgi çek", value=True)
            wiki_info = None
            
            if use_wiki and character_name:
                wiki_button = st.button("Wikipedia'dan Bilgi Çek")
                if wiki_button:
                    with st.spinner(f"{character_name} hakkında bilgi çekiliyor..."):
                        # WikiService kullanarak bilgi çek
                        wiki_info = WikiService.fetch_info(character_name)
                        st.session_state.wiki_info = wiki_info
                        st.success("Bilgi çekildi!")
            
            if 'wiki_info' in st.session_state:
                st.text_area("Wikipedia Bilgisi", st.session_state.wiki_info, height=150)
            
            character_background = st.text_area(
                "Karakter Geçmişi", 
                placeholder="Karakterin geçmişini, hikayesini ve önemli olayları yazın..."
            )
            
            character_personality = st.text_area(
                "Karakter Kişiliği",
                placeholder="Karakterin kişilik özelliklerini, konuşma tarzını ve davranışlarını yazın..."
            )
            
            use_agentic = st.checkbox("Agentic Özellikleri Etkinleştir", value=True, 
                                      help="Karakterin eylemler gerçekleştirmesine ve araçlar kullanmasına izin verir")
            
            if st.button("Karakteri Oluştur"):
                if character_name:
                    wiki_data = st.session_state.get('wiki_info', None) if use_wiki else None
                    
                    # Wikipedia'dan bilgi çekilmediyse geçmiş ve kişilik zorunlu
                    if not wiki_data and (not character_background or not character_personality):
                        st.error("Wikipedia'dan bilgi çekilmediyse, lütfen hem karakter geçmişini hem de kişilik bilgisini doldurun.")
                    else:
                        # CharacterService kullanarak karakteri oluştur ve kaydet
                        prompt = CharacterService.create_prompt(
                            character_name, 
                            character_background, 
                            character_personality, 
                            wiki_data
                        )
                        CharacterService.save_character(
                            character_name, 
                            character_background, 
                            character_personality, 
                            prompt, 
                            wiki_data, 
                            use_agentic
                        )
                        st.success(f"{character_name} karakteri başarıyla oluşturuldu!")
                        
                        # Session state'i güncelle
                        st.session_state.active_character = character_name
                        st.session_state.chat_started = True
                        st.rerun()
                else:
                    st.error("Lütfen karakter adını doldurun.")

    
    # Ana sohbet alanı
    if 'chat_started' not in st.session_state:
        st.session_state.chat_started = False
        
    if 'active_character' not in st.session_state:
        st.session_state.active_character = None
        
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Aktif karakter varsa sohbet alanını göster
    if st.session_state.chat_started and st.session_state.active_character:
        character_data = CharacterService.load_character(st.session_state.active_character)
        
        if character_data:
            st.subheader(f"{character_data['name']} ile Sohbet")
            
            # Karakter bilgilerini göster
            with st.expander("Karakter Hakkında"):
                st.write(f"**Kişilik:** {character_data['personality']}")
                if character_data.get('background'):
                    st.write(f"**Geçmiş:** {character_data['background']}")
                if character_data.get('wiki_info'):
                    st.write(f"**Wikipedia Bilgisi:** {character_data['wiki_info']}")
            
            # Sohbeti temizle butonu
            col1, col2 = st.columns([6, 1])
            with col2:
                if st.button("🗑️ Sohbeti Temizle"):
                    # Session state'teki mesajları temizle
                    st.session_state.messages = []
                    # Karakter sohbet geçmişini temizle
                    character_data["chat_history"] = []
                    # Güncellenen karakteri kaydet
                    CharacterService.save_character_data(st.session_state.active_character, character_data)
                    st.rerun()
            
            # Sohbet geçmişini göster
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            # Kullanıcı mesajı
            user_message = st.chat_input("Mesajınızı yazın...")
            
            if user_message:
                # Kullanıcı mesajını göster
                with st.chat_message("user"):
                    st.write(user_message)
                
                # Kullanıcı mesajını session state'e ekle
                st.session_state.messages.append({"role": "user", "content": user_message})
                
                # Karakterin agentic özelliğini kontrol et
                use_agentic = character_data.get("use_agentic", False)
                
                # Karakterin cevabını al
                with st.chat_message("assistant"):
                    with st.spinner(f"{character_data['name']} yazıyor..."):
                        character_response, response_data = get_character_response(character_data, user_message, use_agentic)
                        st.write(character_response)
                
                # Karakterin cevabını session state'e ekle
                st.session_state.messages.append({"role": "assistant", "content": character_response})
                
                # Sohbet geçmişini güncelle
                update_character_history(st.session_state.active_character, user_message, character_response, response_data)
        else:
            st.error("Karakter bulunamadı. Lütfen başka bir karakter seçin.")
    else:
        st.info("👈 Sohbete başlamak için yan menüden bir karakter seçin veya yeni bir karakter oluşturun.")

if __name__ == "__main__":
    main()
