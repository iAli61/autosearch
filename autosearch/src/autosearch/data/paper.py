from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Paper:
    title: str
    authors: List[str]
    url: str
    source: str
    pdf_url: Optional[str] = None
    local_path: Optional[str] = None
    abstract: Optional[str] = None
    published_date: Optional[datetime] = None
    last_updated_date: Optional[datetime] = None
    summary: Optional[str] = None
    id: Optional[str] = None  # For database purposes

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'authors': ', '.join(self.authors),
            'url': self.url,
            'pdf_url': self.pdf_url,
            'local_path': self.local_path,
            'abstract': self.abstract,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'last_updated_date': self.last_updated_date.isoformat() if self.last_updated_date else None,
            'source': self.source,
            'summary': self.summary,
            'id': self.id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Paper':
        authors = data['authors'].split(', ') if isinstance(data['authors'], str) else data['authors']
        return cls(
            title=data['title'],
            authors=authors,
            url=data['url'],
            pdf_url=data.get('pdf_url'),
            local_path=data.get('local_path'),
            abstract=data.get('abstract'),
            published_date=datetime.fromisoformat(data['published_date']) if data.get('published_date') else None,
            last_updated_date=datetime.fromisoformat(data['last_updated_date']) if data.get('last_updated_date') else None,
            source=data['source'],
            summary=data.get('summary'),
            id=data.get('id')
        )
