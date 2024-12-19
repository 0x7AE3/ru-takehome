import json, os, sys
from tqdm import tqdm
import sqlite3
import numpy as np
from dotenv import load_dotenv
from typing import List, Tuple, Optional, Dict
from sentence_transformers import SentenceTransformer

class JobSearch:
    def __init__(self, db_path: str, recompute_embeddings: bool = False):
        """
        Initialize the job search system.
        
        Args:
            db_path: Path to SQLite database
            recompute_embeddings: Whether to recompute embeddings if they already exist
        """
        print("Initializing JobSearch system...")
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_embeddings (
                    rowid INTEGER PRIMARY KEY,
                    embedding BLOB
                )
            """)
            
        if recompute_embeddings or not self._embeddings_exist():
            print("Computing embeddings...")
            self._compute_embeddings()
        else:
            print("Embeddings already exist, skipping computation")
    
    def _embeddings_exist(self) -> bool:
        """Check if embeddings table has data."""
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM job_embeddings").fetchone()[0]
        return count > 0
    
    def _compute_embeddings(self):
        """Compute and store embeddings for all job postings."""
        with sqlite3.connect(self.db_path) as conn:
            jobs = conn.execute("""
                SELECT rowid, position, category, overview, team 
                FROM jobs
            """).fetchall()
            
        print(f"Computing embeddings for {len(jobs)} jobs...")
        
        texts = []
        for job in jobs:
            combined_text = f"{job[1]} {job[2]} {job[3]} {job[4]}"
            texts.append(combined_text)
        
        batch_size = 32
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size)):
            batch_texts = texts[i:i + batch_size]
            embeddings = self.model.encode(batch_texts)
            all_embeddings.extend(embeddings)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM job_embeddings")
            
            for job_id, embedding in zip([job[0] for job in jobs], all_embeddings):
                conn.execute(
                    "INSERT INTO job_embeddings (rowid, embedding) VALUES (?, ?)",
                    (job_id, embedding.tobytes())
                )
            
        print("Finished computing and storing embeddings")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for jobs matching the query.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of matching jobs with similarity scores
        """
        print(f"Searching for: {query}")
        
        query_embedding = self.model.encode(query)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT rowid, embedding FROM job_embeddings")
            
            similarities = []
            for row in cursor:
                job_id = row[0]
                embedding = np.frombuffer(row[1], dtype=np.float32)
                
                similarity = np.dot(query_embedding, embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                )
                similarities.append((job_id, similarity))
            
            top_jobs = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
            
            results = []
            for job_id, similarity in top_jobs:
                job = conn.execute("""
                    SELECT rowid, position, category, availability, city, url, 
                           overview, team, min_salary, max_salary
                    FROM jobs WHERE rowid = ?
                """, (job_id,)).fetchone()
                
                results.append({
                    'rowid': job[0],
                    'position': job[1],
                    'category': job[2],
                    'availability': job[3],
                    'city': job[4],
                    'url': job[5],
                    'overview': job[6],
                    'team': job[7],
                    'min_salary': job[8],
                    'max_salary': job[9],
                    'similarity': float(similarity)
                })
        
        return results

if __name__ == "__main__":
    load_dotenv()
    searcher = JobSearch("janestreet.db", recompute_embeddings=("-f" in sys.argv))
    if len(sys.argv) < 2:
        print("Please provide a query string as an argument")
        sys.exit(1)
    query = sys.argv[1]

    print("\n" + "="*50)
    print(f"Query: {query}")
    results = searcher.search(query, top_k=3)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['position']} ({result['city']})")
        print(f"   Team: {result['team']}")
        print(f"   Category: {result['category']}")
        print(f"   Similarity Score: {result['similarity']:.3f}")
        print(f"   URL: {result['url']}")
    print("\n" + "="*50)
