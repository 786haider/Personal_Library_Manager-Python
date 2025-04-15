import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

class LibraryManager:
    def __init__(self):
        self.library = []
        self.filename = "library.txt"
        self.load_library()

    def add_book(self, title, author, year, genre, read_status):
        """Add a new book to the library"""
        book = {
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "read": read_status,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        }
        self.library.append(book)
        return book

    def remove_book(self, index):
        """Remove a book from the library by index"""
        if 0 <= index < len(self.library):
            removed = self.library.pop(index)
            return True, removed["title"]
        return False, ""

    def search_by_title(self, title):
        """Search for books by title"""
        results = [book for book in self.library if title.lower() in book["title"].lower()]
        return results

    def search_by_author(self, author):
        """Search for books by author"""
        results = [book for book in self.library if author.lower() in book["author"].lower()]
        return results

    def get_statistics(self):
        """Calculate library statistics"""
        total_books = len(self.library)
        read_books = sum(1 for book in self.library if book["read"])
        
        percentage_read = 0
        if total_books > 0:
            percentage_read = (read_books / total_books) * 100
            
        return {
            "total": total_books,
            "read": read_books,
            "unread": total_books - read_books,
            "percentage": percentage_read
        }

    def save_library(self):
        """Save the library to a file"""
        try:
            with open(self.filename, "w") as file:
                json.dump(self.library, file, indent=4)
            return True
        except Exception as e:
            st.error(f"Error saving library: {str(e)}")
            return False

    def load_library(self):
        """Load the library from a file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    self.library = json.load(file)
                return True
            except Exception as e:
                st.error(f"Error loading library: {str(e)}")
                return False
        return False

    def get_all_genres(self):
        """Get all unique genres in the library"""
        return sorted(set(book["genre"] for book in self.library))

    def filter_by_genre(self, genre):
        """Filter books by genre"""
        if genre == "All Genres":
            return self.library
        return [book for book in self.library if book["genre"] == genre]

def main():
    st.set_page_config(page_title="Personal Library Manager", page_icon="📚")
    
    # Initialize session state
    if "library_manager" not in st.session_state:
        st.session_state.library_manager = LibraryManager()
    
    # App title and description
    st.title("📚 Personal Library Manager")
    st.markdown("Manage your personal book collection with ease!")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Library", "Add Book", "Search", "Statistics"])
    
    # Library Tab
    with tab1:
        st.header("Your Book Collection")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            all_genres = ["All Genres"] + st.session_state.library_manager.get_all_genres()
            selected_genre = st.selectbox("Filter by Genre:", all_genres)
        
        with col2:
            read_options = ["All Books", "Read", "Unread"]
            selected_status = st.selectbox("Filter by Status:", read_options)
        
        # Apply filters
        filtered_books = st.session_state.library_manager.filter_by_genre(selected_genre)
        filtered_books = [book for book in filtered_books if (
            selected_status == "All Books" or 
            (selected_status == "Read" and book["read"]) or 
            (selected_status == "Unread" and not book["read"])
        )]
        
        # Convert to DataFrame for better display
        if filtered_books:
            df = pd.DataFrame(filtered_books)
            df["read_status"] = df["read"].apply(lambda x: "Read" if x else "Unread")
            df = df[["title", "author", "year", "genre", "read_status", "date_added"]]
            df.columns = ["Title", "Author", "Year", "Genre", "Status", "Date Added"]
            
            st.dataframe(df, use_container_width=True)
            
            # Remove book functionality
            st.subheader("Remove a Book")
            book_titles = [book["title"] for book in filtered_books]
            book_to_remove = st.selectbox("Select a book to remove:", [""] + book_titles)
            
            if st.button("Remove Selected Book") and book_to_remove:
                index = book_titles.index(book_to_remove)
                success, title = st.session_state.library_manager.remove_book(
                    st.session_state.library_manager.library.index(filtered_books[index])
                )
                if success:
                    st.session_state.library_manager.save_library()
                    st.success(f"'{title}' has been removed from your library!")
                    st.rerun()
        else:
            st.info("No books found in your library. Add some books in the 'Add Book' tab!")
    
    # Add Book Tab
    with tab2:
        st.header("Add a New Book")
        
        with st.form("add_book_form"):
            title = st.text_input("Book Title", key="title")
            author = st.text_input("Author", key="author")
            current_year = datetime.now().year
            year = st.number_input("Publication Year", min_value=0, max_value=current_year, value=current_year, key="year")
            genre = st.text_input("Genre", key="genre")
            read_status = st.checkbox("I have read this book", key="read")
            
            submitted = st.form_submit_button("Add Book")
            
            if submitted:
                if title and author and genre:
                    st.session_state.library_manager.add_book(title, author, int(year), genre, read_status)
                    st.session_state.library_manager.save_library()
                    st.success(f"'{title}' has been added to your library!")
                else:
                    st.error("Please fill in all required fields (title, author, and genre).")
    
    # Search Tab
    with tab3:
        st.header("Search for Books")
        
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            st.subheader("Search by Title")
            title_query = st.text_input("Enter title keywords:")
            if title_query:
                results = st.session_state.library_manager.search_by_title(title_query)
                if results:
                    st.write(f"Found {len(results)} matching books:")
                    for book in results:
                        read_status = "Read" if book["read"] else "Unread"
                        st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - {read_status}")
                else:
                    st.info("No books found matching your search.")
        
        with search_col2:
            st.subheader("Search by Author")
            author_query = st.text_input("Enter author name:")
            if author_query:
                results = st.session_state.library_manager.search_by_author(author_query)
                if results:
                    st.write(f"Found {len(results)} matching books:")
                    for book in results:
                        read_status = "Read" if book["read"] else "Unread"
                        st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - {read_status}")
                else:
                    st.info("No books found matching your search.")
    
    # Statistics Tab
    with tab4:
        st.header("Library Statistics")
        
        stats = st.session_state.library_manager.get_statistics()
        
        # Display basic stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats["total"])
        col2.metric("Books Read", stats["read"])
        col3.metric("Books Unread", stats["unread"])
        
        # Read/Unread visualization using Streamlit
        if stats["total"] > 0:
            st.subheader("Reading Progress")
            
            # Create a progress bar for read percentage
            st.progress(stats["percentage"] / 100)
            st.write(f"**{stats['percentage']:.1f}%** of your books have been read")
            
            # Display genre distribution
            st.subheader("Genre Distribution")
            genre_counts = {}
            for book in st.session_state.library_manager.library:
                genre = book["genre"]
                if genre in genre_counts:
                    genre_counts[genre] += 1
                else:
                    genre_counts[genre] = 1
            
            # Create a bar chart using Streamlit
            genre_data = pd.DataFrame({
                'Genre': list(genre_counts.keys()),
                'Count': list(genre_counts.values())
            }).sort_values('Count', ascending=False)
            
            st.bar_chart(genre_data.set_index('Genre'))
        else:
            st.info("Add some books to see statistics!")

if __name__ == "__main__":
    main()