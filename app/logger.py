"""MongoDB logger module for user action tracking."""
from datetime import datetime
from typing import Any
from pymongo.collection import Collection
from app.mongo import mongo


class UserLogger:
    """Handle user actions logging to MongoDB"""
    collection_name: str
    
    def __init__(self):
        """
        Initialize UserLogger
        """
        self.collection_name = "user_logs"

    def _collection(self) -> Collection[dict[str, Any]] | None:
        if mongo.db is None:
            return None
        return mongo.db[self.collection_name]
    
    def log_action(
        self,
        current_user: Any,
        module: str,
        action: str,        
        success: bool,
    ) -> str | None:
        """
        Log a user action to MongoDB
        
        Args:
            current_user: The current user object
            module: The module where the action occurred
            action: Action name (e.g., 'create_product', 'delete_customer')
            success: Whether the action was successful
        Returns:
            MongoDB document ID or None if logging failed
        """
        collection = self._collection()
        if collection is None:
            print("Warning: MongoDB connection not available, skipping log")
            return None
        
        try:
            log_entry: dict[str, Any] = {
                "date": datetime.now(),
                "user_id": getattr(current_user, "id", None),
                "user_name": getattr(current_user, "nombre_completo", "unknown"),
                "module": module,
                "action": action,
                "success": success
            }
            
            result = collection.insert_one(log_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error logging action: {e}")
            return None

    def get_logs(
        self,
        query: str = "",
        page: int = 1,
        per_page: int = 10,
    ) -> tuple[list[dict[str, Any]], int]:
        """Retrieve user logs with optional search and pagination."""
        collection = self._collection()
        if collection is None:
            return [], 0

        if page < 1:
            page = 1
        if per_page < 5:
            per_page = 5
        if per_page > 50:
            per_page = 50

        raw_query = (query or "").strip()
        filters: dict[str, Any] = {}

        if raw_query:
            regex_filter = {"$regex": raw_query, "$options": "i"}
            or_filters: list[dict[str, Any]] = [
                {"user_name": regex_filter},
                {"module": regex_filter},
                {"action": regex_filter},
            ]

            normalized = raw_query.lower()
            if normalized in {"true", "success", "ok", "exito", "exitoso"}:
                or_filters.append({"success": True})
            if normalized in {"false", "fail", "failed", "error", "fallido"}:
                or_filters.append({"success": False})

            filters = {"$or": or_filters}

        try:
            total = collection.count_documents(filters)
            cursor = (
                collection.find(filters)
                .sort("date", -1)
                .skip((page - 1) * per_page)
                .limit(per_page)
            )
            return list(cursor), total
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return [], 0
    
