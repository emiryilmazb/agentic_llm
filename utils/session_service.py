"""
Session service utilities for handling session data operations.
"""
import json
import sqlite3
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from utils.config import DB_PATH, MAX_HISTORY_MESSAGES, DEFAULT_SESSION_TIMEOUT

class SessionService:
    """Service class for handling session data operations."""
    
    @staticmethod
    def get_db_connection():
        """
        SQLite veritabanı bağlantısı oluştur.
        
        Returns:
            sqlite3.Connection: Veritabanı bağlantısı
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def create_session(system_prompt: str = "", 
                      use_agentic: bool = True, 
                      wiki_info: str = "", 
                      session_name: str = None,
                      user_id: str = None) -> str:
        """
        Yeni bir oturum oluştur.
        
        Args:
            system_prompt: Sistem promptu
            use_agentic: Agentic özellikleri kullanılsın mı
            wiki_info: Wikipedia bilgisi
            session_name: Oturum adı (belirtilmezse otomatik oluşturulur)
            user_id: Kullanıcı ID'si (belirtilmezse anonim olur)
            
        Returns:
            str: Oluşturulan oturumun ID'si
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            # Oturum ID'si oluştur
            session_id = str(uuid.uuid4())
            
            # Oturum adı belirtilmemişse tarih/saat ile oluştur
            if not session_name:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                session_name = f"Oturum {current_time}"
            
            # Oturumu veritabanına ekle
            cursor.execute("""
                INSERT INTO sessions (
                    session_id, user_id, session_name, use_agentic, 
                    system_prompt, wiki_info, session_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, session_name, 1 if use_agentic else 0, 
                  system_prompt, wiki_info, 'active'))
            
            conn.commit()
            conn.close()
            
            return session_id
        except Exception as e:
            print(f"Oturum oluşturulurken hata: {str(e)}")
            raise
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Bir oturumun bilgilerini getir.
        
        Args:
            session_id: Oturum ID'si
            
        Returns:
            Dict or None: Oturum bilgileri veya bulunamazsa None
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,))
            
            session = cursor.fetchone()
            conn.close()
            
            if session:
                return dict(session)
            return None
        except Exception as e:
            print(f"Oturum bilgileri alınırken hata: {str(e)}")
            return None
    
    @staticmethod
    def get_all_sessions(active_only: bool = False, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Tüm oturumları getir.
        
        Args:
            active_only: Sadece aktif oturumları getir
            limit: Maksimum oturum sayısı
            
        Returns:
            List: Oturum bilgilerinin listesi
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM sessions"
            params = []
            
            if active_only:
                query += " WHERE session_status = 'active'"
            
            query += " ORDER BY last_activity_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return sessions
        except Exception as e:
            print(f"Oturumlar alınırken hata: {str(e)}")
            return []
    
    @staticmethod
    def update_session_activity(session_id: str) -> bool:
        """
        Oturum aktivitesini güncelle.
        
        Args:
            session_id: Oturum ID'si
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions 
                SET last_activity_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Oturum aktivitesi güncellenirken hata: {str(e)}")
            return False
    
    @staticmethod
    def add_message(session_id: str, 
                   role: str, 
                   content: str, 
                   parent_message_id: str = None,
                   tool_calls: List[Dict[str, Any]] = None,
                   model_used: str = None,
                   temperature: float = None,
                   processing_time_ms: int = None,
                   token_count: int = None) -> Optional[str]:
        """
        Oturuma yeni bir mesaj ekle.
        
        Args:
            session_id: Oturum ID'si
            role: Mesaj rolü ('user', 'assistant', 'system')
            content: Mesaj içeriği
            parent_message_id: Üst mesaj ID'si (varsa)
            tool_calls: Araç çağrıları (varsa)
            model_used: Kullanılan model
            temperature: Sıcaklık değeri
            processing_time_ms: İşlem süresi (ms)
            token_count: Token sayısı
            
        Returns:
            str or None: Eklenen mesajın ID'si veya hata durumunda None
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            # Oturumun varlığını kontrol et
            cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
            if not cursor.fetchone():
                print(f"Oturum bulunamadı: {session_id}")
                conn.close()
                return None
            
            # Mesaj indeksini belirle
            cursor.execute("""
                SELECT COALESCE(MAX(message_index), -1) + 1 as next_index 
                FROM messages 
                WHERE session_id = ?
            """, (session_id,))
            message_index = cursor.fetchone()[0]
            
            # Mesaj ID'si oluştur
            message_id = str(uuid.uuid4())
            
            # Araç çağrılarını JSON'a dönüştür
            tool_calls_json = json.dumps(tool_calls if tool_calls else [])
            
            # Mesajı ekle
            cursor.execute("""
                INSERT INTO messages (
                    message_id, session_id, parent_message_id, message_role, 
                    message_content, tool_calls, processing_time_ms, 
                    token_count, model_used, temperature, message_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id, session_id, parent_message_id, role, 
                content, tool_calls_json, processing_time_ms, 
                token_count, model_used, temperature, message_index
            ))
            
            # Oturum mesaj sayısını güncelle
            cursor.execute("""
                UPDATE sessions 
                SET message_count = message_count + 1,
                    last_activity_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
            return message_id
        except Exception as e:
            print(f"Mesaj eklenirken hata: {str(e)}")
            return None
    
    @staticmethod
    def get_messages(session_id: str, limit: int = MAX_HISTORY_MESSAGES) -> List[Dict[str, Any]]:
        """
        Bir oturumdaki mesajları getir.
        
        Args:
            session_id: Oturum ID'si
            limit: Maksimum mesaj sayısı
            
        Returns:
            List: Mesajların listesi
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM messages 
                WHERE session_id = ? AND is_hidden = 0
                ORDER BY message_index ASC
                LIMIT ?
            """, (session_id, limit))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # JSON alanlarını parse et
            for message in messages:
                if 'tool_calls' in message and message['tool_calls']:
                    try:
                        message['tool_calls'] = json.loads(message['tool_calls'])
                    except:
                        message['tool_calls'] = []
                
                if 'message_metadata' in message and message['message_metadata']:
                    try:
                        message['message_metadata'] = json.loads(message['message_metadata'])
                    except:
                        message['message_metadata'] = {}
            
            return messages
        except Exception as e:
            print(f"Mesajlar alınırken hata: {str(e)}")
            return []
    
    @staticmethod
    def format_chat_history(session_id: str, limit: int = MAX_HISTORY_MESSAGES) -> str:
        """
        Sohbet geçmişini formatlı metin olarak getir.
        
        Args:
            session_id: Oturum ID'si
            limit: Maksimum mesaj sayısı
            
        Returns:
            str: Formatlı sohbet geçmişi
        """
        messages = SessionService.get_messages(session_id, limit)
        history_text = ""
        
        for message in messages:
            role = message["message_role"]
            content = message["message_content"]
            
            if role == "user":
                history_text += f"Kullanıcı: {content}\n"
            elif role == "assistant":
                history_text += f"Asistan: {content}\n"
            elif role == "system":
                # Sistem mesajlarını geçmişe dahil etme
                continue
        
        return history_text
    
    @staticmethod
    def clear_session_messages(session_id: str) -> bool:
        """
        Bir oturumdaki tüm mesajları temizle.
        
        Args:
            session_id: Oturum ID'si
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            # Mesajları sil
            cursor.execute("""
                DELETE FROM messages WHERE session_id = ?
            """, (session_id,))
            
            # Oturum mesaj sayısını sıfırla
            cursor.execute("""
                UPDATE sessions 
                SET message_count = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Oturum mesajları temizlenirken hata: {str(e)}")
            return False
    
    @staticmethod
    def close_session(session_id: str) -> bool:
        """
        Bir oturumu kapat.
        
        Args:
            session_id: Oturum ID'si
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            # Oturumu kapat
            cursor.execute("""
                UPDATE sessions 
                SET session_status = 'completed',
                    updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Oturum kapatılırken hata: {str(e)}")
            return False
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Bir oturumu sil.
        
        Args:
            session_id: Oturum ID'si
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            conn = SessionService.get_db_connection()
            cursor = conn.cursor()
            
            # Önce oturuma ait mesajları sil
            cursor.execute("""
                DELETE FROM messages WHERE session_id = ?
            """, (session_id,))
            
            # Sonra oturumu sil
            cursor.execute("""
                DELETE FROM sessions WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Oturum silinirken hata: {str(e)}")
            return False
    
    @staticmethod
    def get_or_create_session(session_id: str = None, 
                             system_prompt: str = "", 
                             use_agentic: bool = True) -> Tuple[str, bool]:
        """
        Bir oturumu getir veya yoksa oluştur.
        
        Args:
            session_id: Oturum ID'si (belirtilmezse yeni oluşturulur)
            system_prompt: Sistem promptu (yeni oturum için)
            use_agentic: Agentic özellikleri kullanılsın mı (yeni oturum için)
            
        Returns:
            Tuple[str, bool]: (oturum_id, yeni_mi) çifti
        """
        # Oturum ID'si belirtilmişse, varlığını kontrol et
        if session_id:
            session = SessionService.get_session(session_id)
            if session:
                # Oturum varsa, aktiviteyi güncelle
                SessionService.update_session_activity(session_id)
                return session_id, False
        
        # Oturum yoksa veya ID belirtilmemişse, yeni oluştur
        new_session_id = SessionService.create_session(
            system_prompt=system_prompt,
            use_agentic=use_agentic
        )
        
        return new_session_id, True