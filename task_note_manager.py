"""
Task and Note Manager Module
Handles storage and retrieval of tasks and notes
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class TaskNoteManager:
    """Manages tasks and notes with JSON file storage"""
    
    def __init__(self, storage_dir: str = "data"):
        """
        Initialize the TaskNoteManager
        
        Args:
            storage_dir: Directory to store data files
        """
        self.storage_dir = storage_dir
        self.tasks_file = os.path.join(storage_dir, "tasks.json")
        self.notes_file = os.path.join(storage_dir, "notes.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_file(self.tasks_file)
        self._init_file(self.notes_file)
    
    def _init_file(self, filepath: str):
        """Initialize a JSON file if it doesn't exist"""
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _load_data(self, filepath: str, user_id: int) -> List[Dict]:
        """Load data for a specific user from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                return all_data.get(str(user_id), [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, filepath: str, user_id: int, data: List[Dict]):
        """Save data for a specific user to file"""
        try:
            # Load all user data
            with open(filepath, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            all_data = {}
        
        # Update user's data
        all_data[str(user_id)] = data
        
        # Save back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # ===== TASK METHODS =====
    
    def add_task(self, user_id: int, title: str, description: str = "", priority: str = "medium") -> Dict:
        """
        Add a new task
        
        Args:
            user_id: Telegram user ID
            title: Task title
            description: Task description (optional)
            priority: Priority level (low, medium, high)
        
        Returns:
            Dict with success status and task data
        """
        tasks = self._load_data(self.tasks_file, user_id)
        
        # Generate unique ID
        task_id = len(tasks) + 1
        while any(t['id'] == task_id for t in tasks):
            task_id += 1
        
        new_task = {
            'id': task_id,
            'title': title,
            'description': description,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        tasks.append(new_task)
        self._save_data(self.tasks_file, user_id, tasks)
        
        return {'success': True, 'task': new_task}
    
    def get_tasks(self, user_id: int, include_completed: bool = False) -> List[Dict]:
        """
        Get all tasks for a user
        
        Args:
            user_id: Telegram user ID
            include_completed: Whether to include completed tasks
        
        Returns:
            List of tasks
        """
        tasks = self._load_data(self.tasks_file, user_id)
        
        if not include_completed:
            tasks = [t for t in tasks if not t['completed']]
        
        return sorted(tasks, key=lambda x: x['created_at'], reverse=True)
    
    def complete_task(self, user_id: int, task_id: int) -> Dict:
        """
        Mark a task as completed
        
        Args:
            user_id: Telegram user ID
            task_id: Task ID to complete
        
        Returns:
            Dict with success status and message
        """
        tasks = self._load_data(self.tasks_file, user_id)
        
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self._save_data(self.tasks_file, user_id, tasks)
                return {'success': True, 'message': 'Task completed', 'task': task}
        
        return {'success': False, 'error': 'Task not found'}
    
    def delete_task(self, user_id: int, task_id: int) -> Dict:
        """
        Delete a task
        
        Args:
            user_id: Telegram user ID
            task_id: Task ID to delete
        
        Returns:
            Dict with success status and message
        """
        tasks = self._load_data(self.tasks_file, user_id)
        
        for i, task in enumerate(tasks):
            if task['id'] == task_id:
                deleted_task = tasks.pop(i)
                self._save_data(self.tasks_file, user_id, tasks)
                return {'success': True, 'message': 'Task deleted', 'task': deleted_task}
        
        return {'success': False, 'error': 'Task not found'}
    
    def search_tasks(self, user_id: int, query: str) -> List[Dict]:
        """
        Search tasks by title or description
        
        Args:
            user_id: Telegram user ID
            query: Search query
        
        Returns:
            List of matching tasks
        """
        tasks = self._load_data(self.tasks_file, user_id)
        query_lower = query.lower()
        
        return [
            t for t in tasks
            if query_lower in t['title'].lower() or query_lower in t.get('description', '').lower()
        ]
    
    # ===== NOTE METHODS =====
    
    def add_note(self, user_id: int, title: str, content: str = "", tags: List[str] = None) -> Dict:
        """
        Add a new note
        
        Args:
            user_id: Telegram user ID
            title: Note title
            content: Note content
            tags: List of tags (optional)
        
        Returns:
            Dict with success status and note data
        """
        notes = self._load_data(self.notes_file, user_id)
        
        # Generate unique ID
        note_id = len(notes) + 1
        while any(n['id'] == note_id for n in notes):
            note_id += 1
        
        new_note = {
            'id': note_id,
            'title': title,
            'content': content,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        notes.append(new_note)
        self._save_data(self.notes_file, user_id, notes)
        
        return {'success': True, 'note': new_note}
    
    def get_notes(self, user_id: int) -> List[Dict]:
        """
        Get all notes for a user
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            List of notes
        """
        notes = self._load_data(self.notes_file, user_id)
        return sorted(notes, key=lambda x: x['updated_at'], reverse=True)
    
    def get_note(self, user_id: int, note_id: int) -> Optional[Dict]:
        """
        Get a specific note
        
        Args:
            user_id: Telegram user ID
            note_id: Note ID
        
        Returns:
            Note data or None if not found
        """
        notes = self._load_data(self.notes_file, user_id)
        
        for note in notes:
            if note['id'] == note_id:
                return note
        
        return None
    
    def update_note(self, user_id: int, note_id: int, title: str = None, content: str = None, tags: List[str] = None) -> Dict:
        """
        Update a note
        
        Args:
            user_id: Telegram user ID
            note_id: Note ID to update
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
        
        Returns:
            Dict with success status and updated note
        """
        notes = self._load_data(self.notes_file, user_id)
        
        for note in notes:
            if note['id'] == note_id:
                if title is not None:
                    note['title'] = title
                if content is not None:
                    note['content'] = content
                if tags is not None:
                    note['tags'] = tags
                note['updated_at'] = datetime.now().isoformat()
                
                self._save_data(self.notes_file, user_id, notes)
                return {'success': True, 'message': 'Note updated', 'note': note}
        
        return {'success': False, 'error': 'Note not found'}
    
    def delete_note(self, user_id: int, note_id: int) -> Dict:
        """
        Delete a note
        
        Args:
            user_id: Telegram user ID
            note_id: Note ID to delete
        
        Returns:
            Dict with success status and message
        """
        notes = self._load_data(self.notes_file, user_id)
        
        for i, note in enumerate(notes):
            if note['id'] == note_id:
                deleted_note = notes.pop(i)
                self._save_data(self.notes_file, user_id, notes)
                return {'success': True, 'message': 'Note deleted', 'note': deleted_note}
        
        return {'success': False, 'error': 'Note not found'}
    
    def search_notes(self, user_id: int, query: str) -> List[Dict]:
        """
        Search notes by title, content, or tags
        
        Args:
            user_id: Telegram user ID
            query: Search query
        
        Returns:
            List of matching notes
        """
        notes = self._load_data(self.notes_file, user_id)
        query_lower = query.lower()
        
        return [
            n for n in notes
            if (query_lower in n['title'].lower() or 
                query_lower in n.get('content', '').lower() or
                any(query_lower in tag.lower() for tag in n.get('tags', [])))
        ]
