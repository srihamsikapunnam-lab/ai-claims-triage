import sqlite3
import os
from datetime import datetime

class DocumentStorage:
    def __init__(self, db_path="documents.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the documents database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                document_name TEXT NOT NULL,
                document_type TEXT DEFAULT 'general',
                file_path TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                mime_type TEXT DEFAULT 'application/octet-stream',
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_processed BOOLEAN DEFAULT FALSE,
                extracted_text TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_result TEXT,
                confidence_score REAL DEFAULT 0.0,
                flags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_document(self, claim_id, user_id, document_name, file_path, **kwargs):
        """Store a document in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get file info
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        cursor.execute('''
            INSERT INTO documents 
            (claim_id, user_id, document_name, document_type, file_path, 
             file_size, mime_type, is_processed, extracted_text, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            claim_id,
            user_id,
            document_name,
            kwargs.get('document_type', 'general'),
            file_path,
            file_size,
            kwargs.get('mime_type', 'application/octet-stream'),
            kwargs.get('is_processed', False),
            kwargs.get('extracted_text', ''),
            kwargs.get('metadata', '')
        ))
        
        document_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return document_id
    
    def get_documents_by_claim(self, claim_id):
        """Get all documents for a specific claim"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM documents 
            WHERE claim_id = ? 
            ORDER BY upload_date DESC
        ''', (claim_id,))
        
        documents = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return documents
    
    def get_documents_by_user(self, user_id):
        """Get all documents for a specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, COUNT(da.id) as analysis_count
            FROM documents d
            LEFT JOIN document_analysis da ON d.id = da.document_id
            WHERE d.user_id = ?
            GROUP BY d.id
            ORDER BY d.upload_date DESC
        ''', (user_id,))
        
        documents = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return documents
    
    def add_document_analysis(self, document_id, analysis_type, analysis_result, confidence_score=0.0, flags=""):
        """Add analysis results for a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO document_analysis 
            (document_id, analysis_type, analysis_result, confidence_score, flags)
            VALUES (?, ?, ?, ?, ?)
        ''', (document_id, analysis_type, analysis_result, confidence_score, flags))
        
        # Update document as processed
        cursor.execute('''
            UPDATE documents 
            SET is_processed = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (document_id,))
        
        conn.commit()
        conn.close()
    
    def get_document_analysis(self, document_id):
        """Get analysis results for a document"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM document_analysis 
            WHERE document_id = ? 
            ORDER BY created_at DESC
        ''', (document_id,))
        
        analysis = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return analysis
    
    def delete_document(self, document_id):
        """Delete a document and its analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get file path to delete physical file
        cursor.execute('SELECT file_path FROM documents WHERE id = ?', (document_id,))
        result = cursor.fetchone()
        
        if result:
            file_path = result[0]
            # Delete physical file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete analysis records
        cursor.execute('DELETE FROM document_analysis WHERE document_id = ?', (document_id,))
        
        # Delete document record
        cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        
        conn.commit()
        conn.close()
    
    def get_storage_stats(self):
        """Get storage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_documents,
                SUM(file_size) as total_size,
                COUNT(CASE WHEN is_processed = TRUE THEN 1 END) as processed_documents,
                COUNT(DISTINCT claim_id) as unique_claims,
                COUNT(DISTINCT user_id) as unique_users
            FROM documents
        ''')
        
        stats = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        conn.close()
        
        return stats

# Initialize the document storage system
document_storage = DocumentStorage()