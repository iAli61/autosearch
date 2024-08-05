import sqlite3
import os
from typing import List, Tuple, Optional

class PaperDatabase:
    def __init__(self, project_dir: str):
        """
        Initialize the PaperDatabase.

        Args:
            project_dir (str): The directory path where the database file will be created.
        """
        self.project_dir = project_dir
        # create dir if not exists
        os.makedirs(project_dir, exist_ok=True)

        self.db_path = os.path.join(project_dir, 'papers.db')
        self._init_db()

    def _init_db(self):
        """Initialize the database with necessary tables."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS read_abstracts (
                url TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                published_date TEXT,
                last_updated_date TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS read_papers (
                url TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                published_date TEXT,
                last_updated_date TEXT,
                local_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_paper(self, table_name: str, paper_data: dict):
        """
        Add a paper to the specified table in the database.
        Only the URL is mandatory; other fields will use default values if missing.

        Args:
            table_name (str): The name of the table ('read_abstracts' or 'read_papers').
            paper_data (dict): A dictionary containing paper information.

        Raises:
            ValueError: If the 'url' field is missing from paper_data.
        """
        if 'url' not in paper_data:
            raise ValueError("The 'url' field is mandatory for adding a paper.")

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        if table_name == 'read_abstracts':
            c.execute('''
                INSERT OR REPLACE INTO read_abstracts 
                (url, title, authors, published_date, last_updated_date) 
                VALUES (?, ?, ?, ?, ?)
            ''', (
                paper_data['url'],
                paper_data.get('title', ''),
                paper_data.get('authors', ''),
                paper_data.get('published_date', ''),
                paper_data.get('last_updated_date', '')
            ))
        elif table_name == 'read_papers':
            c.execute('''
                INSERT OR REPLACE INTO read_papers 
                (url, title, authors, published_date, last_updated_date, local_path) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                paper_data['url'],
                paper_data.get('title', ''),
                paper_data.get('authors', ''),
                paper_data.get('published_date', ''),
                paper_data.get('last_updated_date', ''),
                paper_data.get('local_path', '')
            ))
        else:
            conn.close()
            raise ValueError(f"Invalid table name: {table_name}")

        conn.commit()
        conn.close()

    def check_paper(self, url: str, table_name: str) -> bool:
        """
        Check if a paper URL exists in the specified table.

        Args:
            url (str): The URL of the paper to check.
            table_name (str): The name of the table to check in.

        Returns:
            bool: True if the paper exists, False otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT url FROM {table_name} WHERE url = ?", (url,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def get_paper_info(self, url: str, table_name: str) -> Optional[dict]:
        """
        Retrieve paper information from the specified table.

        Args:
            url (str): The URL of the paper to retrieve.
            table_name (str): The name of the table to retrieve from.

        Returns:
            Optional[dict]: A dictionary containing paper information if found, None otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if table_name == 'read_abstracts':
            c.execute("SELECT * FROM read_abstracts WHERE url = ?", (url,))
            result = c.fetchone()
            if result:
                return {
                    'url': result[0],
                    'title': result[1],
                    'authors': result[2],
                    'published_date': result[3],
                    'last_updated_date': result[4]
                }
        elif table_name == 'read_papers':
            c.execute("SELECT * FROM read_papers WHERE url = ?", (url,))
            result = c.fetchone()
            if result:
                return {
                    'url': result[0],
                    'title': result[1],
                    'authors': result[2],
                    'published_date': result[3],
                    'last_updated_date': result[4],
                    'local_path': result[5]
                }
        conn.close()
        return None

    def count_papers(self, table_name: str) -> int:
        """
        Count the number of papers in the specified table.

        Args:
            table_name (str): The name of the table to count papers in.

        Returns:
            int: The number of papers in the table.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def get_all_papers(self, table_name: str) -> List[dict]:
        """
        Retrieve all papers from the specified table.

        Args:
            table_name (str): The name of the table to retrieve papers from.

        Returns:
            List[dict]: A list of dictionaries containing paper information.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if table_name == 'read_abstracts':
            c.execute("SELECT * FROM read_abstracts")
            return [
                {
                    'url': row[0],
                    'title': row[1],
                    'authors': row[2],
                    'published_date': row[3],
                    'last_updated_date': row[4]
                }
                for row in c.fetchall()
            ]
        elif table_name == 'read_papers':
            c.execute("SELECT * FROM read_papers")
            return [
                {
                    'url': row[0],
                    'title': row[1],
                    'authors': row[2],
                    'published_date': row[3],
                    'last_updated_date': row[4],
                    'local_path': row[5]
                }
                for row in c.fetchall()
            ]
        conn.close()
        return []

    def update_paper(self, url: str, table_name: str, update_data: dict):
        """
        Update paper information in the specified table.

        Args:
            url (str): The URL of the paper to update.
            table_name (str): The name of the table to update in.
            update_data (dict): A dictionary containing the fields to update.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        update_fields = ', '.join([f"{key} = ?" for key in update_data.keys()])
        query = f"UPDATE {table_name} SET {update_fields} WHERE url = ?"
        c.execute(query, list(update_data.values()) + [url])
        conn.commit()
        conn.close()

    def delete_paper(self, url: str, table_name: str):
        """
        Delete a paper from the specified table.

        Args:
            url (str): The URL of the paper to delete.
            table_name (str): The name of the table to delete from.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"DELETE FROM {table_name} WHERE url = ?", (url,))
        conn.commit()
        conn.close()

    def search_papers(self, table_name: str, search_term: str) -> List[dict]:
        """
        Search for papers in the specified table.

        Args:
            table_name (str): The name of the table to search in.
            search_term (str): The term to search for in titles and authors.

        Returns:
            List[dict]: A list of dictionaries containing matching paper information.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        search_term = f"%{search_term}%"
        if table_name == 'read_abstracts':
            c.execute("SELECT * FROM read_abstracts WHERE title LIKE ? OR authors LIKE ?", (search_term, search_term))
            return [
                {
                    'url': row[0],
                    'title': row[1],
                    'authors': row[2],
                    'published_date': row[3],
                    'last_updated_date': row[4]
                }
                for row in c.fetchall()
            ]
        elif table_name == 'read_papers':
            c.execute("SELECT * FROM read_papers WHERE title LIKE ? OR authors LIKE ?", (search_term, search_term))
            return [
                {
                    'url': row[0],
                    'title': row[1],
                    'authors': row[2],
                    'published_date': row[3],
                    'last_updated_date': row[4],
                    'local_path': row[5]
                }
                for row in c.fetchall()
            ]
        conn.close()
        return []

# Example usage
if __name__ == "__main__":
    db = PaperDatabase("./project_directory")
    
    # Add a paper with only URL
    db.add_paper('read_abstracts', {
        'url': 'https://arxiv.org/abs/1234.5678'
    })

    # Add a paper with partial information
    db.add_paper('read_abstracts', {
        'url': 'https://arxiv.org/abs/2345.6789',
        'title': 'Partial Information Paper',
        'authors': 'John Doe'
    })

    # Add a paper with full information
    db.add_paper('read_papers', {
        'url': 'https://arxiv.org/abs/3456.7890',
        'title': 'Full Information Paper',
        'authors': 'Jane Smith, Bob Johnson',
        'published_date': '2023-05-15',
        'last_updated_date': '2023-05-20',
        'local_path': '/path/to/local/file.pdf'
    })

    # Try to add a paper without URL (this will raise an error)
    try:
        db.add_paper('read_abstracts', {
            'title': 'Paper Without URL'
        })
    except ValueError as e:
        print(f"Error: {e}")

    # Check if papers exist
    print(db.check_paper('https://arxiv.org/abs/1234.5678', 'read_abstracts'))
    print(db.check_paper('https://arxiv.org/abs/2345.6789', 'read_abstracts'))
    print(db.check_paper('https://arxiv.org/abs/3456.7890', 'read_papers'))

    # Get paper info
    print(db.get_paper_info('https://arxiv.org/abs/1234.5678', 'read_abstracts'))
    print(db.get_paper_info('https://arxiv.org/abs/2345.6789', 'read_abstracts'))
    print(db.get_paper_info('https://arxiv.org/abs/3456.7890', 'read_papers'))