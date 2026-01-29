#!/usr/bin/env python3
"""
Postman Collection Generator from OpenAPI Schema

This script automatically generates a Postman Collection from the FastAPI OpenAPI schema.
Usage:
    python scripts/generate_postman_collection.py
    
Output:
    postman_collection.json (in current directory)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.openapi.utils import get_openapi
from main import app


def generate_postman_collection() -> dict:
    """
    Generate Postman Collection v2.1.0 from OpenAPI schema
    
    Returns:
        dict: Postman Collection JSON
    """
    # Get OpenAPI schema from FastAPI app
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Initialize Postman Collection structure
    postman_collection = {
        "info": {
            "name": f"{openapi_schema['info']['title']} - API",
            "description": openapi_schema['info'].get('description', ''),
            "version": openapi_schema['info'].get('version', '1.0.0'),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{access_token}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "access_token",
                "value": "",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Group endpoints by tags
    grouped_endpoints = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, details in methods.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                tags = details.get("tags", ["Uncategorized"])
                tag = tags[0] if tags else "Uncategorized"
                
                if tag not in grouped_endpoints:
                    grouped_endpoints[tag] = []
                
                grouped_endpoints[tag].append({
                    "path": path,
                    "method": method.upper(),
                    "details": details
                })
    
    # Convert to Postman format
    for tag, endpoints in sorted(grouped_endpoints.items()):
        folder = {
            "name": tag,
            "item": []
        }
        
        for endpoint in sorted(endpoints, key=lambda x: x['path']):
            path = endpoint['path']
            method = endpoint['method']
            details = endpoint['details']
            
            # Build request object
            request_item = {
                "name": details.get("summary", f"{method} {path}"),
                "request": {
                    "method": method,
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json",
                            "type": "text"
                        }
                    ],
                    "url": {
                        "raw": f"{{{{base_url}}}}{path}",
                        "host": ["{{base_url}}"],
                        "path": path.strip('/').split('/')
                    },
                    "description": details.get("description", "")
                }
            }
            
            # Add authentication if needed
            if "security" in details:
                request_item["request"]["auth"] = {
                    "type": "bearer",
                    "bearer": [
                        {
                            "key": "token",
                            "value": "{{access_token}}",
                            "type": "string"
                        }
                    ]
                }
            
            # Add request body if present
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})
                
                # Extract example or generate from schema
                example = json_content.get("example")
                if not example and "properties" in schema:
                    example = {}
                    for prop, prop_schema in schema["properties"].items():
                        example[prop] = prop_schema.get("example", prop_schema.get("default", ""))
                
                if example:
                    request_item["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(example, indent=2),
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }
            
            # Add query parameters
            if "parameters" in details:
                query_params = []
                for param in details["parameters"]:
                    if param.get("in") == "query":
                        query_params.append({
                            "key": param["name"],
                            "value": str(param.get("example", "")),
                            "description": param.get("description", ""),
                            "disabled": not param.get("required", False)
                        })
                
                if query_params:
                    request_item["request"]["url"]["query"] = query_params
            
            # Add response examples
            responses = []
            for status_code, response_detail in details.get("responses", {}).items():
                response_description = response_detail.get("description", "")
                response_content = response_detail.get("content", {})
                json_response = response_content.get("application/json", {})
                response_example = json_response.get("example")
                
                if response_example:
                    responses.append({
                        "name": f"{status_code} - {response_description}",
                        "originalRequest": request_item["request"],
                        "status": response_description,
                        "code": int(status_code),
                        "_postman_previewlanguage": "json",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": json.dumps(response_example, indent=2) if isinstance(response_example, dict) else str(response_example)
                    })
            
            if responses:
                request_item["response"] = responses
            
            folder["item"].append(request_item)
        
        postman_collection["item"].append(folder)
    
    return postman_collection


def main():
    """Main function to generate and save Postman collection"""
    print("🚀 Generating Postman Collection from OpenAPI schema...")
    
    try:
        collection = generate_postman_collection()
        
        output_path = Path("postman_collection.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Postman Collection generated successfully!")
        print(f"📄 Output file: {output_path.absolute()}")
        print(f"📊 Total folders: {len(collection['item'])}")
        
        total_endpoints = sum(len(folder['item']) for folder in collection['item'])
        print(f"🔗 Total endpoints: {total_endpoints}")
        
        print("\n📝 Import instructions:")
        print("1. Open Postman")
        print("2. Click 'Import' button")
        print(f"3. Select '{output_path}' file")
        print("4. Configure environment variables (base_url, access_token)")
        
    except Exception as e:
        print(f"❌ Error generating Postman collection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
