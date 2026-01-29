"""
Model versioning and management system.

Handles model lifecycle, versioning, A/B testing, and deployment.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import joblib


class ModelVersion:
    """Represents a specific version of a model."""
    
    def __init__(
        self,
        model_name: str,
        version: str,
        model_path: str,
        metadata: Dict,
        created_at: Optional[str] = None
    ):
        self.model_name = model_name
        self.version = version
        self.model_path = model_path
        self.metadata = metadata
        self.created_at = created_at or datetime.now().isoformat()
        self.is_active = False
        self.performance_metrics = {}
        self.deployment_info = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'model_name': self.model_name,
            'version': self.version,
            'model_path': self.model_path,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'performance_metrics': self.performance_metrics,
            'deployment_info': self.deployment_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelVersion':
        """Create from dictionary."""
        version = cls(
            model_name=data['model_name'],
            version=data['version'],
            model_path=data['model_path'],
            metadata=data['metadata'],
            created_at=data.get('created_at')
        )
        version.is_active = data.get('is_active', False)
        version.performance_metrics = data.get('performance_metrics', {})
        version.deployment_info = data.get('deployment_info', {})
        return version


class ModelRegistry:
    """
    Central registry for managing model versions.
    
    Features:
    - Model versioning
    - Active model tracking
    - Performance monitoring
    - A/B testing support
    - Rollback capability
    """
    
    def __init__(self, registry_path: str = "ml_models/registry"):
        """
        Initialize model registry.
        
        Args:
            registry_path: Path to registry directory
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.registry_path / "registry.json"
        self.models: Dict[str, List[ModelVersion]] = {}
        
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from disk."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                
            for model_name, versions in data.items():
                self.models[model_name] = [
                    ModelVersion.from_dict(v) for v in versions
                ]
    
    def _save_registry(self):
        """Save registry to disk."""
        data = {
            model_name: [v.to_dict() for v in versions]
            for model_name, versions in self.models.items()
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        model_path: str,
        metadata: Dict,
        version: Optional[str] = None,
        set_active: bool = False
    ) -> ModelVersion:
        """
        Register a new model version.
        
        Args:
            model_name: Name of the model
            model_path: Path to model file
            metadata: Model metadata
            version: Version string (auto-generated if None)
            set_active: Whether to set as active version
            
        Returns:
            ModelVersion object
        """
        # Generate version if not provided
        if version is None:
            version = self._generate_version(model_name)
        
        # Create version object
        model_version = ModelVersion(
            model_name=model_name,
            version=version,
            model_path=model_path,
            metadata=metadata
        )
        
        # Add to registry
        if model_name not in self.models:
            self.models[model_name] = []
        
        self.models[model_name].append(model_version)
        
        # Set as active if requested
        if set_active:
            self.set_active_version(model_name, version)
        
        self._save_registry()
        
        return model_version
    
    def _generate_version(self, model_name: str) -> str:
        """Generate next version number."""
        if model_name not in self.models or not self.models[model_name]:
            return "1.0.0"
        
        # Get latest version
        versions = [v.version for v in self.models[model_name]]
        latest = max(versions)
        
        # Increment patch version
        major, minor, patch = latest.split('.')
        patch = str(int(patch) + 1)
        
        return f"{major}.{minor}.{patch}"
    
    def get_active_version(self, model_name: str) -> Optional[ModelVersion]:
        """Get active version of a model."""
        if model_name not in self.models:
            return None
        
        for version in self.models[model_name]:
            if version.is_active:
                return version
        
        return None
    
    def set_active_version(self, model_name: str, version: str):
        """Set a version as active."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        # Deactivate all versions
        for v in self.models[model_name]:
            v.is_active = False
        
        # Activate specified version
        for v in self.models[model_name]:
            if v.version == version:
                v.is_active = True
                v.deployment_info['activated_at'] = datetime.now().isoformat()
                break
        else:
            raise ValueError(f"Version {version} not found for model {model_name}")
        
        self._save_registry()
    
    def get_version(self, model_name: str, version: str) -> Optional[ModelVersion]:
        """Get specific version of a model."""
        if model_name not in self.models:
            return None
        
        for v in self.models[model_name]:
            if v.version == version:
                return v
        
        return None
    
    def list_versions(self, model_name: str) -> List[ModelVersion]:
        """List all versions of a model."""
        return self.models.get(model_name, [])
    
    def list_all_models(self) -> List[str]:
        """List all registered models."""
        return list(self.models.keys())
    
    def update_performance_metrics(
        self,
        model_name: str,
        version: str,
        metrics: Dict
    ):
        """Update performance metrics for a version."""
        model_version = self.get_version(model_name, version)
        if model_version:
            model_version.performance_metrics.update(metrics)
            model_version.performance_metrics['updated_at'] = datetime.now().isoformat()
            self._save_registry()
    
    def compare_versions(
        self,
        model_name: str,
        version1: str,
        version2: str
    ) -> Dict:
        """Compare two versions of a model."""
        v1 = self.get_version(model_name, version1)
        v2 = self.get_version(model_name, version2)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        comparison = {
            'model_name': model_name,
            'version1': {
                'version': v1.version,
                'created_at': v1.created_at,
                'is_active': v1.is_active,
                'metrics': v1.performance_metrics
            },
            'version2': {
                'version': v2.version,
                'created_at': v2.created_at,
                'is_active': v2.is_active,
                'metrics': v2.performance_metrics
            }
        }
        
        # Calculate metric differences
        if v1.performance_metrics and v2.performance_metrics:
            comparison['differences'] = {}
            for metric in v1.performance_metrics:
                if metric in v2.performance_metrics and isinstance(v1.performance_metrics[metric], (int, float)):
                    diff = v2.performance_metrics[metric] - v1.performance_metrics[metric]
                    comparison['differences'][metric] = {
                        'absolute': diff,
                        'relative': (diff / v1.performance_metrics[metric] * 100) if v1.performance_metrics[metric] != 0 else 0
                    }
        
        return comparison
    
    def rollback(self, model_name: str, to_version: Optional[str] = None):
        """
        Rollback to previous version or specified version.
        
        Args:
            model_name: Name of the model
            to_version: Version to rollback to (previous if None)
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        versions = self.models[model_name]
        
        if to_version is None:
            # Find previous version (second most recent)
            sorted_versions = sorted(
                versions,
                key=lambda v: v.created_at,
                reverse=True
            )
            
            if len(sorted_versions) < 2:
                raise ValueError("No previous version available for rollback")
            
            to_version = sorted_versions[1].version
        
        # Set the target version as active
        self.set_active_version(model_name, to_version)
    
    def delete_version(self, model_name: str, version: str, delete_files: bool = False):
        """
        Delete a model version.
        
        Args:
            model_name: Name of the model
            version: Version to delete
            delete_files: Whether to delete model files from disk
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model_version = self.get_version(model_name, version)
        if not model_version:
            raise ValueError(f"Version {version} not found")
        
        if model_version.is_active:
            raise ValueError("Cannot delete active version. Set another version as active first.")
        
        # Delete from registry
        self.models[model_name] = [
            v for v in self.models[model_name] if v.version != version
        ]
        
        # Delete files if requested
        if delete_files and Path(model_version.model_path).exists():
            Path(model_version.model_path).unlink()
            # Also delete metadata file if exists
            metadata_path = Path(model_version.model_path).with_suffix('.json')
            if metadata_path.exists():
                metadata_path.unlink()
        
        self._save_registry()
    
    def export_model(
        self,
        model_name: str,
        version: str,
        export_path: str
    ):
        """
        Export a model version to specified location.
        
        Args:
            model_name: Name of the model
            version: Version to export
            export_path: Destination path
        """
        model_version = self.get_version(model_name, version)
        if not model_version:
            raise ValueError(f"Version {version} not found")
        
        # Copy model file
        shutil.copy2(model_version.model_path, export_path)
        
        # Export metadata
        metadata_export_path = Path(export_path).with_suffix('.json')
        with open(metadata_export_path, 'w') as f:
            json.dump(model_version.to_dict(), f, indent=2)
    
    def get_registry_stats(self) -> Dict:
        """Get statistics about the registry."""
        stats = {
            'total_models': len(self.models),
            'total_versions': sum(len(versions) for versions in self.models.values()),
            'models': {}
        }
        
        for model_name, versions in self.models.items():
            active_version = self.get_active_version(model_name)
            
            stats['models'][model_name] = {
                'version_count': len(versions),
                'active_version': active_version.version if active_version else None,
                'latest_version': max(v.version for v in versions),
                'oldest_version': min(v.version for v in versions),
                'created_at': min(v.created_at for v in versions)
            }
        
        return stats


# Global registry instance
_registry = None


def get_registry(registry_path: str = "ml_models/registry") -> ModelRegistry:
    """Get or create global registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry(registry_path)
    return _registry
