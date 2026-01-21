#!/usr/bin/env python3
"""Enhanced API server with proper file upload support"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import os
import io
from urllib.parse import urlparse
from datetime import datetime
import mimetypes
import re

class MultipartParser:
    """Simple multipart/form-data parser"""
    def __init__(self, body, boundary):
        self.body = body
        self.boundary = boundary.encode() if isinstance(boundary, str) else boundary
        
    def parse(self):
        parts = {}
        sections = self.body.split(b'--' + self.boundary)
        
        for section in sections[1:-1]:  # Skip first and last empty parts
            if not section.strip():
                continue
                
            # Split headers and content
            try:
                header_end = section.find(b'\r\n\r\n')
                if header_end == -1:
                    continue
                    
                headers = section[:header_end].decode('utf-8', errors='ignore')
                content = section[header_end + 4:]
                
                # Remove trailing \r\n
                if content.endswith(b'\r\n'):
                    content = content[:-2]
                
                # Parse Content-Disposition
                name_match = re.search(r'name="([^"]+)"', headers)
                filename_match = re.search(r'filename="([^"]+)"', headers)
                
                if name_match:
                    field_name = name_match.group(1)
                    
                    if filename_match:
                        # File upload
                        filename = filename_match.group(1)
                        parts[field_name] = {
                            'filename': filename,
                            'content': content
                        }
                    else:
                        # Regular field
                        parts[field_name] = content.decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Error parsing section: {e}")
                continue
        
        return parts

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/v1/notices/':
            self.handle_get_notices()
        elif path.startswith('/api/v1/notices/') and path.count('/') == 4:
            notice_id = path.split('/')[-1]
            self.handle_get_notice(notice_id)
        elif path == '/api/v1/purchase-orders/':
            self.handle_get_purchase_orders()
        elif path.startswith('/api/v1/purchase-orders/') and path.count('/') == 4:
            po_id = path.split('/')[-1]
            self.handle_get_purchase_order(po_id)
        elif path.startswith('/uploads/'):
            self.handle_static_file(path)
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        if path == '/api/v1/notices/':
            self.handle_create_notice(body)
        elif path == '/api/v1/purchase-orders/':
            self.handle_create_purchase_order(body)
        elif path == '/api/v1/notices/upload-image/':
            self.handle_upload_image('notices', body)
        elif path == '/api/v1/purchase-orders/upload-image/':
            self.handle_upload_image('purchase_orders', body)
        else:
            self.send_error(404)
    
    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        if path.startswith('/api/v1/notices/') and path.count('/') == 4:
            notice_id = path.split('/')[-1]
            self.handle_update_notice(notice_id, body)
        elif path.startswith('/api/v1/purchase-orders/') and path.count('/') == 4:
            po_id = path.split('/')[-1]
            self.handle_update_purchase_order(po_id, body)
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/v1/notices/') and path.count('/') == 4:
            notice_id = path.split('/')[-1]
            self.handle_delete_notice(notice_id)
        elif path.startswith('/api/v1/purchase-orders/') and path.count('/') == 4:
            po_id = path.split('/')[-1]
            self.handle_delete_purchase_order(po_id)
        else:
            self.send_error(404)
    
    def handle_get_notices(self):
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notices WHERE is_active = 1 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        items = [dict(row) for row in rows]
        conn.close()
        
        self.send_json_response({'total': len(items), 'items': items})
    
    def handle_get_notice(self, notice_id):
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("UPDATE notices SET views = views + 1 WHERE id = ?", (notice_id,))
        cursor.execute("SELECT * FROM notices WHERE id = ?", (notice_id,))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if row:
            self.send_json_response(dict(row))
        else:
            self.send_error(404)
    
    def handle_create_notice(self, body):
        data = json.loads(body)
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notices (title, content, author, image_url, is_important, views, is_active)
            VALUES (?, ?, ?, ?, ?, 0, 1)
        """, (data['title'], data['content'], data['author'], 
              data.get('image_url', ''), data.get('is_important', False)))
        conn.commit()
        notice_id = cursor.lastrowid
        conn.close()
        
        self.send_json_response({'id': notice_id, **data}, 201)
    
    def handle_update_notice(self, notice_id, body):
        data = json.loads(body)
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key in ['title', 'content', 'author', 'image_url', 'is_important', 'is_active']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if fields:
            values.append(notice_id)
            cursor.execute(f"UPDATE notices SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        
        conn.close()
        self.send_json_response({'message': 'Updated successfully'})
    
    def handle_delete_notice(self, notice_id):
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE notices SET is_active = 0 WHERE id = ?", (notice_id,))
        conn.commit()
        conn.close()
        
        self.send_json_response({'message': '공지사항이 삭제되었습니다'})
    
    def handle_get_purchase_orders(self):
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM purchase_orders WHERE is_active = 1 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        items = [dict(row) for row in rows]
        conn.close()
        
        self.send_json_response({'total': len(items), 'items': items})
    
    def handle_get_purchase_order(self, po_id):
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM purchase_orders WHERE id = ?", (po_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            self.send_json_response(dict(row))
        else:
            self.send_error(404)
    
    def handle_create_purchase_order(self, body):
        data = json.loads(body)
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO purchase_orders (po_number, title, supplier, order_date, delivery_date,
                                        total_amount, status, content, image_url, author, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (data['po_number'], data['title'], data['supplier'], data['order_date'],
              data.get('delivery_date', ''), data.get('total_amount', 0), data.get('status', '작성중'),
              data.get('content', ''), data.get('image_url', ''), data['author']))
        conn.commit()
        po_id = cursor.lastrowid
        conn.close()
        
        self.send_json_response({'id': po_id, **data}, 201)
    
    def handle_update_purchase_order(self, po_id, body):
        data = json.loads(body)
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key in ['po_number', 'title', 'supplier', 'order_date', 'delivery_date',
                    'total_amount', 'status', 'content', 'image_url', 'author', 'is_active']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if fields:
            values.append(po_id)
            cursor.execute(f"UPDATE purchase_orders SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        
        conn.close()
        self.send_json_response({'message': 'Updated successfully'})
    
    def handle_delete_purchase_order(self, po_id):
        conn = sqlite3.connect('/home/user/webapp/backend/dispatch.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE purchase_orders SET is_active = 0 WHERE id = ?", (po_id,))
        conn.commit()
        conn.close()
        
        self.send_json_response({'message': '발주서가 삭제되었습니다'})
    
    def handle_upload_image(self, module, body):
        """Handle multipart file upload"""
        try:
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_json_response({'error': 'Must be multipart/form-data'}, 400)
                return
            
            # Extract boundary
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if not boundary_match:
                self.send_json_response({'error': 'No boundary found'}, 400)
                return
            
            boundary = boundary_match.group(1).strip('"')
            
            # Parse multipart data
            parser = MultipartParser(body, boundary)
            parts = parser.parse()
            
            if 'file' not in parts:
                self.send_json_response({'error': 'No file uploaded'}, 400)
                return
            
            file_data = parts['file']
            filename = file_data['filename']
            content = file_data['content']
            
            # Validate file type
            if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                self.send_json_response({'error': '이미지 파일만 업로드 가능합니다'}, 400)
                return
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(filename)[1]
            new_filename = f"{timestamp}_{filename}"
            
            # Save file
            upload_dir = f"/home/user/webapp/backend/uploads/{module}"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, new_filename)
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Return URL
            image_url = f"/uploads/{module}/{new_filename}"
            print(f"✅ Image uploaded: {image_url}")
            self.send_json_response({'image_url': image_url})
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_static_file(self, path):
        file_path = f"/home/user/webapp/backend{path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            self.send_response(200)
            self.send_header('Content-Type', mime_type or 'application/octet-stream')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=31536000')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"✅ Enhanced API server started on port {port}")
    print(f"📂 Upload directories:")
    print(f"   - /uploads/notices/")
    print(f"   - /uploads/purchase_orders/")
    server.serve_forever()
