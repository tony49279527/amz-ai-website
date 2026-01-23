from fastapi import WebSocket
from typing import Dict, List
import asyncio
import json

class ProgressManager:
    def __init__(self):
        # Store active connections: task_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
        print(f"WS: Client connected to task {task_id}")

    def disconnect(self, task_id: str, websocket: WebSocket):
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
        print(f"WS: Client disconnected from task {task_id}")

    async def emit(self, task_id: str, step: str, status: str, progress: int, details: dict = None):
        """
        Send a progress update to all clients watching this task.
        """
        if task_id not in self.active_connections:
            return

        message = {
            "task_id": task_id,
            "step": step,           # e.g., "Web Research"
            "status": status,       # e.g., "Scraping YouTube..."
            "progress": progress,   # 0-100
            "details": details or {} # Extra data like logs or JSON previews
        }

        # Broadcast to all connected clients
        to_remove = []
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception:
                to_remove.append(connection)
        
        # Cleanup dead connections
        for dead in to_remove:
            self.disconnect(task_id, dead)

# Global instance
progress_manager = ProgressManager()
