import gradio as gr
import json
import os
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

from mcp_server import get_default_server
from utils.ai_service import AIService
from utils.session_service import SessionService
from utils.wiki_service import WikiService
from utils.config import (
    DB_PATH,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_CHAT_TOKENS,
    DEFAULT_MAX_TOKENS,
    APPLICATION_TITLE,
    APPLICATION_ICON,
    APPLICATION_DESCRIPTION
)

def get_response(session_id, user_message, use_agentic=False):
    """
    Kullanıcı mesajına yanıt al.
    
    Args:
        session_id: Oturum ID'si
        user_message: Kullanıcı mesajı
        use_agentic: Agentic mod kullanılsın mı
        
    Returns:
        str: Asistan yanıtı
    """
    try:
        # Oturum bilgilerini al
        session = SessionService.get_session(session_id)
        if not session:
            return "Oturum bulunamadı. Lütfen yeni bir oturum başlatın."
        
        # Oturum aktivitesini güncelle
        SessionService.update_session_activity(session_id)
        
        # Kullanıcı mesajını veritabanına ekle
        user_message_id = SessionService.add_message(
            session_id=session_id,
            role="user",
            content=user_message
        )
        
        # Agentic mod etkinse ve tool gerektiren bir istek varsa
        tool_info = None
        tool_name = None
        tool_result = None
        
        # Tool ihtiyacı değişkeni
        direct_tool_needed = False
        
        if use_agentic and "tool" in user_message.lower():
            # DynamicToolManager'ı import et
            from utils.dynamic_tool_manager import DynamicToolManager
            
            print(f"Kullanıcı mesajı analiz ediliyor: '{user_message}'")
            
            # Kullanıcı mesajına göre yeni bir tool oluştur ve kaydet
            success, tool_name, tool_info = DynamicToolManager.create_and_register_tool(user_message)
            
            if success:
                print(f"Tool oluşturma kararı: EVET - '{tool_name}' tool'u oluşturuldu")
            else:
                print(f"Tool oluşturma kararı: HAYIR - Yeni tool'a ihtiyaç yok veya oluşturulamadı")
            
            if success and tool_name:
                print(f"Tool oluşturuldu ve kaydedildi: {tool_name}")
                
                # MCP sunucusundan tool'u al ve çalıştır
                from mcp_server import get_default_server
                mcp_server = get_default_server()
                
                # Tool parametrelerini belirle
                tool_args = {}
                
                # Parametre çıkarımı
                import re
                
                # AI'ın tool_name'e göre parametreleri belirlemesi
                # Kullanıcı mesajını ve tool adını AI'a gönder ve parametreleri çıkarmasını iste
                prompt = f"""
                Kullanıcı mesajı: "{user_message}"
                
                Tool adı: "{tool_name}"
                
                Bu tool için gerekli parametreleri kullanıcı mesajından çıkar.
                Eğer bir parametre için değer bulamazsan, mantıklı bir varsayılan değer kullan.
                
                Yanıtını sadece JSON formatında ver, başka açıklama yapma:
                {{
                    "parameters": {{
                        "parametre1": "değer1",
                        "parametre2": "değer2",
                        ...
                    }}
                }}
                """
                
                # AI'dan parametreleri al
                parameter_response = AIService.generate_response(
                    prompt=prompt,
                    model_name=DEFAULT_MODEL,
                    temperature=0.2,
                    max_tokens=DEFAULT_MAX_TOKENS,
                    top_p=DEFAULT_TOP_P
                )
                
                # JSON yanıtını çıkar
                import re
                import json
                
                json_match = re.search(r'({.*})', parameter_response, re.DOTALL)
                if json_match:
                    try:
                        parameter_result = json.loads(json_match.group(1))
                        tool_args = parameter_result.get("parameters", {})
                        print(f"AI tarafından çıkarılan parametreler: {tool_args}")
                    except json.JSONDecodeError:
                        print(f"Parametre yanıtı JSON formatında değil: {parameter_response}")
                        tool_args = {}
                else:
                    print(f"Parametre yanıtında JSON bulunamadı: {parameter_response}")
                    tool_args = {}
                
                # Tool'u çalıştır
                try:
                    tool_result = mcp_server.execute_tool(tool_name, tool_args)
                    print(f"Tool çalıştırıldı: {tool_name}, Sonuç: {tool_result}")
                except Exception as e:
                    # Tool çalıştırma sırasında bir hata oluştu
                    error_message = str(e)
                    print(f"Tool çalıştırma sırasında hata: {error_message}")
                    tool_result = {"error": error_message}
                
                # Hata kontrolü
                if "error" in tool_result:
                    error_message = tool_result["error"]
                    print(f"Tool çalıştırma hatası: {error_message}")
                    
                    # Otomatik debug ve düzeltme dene
                    print("Tool otomatik debug ve düzeltme deneniyor...")
                    from utils.dynamic_tool_manager import DynamicToolManager
                    debug_success, fixed_tool_name, fixed_tool_info = DynamicToolManager.debug_and_fix_tool(
                        tool_name,
                        error_message,
                        tool_args
                    )
                    
                    if debug_success:
                        print(f"Tool başarıyla düzeltildi: {fixed_tool_name}")
                        # Düzeltilen tool'u çalıştır
                        tool_result = mcp_server.execute_tool(fixed_tool_name, tool_args)
                        print(f"Düzeltilen tool çalıştırıldı: {fixed_tool_name}, Sonuç: {tool_result}")
                        # Tool adını güncelle
                        tool_name = fixed_tool_name
                        tool_info = fixed_tool_info
                    else:
                        print("Otomatik düzeltme başarısız oldu, alternatif çözümler deneniyor...")
                        
                        # Hata durumunda alternatif tool'ları dene
                        if "currency" in tool_name.lower() and tool_name != "currency_converter":
                            print("Alternatif olarak currency_converter aracı deneniyor...")
                            tool_result = mcp_server.execute_tool("currency_converter", tool_args)
                            print(f"Alternatif araç çalıştırıldı: currency_converter, Sonuç: {tool_result}")
                        
                        # Parametrelerde eksiklik varsa, varsayılan değerlerle tekrar dene
                        elif "Missing required parameters" in error_message or "required" in error_message.lower():
                            print("Eksik parametreler için varsayılan değerler kullanılıyor...")
                            
                            # Döviz kuru için varsayılan parametreler
                            if "currency" in tool_name.lower():
                                tool_args = {
                                    "from_currency": "USD",
                                    "to_currency": "TRY",
                                    "amount": 1.0
                                }
                            # Hava durumu için varsayılan parametreler
                            elif "weather" in tool_name.lower():
                                tool_args = {
                                    "location": "Istanbul"
                                }
                            # Çeviri için varsayılan parametreler
                            elif "translate" in tool_name.lower():
                                tool_args = {
                                    "text": user_message,
                                    "target_language": "tr",
                                    "source_language": "auto"
                                }
                                
                            # Varsayılan parametrelerle tekrar dene
                            tool_result = mcp_server.execute_tool(tool_name, tool_args)
                            print(f"Varsayılan parametrelerle araç çalıştırıldı: {tool_name}, Sonuç: {tool_result}")
        
        # Sohbet geçmişini al
        history_text = SessionService.format_chat_history(session_id)
        
        # Sistem promptunu al
        system_prompt = session.get("system_prompt", "")
        if not system_prompt:
            system_prompt = "Sen yardımcı bir yapay zeka asistanısın. Kullanıcının sorularına doğru ve yararlı yanıtlar ver."
        
        # Tool bilgilerini sistem promptuna ekle
        if tool_info and tool_name and tool_result:
            tool_prompt = f"""
Kullanıcının isteği için '{tool_name}' adlı bir araç oluşturuldu ve kullanıldı.
Araç açıklaması: {tool_info.get('tool_description', 'Belirtilmemiş')}
Araç sonucu: {json.dumps(tool_result, ensure_ascii=False, indent=2)}

Bu aracın sonuçlarını kullanarak kullanıcının sorusuna yanıt ver. Aracın nasıl oluşturulduğundan bahsetme, sadece sonuçları kullan.

ÖNEMLİ: Eğer döviz kuru bilgisi veriyorsan, şu formatı kullan:
1 {tool_args.get('from_currency', 'USD')} = {tool_result.get('rate', 'N/A')} {tool_args.get('to_currency', 'TRY')}
{tool_args.get('amount', 1)} {tool_args.get('from_currency', 'USD')} = {tool_result.get('converted_amount', 'N/A')} {tool_args.get('to_currency', 'TRY')}
Son güncelleme: {tool_result.get('last_updated', 'Belirtilmemiş')}
"""
            system_prompt = f"{system_prompt}\n\n{tool_prompt}"
        
        # Tam promptu oluştur
        full_prompt = f"""{system_prompt}

Sohbet geçmişi:
{history_text}

Kullanıcı: {user_message}
Asistan:"""
        
        # AIService kullanarak cevap al
        start_time = datetime.now()
        response_text = AIService.generate_response(
            prompt=full_prompt,
            model_name=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_CHAT_TOKENS,
            top_p=DEFAULT_TOP_P
        )
        end_time = datetime.now()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Yanıt validasyonu - Eğer tool kullanılmadıysa ve agentic mod etkinse
        if use_agentic and not tool_result:
            # Gemini'nin thinking modelini kullanarak yanıtı değerlendir
            validation_question = f"""
            Aşağıdaki yanıtı değerlendir ve bu yanıtın güncel ve doğru bilgi içerip içermediğini belirle.
            
            Kullanıcı sorusu: {user_message}
            
            Asistan yanıtı: {response_text}
            
            Eğer yanıt eski bilgi içeriyorsa, belirsizse veya "bilmiyorum" gibi ifadeler içeriyorsa,
            veya daha güncel/doğru bilgi için bir tool kullanılması gerekiyorsa, bunu detaylı olarak açıkla.
            
            Sonuç olarak, bu yanıt için bir tool'a ihtiyaç var mı? Eğer varsa, hangi tür bir tool gerekiyor?
            (currency_converter/weather_tool/translation_tool/other)
            
            Yanıtını şu formatta ver:
            {{
                "needs_tool": true/false,
                "reason": "Neden bir tool'a ihtiyaç var/yok açıklaması",
                "suggested_tool_type": "currency_converter/weather_tool/translation_tool/other"
            }}
            """
            
            # Thinking modeli ile değerlendirme yap
            validation_result_dict = AIService.generate_thinking_response(
                question=validation_question,
                model_name=DEFAULT_MODEL,
                temperature=0.2,
                max_tokens=DEFAULT_MAX_TOKENS * 2,
                top_p=DEFAULT_TOP_P
            )
            
            # Düşünce sürecini ve yanıtı logla
            print(f"Validasyon düşünce süreci:\n{validation_result_dict['thinking']}")
            print(f"Validasyon yanıtı:\n{validation_result_dict['answer']}")
            
            # JSON yanıtını çıkar
            import re
            import json
            
            json_match = re.search(r'({.*})', validation_result_dict['answer'], re.DOTALL)
            if json_match:
                try:
                    validation_result = json.loads(json_match.group(1))
                    
                    if validation_result.get("needs_tool", False):
                        print(f"Yanıt validasyonu: Tool gerekiyor - {validation_result.get('reason')}")
                        
                        # Önerilen tool tipine göre özel bir tool oluştur
                        from utils.dynamic_tool_manager import DynamicToolManager
                        
                        tool_type = validation_result.get("suggested_tool_type", "")
                        
                        # AI'a tool bilgilerini oluşturmasını iste
                        prompt = f"""
                        Kullanıcı mesajı: "{user_message}"
                        
                        Önerilen tool tipi: "{tool_type}"
                        
                        Bu kullanıcı mesajı için en uygun tool'u oluştur. Aşağıdaki JSON formatında yanıt ver:
                        
                        {{
                            "new_tool_needed": true,
                            "tool_name": "önerilen_tool_adı",
                            "tool_description": "Tool'un ne yaptığının açıklaması",
                            "tool_parameters": [
                                {{"name": "parametre1", "type": "string/number/boolean", "description": "Parametre açıklaması", "required": true/false}},
                                ...
                            ],
                            "implementation_details": "Tool'un nasıl uygulanacağına dair detaylar"
                        }}
                        
                        Sadece JSON yanıtı ver, başka açıklama yapma.
                        """
                        
                        # AI'dan tool bilgilerini al
                        tool_info_response = AIService.generate_response(
                            prompt=prompt,
                            model_name=DEFAULT_MODEL,
                            temperature=0.2,
                            max_tokens=DEFAULT_MAX_TOKENS,
                            top_p=DEFAULT_TOP_P
                        )
                        
                        # JSON yanıtını çıkar
                        import re
                        import json
                        
                        json_match = re.search(r'({.*})', tool_info_response, re.DOTALL)
                        if json_match:
                            try:
                                tool_info = json.loads(json_match.group(1))
                                print(f"AI tarafından oluşturulan tool bilgileri: {tool_info}")
                            except json.JSONDecodeError:
                                print(f"Tool bilgisi yanıtı JSON formatında değil: {tool_info_response}")
                                # Varsayılan bir tool bilgisi oluştur
                                tool_info = {
                                    "new_tool_needed": True,
                                    "tool_name": "information_retriever",
                                    "tool_description": "Retrieves up-to-date information on various topics",
                                    "tool_parameters": [
                                        {"name": "query", "type": "string", "description": "Search query", "required": True}
                                    ],
                                    "implementation_details": "Use appropriate APIs to fetch current information on the requested topic."
                                }
                        else:
                            print(f"Tool bilgisi yanıtında JSON bulunamadı: {tool_info_response}")
                            # Varsayılan bir tool bilgisi oluştur
                            tool_info = {
                                "new_tool_needed": True,
                                "tool_name": "information_retriever",
                                "tool_description": "Retrieves up-to-date information on various topics",
                                "tool_parameters": [
                                    {"name": "query", "type": "string", "description": "Search query", "required": True}
                                ],
                                "implementation_details": "Use appropriate APIs to fetch current information on the requested topic."
                            }
                        
                        # Tool'u oluştur ve kaydet
                        from utils.dynamic_tool_manager import DynamicToolManager
                        tool_code = DynamicToolManager.generate_tool_code(tool_info)
                        tool = DynamicToolManager.save_and_load_tool(tool_code, tool_info["tool_name"])
                        
                        if tool:
                            # MCP sunucusuna kaydet
                            from mcp_server import get_default_server
                            mcp_server = get_default_server()
                            mcp_server.register_tool(tool)
                            
                            print(f"Validasyon sonucu tool oluşturuldu: {tool.name}")
                            
                            # Tool parametrelerini belirle
                            tool_args = {}
                            
                            # Parametre çıkarımı
                            import re
                            
                            # AI'ın tool parametrelerini belirlemesi
                            prompt = f"""
                            Kullanıcı mesajı: "{user_message}"
                            
                            Tool adı: "{tool.name}"
                            
                            Bu tool için gerekli parametreleri kullanıcı mesajından çıkar.
                            Eğer bir parametre için değer bulamazsan, mantıklı bir varsayılan değer kullan.
                            
                            Yanıtını sadece JSON formatında ver, başka açıklama yapma:
                            {{
                                "parameters": {{
                                    "parametre1": "değer1",
                                    "parametre2": "değer2",
                                    ...
                                }}
                            }}
                            """
                            
                            # AI'dan parametreleri al
                            parameter_response = AIService.generate_response(
                                prompt=prompt,
                                model_name=DEFAULT_MODEL,
                                temperature=0.2,
                                max_tokens=DEFAULT_MAX_TOKENS,
                                top_p=DEFAULT_TOP_P
                            )
                            
                            # JSON yanıtını çıkar
                            import re
                            import json
                            
                            json_match = re.search(r'({.*})', parameter_response, re.DOTALL)
                            if json_match:
                                try:
                                    parameter_result = json.loads(json_match.group(1))
                                    tool_args = parameter_result.get("parameters", {})
                                    print(f"AI tarafından çıkarılan parametreler: {tool_args}")
                                except json.JSONDecodeError:
                                    print(f"Parametre yanıtı JSON formatında değil: {parameter_response}")
                                    tool_args = {}
                            else:
                                print(f"Parametre yanıtında JSON bulunamadı: {parameter_response}")
                                tool_args = {}
                            
                            # Tool'u çalıştır
                            try:
                                tool_result = mcp_server.execute_tool(tool.name, tool_args)
                                print(f"Validasyon sonucu oluşturulan tool çalıştırıldı: {tool.name}, Sonuç: {tool_result}")
                            except Exception as e:
                                # Tool çalıştırma sırasında bir hata oluştu
                                error_message = str(e)
                                print(f"Validasyon sonucu oluşturulan tool çalıştırma sırasında hata: {error_message}")
                                tool_result = {"error": error_message}
                            
                            # Hata kontrolü
                            if "error" in tool_result:
                                error_message = tool_result["error"]
                                print(f"Validasyon sonucu oluşturulan tool çalıştırma hatası: {error_message}")
                                
                                # Otomatik debug ve düzeltme dene
                                print("Tool otomatik debug ve düzeltme deneniyor...")
                                from utils.dynamic_tool_manager import DynamicToolManager
                                debug_success, fixed_tool_name, fixed_tool_info = DynamicToolManager.debug_and_fix_tool(
                                    tool.name,
                                    error_message,
                                    tool_args
                                )
                                
                                if debug_success:
                                    print(f"Tool başarıyla düzeltildi: {fixed_tool_name}")
                                    # Düzeltilen tool'u çalıştır
                                    tool_result = mcp_server.execute_tool(fixed_tool_name, tool_args)
                                    print(f"Düzeltilen tool çalıştırıldı: {fixed_tool_name}, Sonuç: {tool_result}")
                                    # Tool adını güncelle
                                    tool.name = fixed_tool_name
                                    tool_info = fixed_tool_info
                            
                            # Tool sonucuna göre yanıtı güncelle
                            if "error" not in tool_result:
                                # Tool bilgilerini sistem promptuna ekle
                                tool_prompt = f"""
                                Kullanıcının isteği için '{tool.name}' adlı bir araç oluşturuldu ve kullanıldı.
                                Araç açıklaması: {tool_info.get('tool_description', 'Belirtilmemiş')}
                                Araç sonucu: {json.dumps(tool_result, ensure_ascii=False, indent=2)}
                                
                                Bu aracın sonuçlarını kullanarak kullanıcının sorusuna yanıt ver. Aracın nasıl oluşturulduğundan bahsetme, sadece sonuçları kullan.
                                """
                                
                                # Yeni bir prompt oluştur
                                new_system_prompt = f"{system_prompt}\n\n{tool_prompt}"
                                
                                new_full_prompt = f"""{new_system_prompt}
                                
                                Sohbet geçmişi:
                                {history_text}
                                
                                Kullanıcı: {user_message}
                                Asistan:"""
                                
                                # Yeni yanıt al
                                new_response_text = AIService.generate_response(
                                    prompt=new_full_prompt,
                                    model_name=DEFAULT_MODEL,
                                    temperature=DEFAULT_TEMPERATURE,
                                    max_tokens=DEFAULT_CHAT_TOKENS,
                                    top_p=DEFAULT_TOP_P
                                )
                                
                                # Yanıtı güncelle
                                response_text = new_response_text
                                print(f"Yanıt validasyon sonucu güncellendi")
                except json.JSONDecodeError:
                    print(f"Validasyon yanıtı JSON formatında değil: {validation_response}")
        
        # Asistan yanıtını veritabanına ekle
        assistant_message_id = SessionService.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            parent_message_id=user_message_id,
            model_used=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            processing_time_ms=processing_time_ms
        )
        
        return response_text
    except Exception as e:
        error_msg = f"Yanıt alınırken bir hata oluştu: {str(e)}"
        print(error_msg)
        return error_msg

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

# Oturum listesini getir
def get_session_list():
    try:
        sessions = SessionService.get_all_sessions(active_only=True)
        return [session["session_name"] for session in sessions]
    except Exception as e:
        print(f"Oturum listesi alınırken hata oluştu: {str(e)}")
        return []

# Oturum oluşturma fonksiyonu
def create_session(name, system_prompt, wiki_info, use_agentic):
    try:
        if not name:
            return "Lütfen oturum adını doldurun.", None
        
        try:
            # SessionService kullanarak oturumu oluştur
            session_id = SessionService.create_session(
                system_prompt=system_prompt,
                wiki_info=wiki_info,
                use_agentic=use_agentic,
                session_name=name
            )
            
            return f"{name} oturumu başarıyla oluşturuldu!", session_id
        except Exception as e:
            error_msg = f"Oturum oluşturulurken hata oluştu: {str(e)}"
            print(error_msg)
            return error_msg, None
    except Exception as e:
        error_msg = f"Oturum oluşturulurken beklenmeyen hata: {str(e)}"
        print(error_msg)
        return error_msg, None

# Wikipedia'dan bilgi çekme fonksiyonu
def fetch_wiki_info(query):
    try:
        if not query:
            return "Lütfen arama terimini girin."
        
        try:
            # WikiService kullanarak bilgi çek
            wiki_info = WikiService.fetch_info(query)
            return wiki_info
        except Exception as e:
            error_msg = f"Wikipedia'dan bilgi çekilirken hata oluştu: {str(e)}"
            print(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Wikipedia işlemi sırasında beklenmeyen hata: {str(e)}"
        print(error_msg)
        return error_msg

# Sohbet fonksiyonu
def chat_with_session(message, history, session_id):
    # Debug bilgisi yazdır
    print(f"chat_with_session fonksiyonu çağrıldı. Oturum ID: '{session_id}'")
    
    if not session_id:
        print("Oturum ID boş, hata mesajı döndürülüyor")
        return "Lütfen önce bir oturum seçin."
    
    try:
        # Oturum bilgilerini yükle
        session = SessionService.get_session(session_id)
        if not session:
            print(f"Oturum bulunamadı: '{session_id}'")
            return "Oturum bulunamadı. Lütfen başka bir oturum seçin."
        
        # Oturum bilgilerini dict olarak kullan
        session_dict = session  # SessionService.get_session zaten dict döndürüyor
        
        # Agentic özelliği kontrol et
        use_agentic = session_dict.get("use_agentic", False)
        print(f"Oturum '{session_id}' için agentic modu: {use_agentic}")
        
        try:
            # Yanıtı al
            response = get_response(session_id, message, use_agentic)
            return response
        except Exception as e:
            error_msg = f"Yanıt alınırken hata oluştu: {str(e)}"
            print(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Sohbet işlemi sırasında hata oluştu: {str(e)}"
        print(error_msg)
        return error_msg

# Sohbet geçmişini temizleme fonksiyonu
def clear_chat_history(session_id):
    try:
        if not session_id:
            return "Lütfen önce bir oturum seçin."
        
        try:
            # Oturum mesajlarını temizle
            success = SessionService.clear_session_messages(session_id)
            
            if success:
                return f"Oturum sohbet geçmişi temizlendi."
            else:
                return "Sohbet geçmişi temizlenirken bir hata oluştu."
        except Exception as e:
            error_msg = f"Sohbet geçmişi temizlenirken hata oluştu: {str(e)}"
            print(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Sohbet geçmişi temizlenirken beklenmeyen hata: {str(e)}"
        print(error_msg)
        return error_msg

# Araçları listeleme fonksiyonu
def list_tools():
    try:
        mcp_server = get_default_server()
        
        try:
            tools_info = mcp_server.get_tools_info()
            
            # Yerleşik araçlar ve dinamik araçları ayır
            built_in_tools = []
            dynamic_tools = []
            
            try:
                for tool in tools_info:
                    if tool['name'] in ['search_wikipedia', 'get_current_time', 'get_weather', 'open_website', 'calculate_math']:
                        built_in_tools.append(tool)
                    else:
                        dynamic_tools.append(tool)
                
                return built_in_tools, dynamic_tools
            except Exception as e:
                error_msg = f"Araçlar ayrılırken hata oluştu: {str(e)}"
                print(error_msg)
                return [], []
        except Exception as e:
            error_msg = f"Araç bilgileri alınırken hata oluştu: {str(e)}"
            print(error_msg)
            return [], []
    except Exception as e:
        error_msg = f"MCP sunucusu alınırken hata oluştu: {str(e)}"
        print(error_msg)
        return [], []

# Oturum bilgilerini getirme fonksiyonu
def get_session_info(session_name):
    if not session_name:
        return None, None, None, None
    
    try:
        # Oturum adından ID'yi bul
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE session_name = ?", (session_name,))
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return None, None, None, None
        
        # sqlite3.Row nesnesini dict'e dönüştür
        session_dict = dict(session)
        
        return (
            session_dict["session_id"],
            session_dict.get("system_prompt", ""),
            session_dict.get("wiki_info", ""),
            bool(session_dict.get("use_agentic", 0))
        )
    except Exception as e:
        print(f"Oturum bilgileri alınırken hata: {str(e)}")
        return None, None, None, None

# Gradio arayüzünü oluştur
def create_gradio_interface():
    with gr.Blocks(title=APPLICATION_TITLE, theme=gr.themes.Soft()) as app:
        gr.Markdown(f"# {APPLICATION_ICON} {APPLICATION_TITLE}")
        gr.Markdown(APPLICATION_DESCRIPTION)
        
        # Durum değişkenleri
        current_session_id = gr.State(None)
        wiki_info_state = gr.State(None)
        
        with gr.Tabs() as tabs:
            # Sohbet sekmesi
            with gr.Tab("Sohbet"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # Oturum seçimi - Dropdown yerine Radio kullanarak liste görünümü sağlıyoruz
                        session_dropdown = gr.Radio(
                            choices=get_session_list(),
                            label="Oturum Seçin",
                            interactive=True,
                            type="value"
                        )
                        
                        refresh_btn = gr.Button("Oturum Listesini Yenile")
                        
                        # Oturum bilgileri
                        with gr.Accordion("Oturum Bilgileri", open=False):
                            session_system_prompt = gr.Textbox(label="Sistem Promptu", lines=3, interactive=False)
                            session_wiki = gr.Textbox(label="Wikipedia Bilgisi", lines=3, interactive=False)
                            session_agentic = gr.Checkbox(label="Agentic Özellikler", interactive=False)
                        
                        # Araçlar bilgi paneli
                        with gr.Accordion("🛠️ Kullanılabilir Araçlar", open=False):
                            built_in_tools_md = gr.Markdown("### Yerleşik Araçlar")
                            dynamic_tools_md = gr.Markdown("### Dinamik Oluşturulan Araçlar")
                            
                            # Araçları yenileme butonu
                            refresh_tools_btn = gr.Button("Araçları Yenile")
                        
                        # Sohbeti temizleme butonu
                        clear_chat_btn = gr.Button("🗑️ Sohbeti Temizle")
                    
                    with gr.Column(scale=2):
                        # Sohbet arayüzü
                        chatbot = gr.Chatbot(
                            label="Sohbet",
                            height=500,
                            type="messages"
                        )
                        
                        # Mesaj giriş alanı
                        msg = gr.Textbox(
                            label="Mesajınızı yazın",
                            placeholder="Mesajınızı buraya yazın...",
                            lines=2
                        )
                        
                        # Gönder butonu
                        send_btn = gr.Button("Gönder")
            
            # Oturum Oluşturma sekmesi
            with gr.Tab("Oturum Oluştur"):
                with gr.Row():
                    with gr.Column():
                        # Oturum oluşturma formu
                        new_session_name = gr.Textbox(label="Oturum Adı", placeholder="örn. Proje Planlaması, Kod Yardımı, vb.")
                        
                        # Wikipedia bilgisi çekme
                        with gr.Row():
                            wiki_checkbox = gr.Checkbox(label="Wikipedia'dan bilgi çek", value=True)
                            wiki_fetch_btn = gr.Button("Wikipedia'dan Bilgi Çek")
                        
                        wiki_query = gr.Textbox(label="Wikipedia Arama Terimi", placeholder="örn. Yapay Zeka, Python, vb.")
                        wiki_info_box = gr.Textbox(label="Wikipedia Bilgisi", lines=5, interactive=True)
                        
                        new_system_prompt = gr.Textbox(
                            label="Sistem Promptu", 
                            placeholder="Asistanın nasıl davranması gerektiğini belirten talimatları yazın...",
                            lines=5,
                            value="Sen yardımcı bir yapay zeka asistanısın. Kullanıcının sorularına doğru ve yararlı yanıtlar ver."
                        )
                        
                        new_session_agentic = gr.Checkbox(
                            label="Agentic Özellikleri Etkinleştir", 
                            value=True,
                            info="Asistanın eylemler gerçekleştirmesine ve araçlar kullanmasına izin verir"
                        )
                        
                        create_btn = gr.Button("Oturumu Oluştur")
                        
                        # Sonuç mesajı
                        create_result = gr.Textbox(label="Sonuç", interactive=False)
        
        # Fonksiyon bağlantıları
        
        # Oturum seçimi değiştiğinde
        def on_session_select(session_name):
            if not session_name:
                return None, "", "", False, []
            
            # Debug bilgisi yazdır
            print(f"Oturum seçildi: '{session_name}'")
            
            try:
                session_id, system_prompt, wiki_info, agentic = get_session_info(session_name)
                
                if not session_id:
                    print(f"Oturum bilgileri yüklenemedi: '{session_name}'")
                    return None, "", "", False, []
                
                # Sohbet geçmişini yükle
                chat_history = []
                try:
                    messages = SessionService.get_messages(session_id)
                    
                    # Mesajları doğru sırayla işle (user ve assistant mesajlarını eşleştir)
                    user_messages = [msg for msg in messages if msg["message_role"] == "user"]
                    assistant_messages = [msg for msg in messages if msg["message_role"] == "assistant"]
                    
                    # Eşleşen mesajları ekle
                    for i in range(min(len(user_messages), len(assistant_messages))):
                        chat_history.append({"role": "user", "content": user_messages[i]["message_content"]})
                        chat_history.append({"role": "assistant", "content": assistant_messages[i]["message_content"]})
                    
                    # Eğer son mesaj kullanıcıdan gelip cevapsız kaldıysa onu da ekle
                    if len(user_messages) > len(assistant_messages):
                        chat_history.append({"role": "user", "content": user_messages[-1]["message_content"]})
                        
                except Exception as e:
                    print(f"Sohbet geçmişi yüklenirken hata: {str(e)}")
                
                print(f"Oturum seçimi tamamlandı, current_session_id değeri: '{session_id}'")
                return session_id, system_prompt, wiki_info, agentic, chat_history
            except Exception as e:
                print(f"Oturum seçilirken hata: {str(e)}")
                return None, "", "", False, []
        
        session_dropdown.change(
            on_session_select,
            inputs=[session_dropdown],
            outputs=[current_session_id, session_system_prompt, session_wiki, session_agentic, chatbot]
        )
        
        # Oturum listesini yenileme
        refresh_btn.click(
            lambda: gr.update(choices=get_session_list()),
            outputs=[session_dropdown]
        )
        
        # Araçları yenileme
        def update_tools_display():
            try:
                built_in, dynamic = list_tools()
                
                built_in_md = "### Yerleşik Araçlar\n"
                try:
                    for tool in built_in:
                        built_in_md += f"**{tool['name']}**: {tool['description']}\n\n"
                except Exception as e:
                    print(f"Yerleşik araçlar listelenirken hata: {str(e)}")
                    built_in_md += "Araçlar listelenirken bir hata oluştu.\n"
                
                dynamic_md = "### Dinamik Oluşturulan Araçlar\n"
                try:
                    if dynamic:
                        for tool in dynamic:
                            dynamic_md += f"**{tool['name']}**: {tool['description']}\n\n"
                        dynamic_md += "Dinamik araçlar, kullanıcı ihtiyaçlarına göre otomatik olarak oluşturulur."
                    else:
                        dynamic_md += "Henüz dinamik araç oluşturulmamış."
                except Exception as e:
                    print(f"Dinamik araçlar listelenirken hata: {str(e)}")
                    dynamic_md += "Araçlar listelenirken bir hata oluştu.\n"
                
                return built_in_md, dynamic_md
            except Exception as e:
                error_msg = f"Araçlar listelenirken hata oluştu: {str(e)}"
                print(error_msg)
                return "### Yerleşik Araçlar\nAraçlar listelenirken bir hata oluştu.", "### Dinamik Oluşturulan Araçlar\nAraçlar listelenirken bir hata oluştu."
        
        refresh_tools_btn.click(
            update_tools_display,
            outputs=[built_in_tools_md, dynamic_tools_md]
        )
        
        # Sohbeti temizleme
        clear_chat_btn.click(
            lambda session_id: (clear_chat_history(session_id), []),
            inputs=[current_session_id],
            outputs=[create_result, chatbot]
        )
        
        # Mesaj gönderme
        def on_message_send(message, history, session_id):
            try:
                if not message.strip():
                    return history, ""
                
                # Oturum ID'sini kontrol et
                if not session_id:
                    # Kullanıcıya daha açıklayıcı bir mesaj göster
                    error_msg = "Lütfen önce soldaki listeden bir oturum seçin veya 'Oturum Oluştur' sekmesinden yeni bir oturum oluşturun."
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": error_msg})
                    return history, ""
                
                try:
                    # Oturum bilgilerini kontrol et
                    session = SessionService.get_session(session_id)
                    if not session:
                        error_msg = f"Seçilen oturum artık mevcut değil. Lütfen başka bir oturum seçin."
                        history.append({"role": "user", "content": message})
                        history.append({"role": "assistant", "content": error_msg})
                        return history, ""
                    
                    # Asistanın cevabını al
                    response = chat_with_session(message, history, session_id)
                    
                    # Sohbet geçmişine ekle
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": response})
                    
                    return history, ""
                except Exception as e:
                    error_msg = f"Mesaj işlenirken hata oluştu: {str(e)}"
                    print(error_msg)
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": error_msg})
                    return history, ""
            except Exception as e:
                error_msg = f"Beklenmeyen hata: {str(e)}"
                print(error_msg)
                try:
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": error_msg})
                except:
                    history = [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": error_msg}
                    ]
                return history, ""
        
        send_btn.click(
            on_message_send,
            inputs=[msg, chatbot, current_session_id],
            outputs=[chatbot, msg],
            show_progress=True
        )
        
        msg.submit(
            on_message_send,
            inputs=[msg, chatbot, current_session_id],
            outputs=[chatbot, msg],
            show_progress=True
        )
        
        # Wikipedia'dan bilgi çekme
        wiki_fetch_btn.click(
            lambda query: fetch_wiki_info(query),
            inputs=[wiki_query],
            outputs=[wiki_info_box]
        )
        
        # Oturum oluşturma
        def on_create_session(name, system_prompt, wiki_info, use_agentic):
            try:
                result, session_id = create_session(name, system_prompt, wiki_info, use_agentic)
                
                # Oturum listesini güncelle
                try:
                    updated_dropdown = gr.update(choices=get_session_list(), value=name if session_id else None)
                    return result, updated_dropdown
                except Exception as e:
                    error_msg = f"Oturum listesi güncellenirken hata oluştu: {str(e)}"
                    print(error_msg)
                    return f"{result}\n{error_msg}", gr.update()
            except Exception as e:
                error_msg = f"Oturum oluşturulurken hata oluştu: {str(e)}"
                print(error_msg)
                return error_msg, gr.update()
        
        create_btn.click(
            on_create_session,
            inputs=[new_session_name, new_system_prompt, wiki_info_box, new_session_agentic],
            outputs=[create_result, session_dropdown]
        )
        
        # Sayfa yüklendiğinde araçları göster
        app.load(
            update_tools_display,
            outputs=[built_in_tools_md, dynamic_tools_md]
        )
        
    return app

# Ana fonksiyon
def main():
    app = create_gradio_interface()
    app.launch(share=False)

if __name__ == "__main__":
    main()
