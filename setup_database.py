"""
SQLite veritabanını oluşturmak ve tabloları yapılandırmak için script.
"""
import sqlite3
from pathlib import Path
from utils.config import DB_PATH

def setup_database():
    """
    SQLite veritabanını oluştur ve tabloları yapılandır.
    """
    print(f"Veritabanı oluşturuluyor: {DB_PATH}")
    
    # Veritabanı bağlantısı oluştur
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabloları oluştur
    
    # Users tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        user_fingerprint TEXT UNIQUE, -- Browser fingerprint for anonymous tracking
        preferred_language TEXT DEFAULT 'tr',
        timezone TEXT DEFAULT 'Europe/Istanbul',
        user_preferences JSON DEFAULT '{}',
        first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_sessions INTEGER DEFAULT 0,
        total_messages INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sessions tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        session_name TEXT,
        use_agentic BOOLEAN DEFAULT 0,
        system_prompt TEXT,
        wiki_info TEXT,
        conversation_context JSON DEFAULT '{}',
        session_metadata JSON DEFAULT '{}',
        message_count INTEGER DEFAULT 0,
        tool_usage_count INTEGER DEFAULT 0,
        last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_duration_seconds INTEGER DEFAULT 0,
        session_status TEXT DEFAULT 'active' CHECK (session_status IN ('active', 'paused', 'completed', 'expired')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    )
    ''')
    
    # Messages tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        session_id TEXT NOT NULL,
        parent_message_id TEXT, -- For conversation threading
        message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
        message_content TEXT NOT NULL,
        message_metadata JSON DEFAULT '{}',
        tool_calls JSON DEFAULT '[]', -- Array of tool calls made
        processing_time_ms INTEGER,
        token_count INTEGER,
        model_used TEXT,
        temperature REAL,
        message_index INTEGER, -- Order within session
        is_hidden BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
        FOREIGN KEY (parent_message_id) REFERENCES messages(message_id) ON DELETE SET NULL
    )
    ''')
    
    # Tools tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tools (
        tool_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        tool_name TEXT UNIQUE NOT NULL,
        tool_type TEXT NOT NULL CHECK (tool_type IN ('builtin', 'dynamic', 'external')),
        tool_category TEXT,
        tool_description TEXT NOT NULL,
        tool_parameters JSON DEFAULT '{}',
        tool_source_code TEXT, -- For dynamic tools
        implementation_details TEXT,
        version TEXT DEFAULT '1.0.0',
        is_active BOOLEAN DEFAULT 1,
        is_deleted BOOLEAN DEFAULT 0,
        creation_method TEXT, -- 'manual', 'ai_generated', 'user_requested'
        creator_session_id TEXT,
        usage_count INTEGER DEFAULT 0,
        success_rate REAL DEFAULT 0.0,
        average_execution_time_ms REAL DEFAULT 0.0,
        last_used_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        deleted_at TIMESTAMP,
        FOREIGN KEY (creator_session_id) REFERENCES sessions(session_id) ON DELETE SET NULL
    )
    ''')
    
    # Tool executions tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tool_executions (
        execution_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        tool_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        message_id TEXT,
        execution_args JSON DEFAULT '{}',
        execution_result JSON DEFAULT '{}',
        execution_status TEXT DEFAULT 'pending' CHECK (execution_status IN ('pending', 'running', 'success', 'error', 'timeout')),
        execution_time_ms INTEGER,
        error_message TEXT,
        execution_metadata JSON DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
        FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE SET NULL
    )
    ''')
    
    # Tool dependencies tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tool_dependencies (
        dependency_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        tool_id TEXT NOT NULL,
        depends_on_tool_id TEXT NOT NULL,
        dependency_type TEXT DEFAULT 'required' CHECK (dependency_type IN ('required', 'optional', 'suggested')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
        FOREIGN KEY (depends_on_tool_id) REFERENCES tools(tool_id) ON DELETE CASCADE,
        UNIQUE(tool_id, depends_on_tool_id)
    )
    ''')
    
    # Conversation topics tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation_topics (
        topic_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        session_id TEXT NOT NULL,
        topic_name TEXT NOT NULL,
        topic_category TEXT,
        confidence_score REAL DEFAULT 0.0,
        topic_metadata JSON DEFAULT '{}',
        first_mentioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_mentioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mention_count INTEGER DEFAULT 1,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
    )
    ''')
    
    # User intents tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_intents (
        intent_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        session_id TEXT NOT NULL,
        message_id TEXT NOT NULL,
        intent_type TEXT NOT NULL,
        intent_confidence REAL DEFAULT 0.0,
        intent_parameters JSON DEFAULT '{}',
        tool_suggested TEXT, -- Tool that could fulfill this intent
        was_fulfilled BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
        FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
        FOREIGN KEY (tool_suggested) REFERENCES tools(tool_name) ON DELETE SET NULL
    )
    ''')
    
    # Performance metrics tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_metrics (
        metric_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        metric_type TEXT NOT NULL,
        metric_name TEXT NOT NULL,
        metric_value REAL NOT NULL,
        metric_unit TEXT,
        metric_metadata JSON DEFAULT '{}',
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE SET NULL
    )
    ''')
    
    # Usage analytics tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage_analytics (
        analytics_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        date_period DATE NOT NULL,
        period_type TEXT DEFAULT 'daily' CHECK (period_type IN ('hourly', 'daily', 'weekly', 'monthly')),
        total_sessions INTEGER DEFAULT 0,
        total_messages INTEGER DEFAULT 0,
        total_tool_calls INTEGER DEFAULT 0,
        active_users INTEGER DEFAULT 0,
        average_session_duration REAL DEFAULT 0.0,
        popular_tools JSON DEFAULT '[]',
        performance_summary JSON DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date_period, period_type)
    )
    ''')
    
    # Response cache tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS response_cache (
        cache_key TEXT PRIMARY KEY,
        cache_value TEXT NOT NULL,
        cache_metadata JSON DEFAULT '{}',
        cache_type TEXT DEFAULT 'api_response',
        expires_at TIMESTAMP,
        hit_count INTEGER DEFAULT 0,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Embeddings cache tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings_cache (
        embedding_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        content_hash TEXT UNIQUE NOT NULL,
        content_text TEXT NOT NULL,
        embedding_vector TEXT NOT NULL, -- JSON array of floats
        embedding_model TEXT NOT NULL,
        embedding_dimensions INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # System config tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_config (
        config_key TEXT PRIMARY KEY,
        config_value TEXT NOT NULL,
        config_type TEXT DEFAULT 'string' CHECK (config_type IN ('string', 'integer', 'float', 'boolean', 'json')),
        config_description TEXT,
        is_sensitive BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # External services tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS external_services (
        service_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        service_name TEXT UNIQUE NOT NULL,
        service_type TEXT NOT NULL,
        service_url TEXT,
        api_key_encrypted TEXT, -- Should be encrypted
        service_config JSON DEFAULT '{}',
        is_active BOOLEAN DEFAULT 1,
        rate_limit INTEGER DEFAULT 100,
        rate_limit_window TEXT DEFAULT '1h',
        last_status_check TIMESTAMP,
        status TEXT DEFAULT 'unknown' CHECK (status IN ('active', 'inactive', 'error', 'unknown')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Schema migrations tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version TEXT PRIMARY KEY,
        description TEXT,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # İndeksleri oluştur
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(session_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(message_role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_message_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_index ON messages(session_id, message_index)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(tool_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_type ON tools(tool_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_active ON tools(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(tool_category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_usage ON tools(usage_count DESC)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_executions_tool_id ON tool_executions(tool_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_executions_session_id ON tool_executions(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_executions_status ON tool_executions(execution_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_executions_created_at ON tool_executions(created_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_recorded_at ON performance_metrics(recorded_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_cache_expires ON response_cache(expires_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_cache_type ON response_cache(cache_type)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_embeddings_hash ON embeddings_cache(content_hash)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_fingerprint ON users(user_fingerprint)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen_at)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_period ON usage_analytics(date_period, period_type)')
    
    # View'ları oluştur
    
    # Aktif oturumlar view'ı
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_active_sessions AS
    SELECT
        s.*,
        u.user_fingerprint,
        u.preferred_language,
        COUNT(m.message_id) as message_count_calc,
        MAX(m.created_at) as last_message_at
    FROM sessions s
    LEFT JOIN users u ON s.user_id = u.user_id
    LEFT JOIN messages m ON s.session_id = m.session_id
    WHERE s.session_status = 'active'
    GROUP BY s.session_id
    ''')
    
    # Araç performansı view'ı
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_tool_performance AS
    SELECT
        t.tool_id,
        t.tool_name,
        t.tool_type,
        t.tool_category,
        t.usage_count,
        COUNT(te.execution_id) as total_executions,
        COUNT(CASE WHEN te.execution_status = 'success' THEN 1 END) as successful_executions,
        ROUND(
            CAST(COUNT(CASE WHEN te.execution_status = 'success' THEN 1 END) AS FLOAT) /
            NULLIF(COUNT(te.execution_id), 0) * 100, 2
        ) as success_rate_percent,
        AVG(te.execution_time_ms) as avg_execution_time_ms,
        MIN(te.execution_time_ms) as min_execution_time_ms,
        MAX(te.execution_time_ms) as max_execution_time_ms
    FROM tools t
    LEFT JOIN tool_executions te ON t.tool_id = te.tool_id
    WHERE t.is_active = 1 AND t.is_deleted = 0
    GROUP BY t.tool_id, t.tool_name, t.tool_type, t.tool_category, t.usage_count
    ''')
    
    # Günlük istatistikler view'ı
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_daily_stats AS
    SELECT
        DATE(created_at) as date,
        COUNT(DISTINCT session_id) as sessions,
        COUNT(*) as messages,
        COUNT(DISTINCT CASE WHEN tool_calls != '[]' THEN session_id END) as sessions_with_tools,
        AVG(token_count) as avg_tokens_per_message,
        AVG(processing_time_ms) as avg_processing_time_ms
    FROM messages
    WHERE created_at >= DATE('now', '-30 days')
    GROUP BY DATE(created_at)
    ORDER BY date DESC
    ''')
    
    # Değişiklikleri kaydet
    conn.commit()
    
    # İlk şema versiyonunu kaydet
    cursor.execute('''
    INSERT INTO schema_migrations (version, description)
    VALUES ('1.0.0', 'Initial schema creation')
    ''')
    
    conn.commit()
    conn.close()
    
    print("Veritabanı başarıyla oluşturuldu ve yapılandırıldı.")

if __name__ == "__main__":
    setup_database()