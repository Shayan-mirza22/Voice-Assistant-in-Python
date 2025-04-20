import wikipedia

def search_wikipedia(query):
    """
    Search Wikipedia and return a summary of the first result.
    
    Args:
        query (str): The search term to look up on Wikipedia
    
    Returns:
        str: A summary of the Wikipedia page or an error message
    """
    try:
        # Try to search for the query
        search_results = wikipedia.search(query)
        
        # If no results found
        if not search_results:
            return f"No Wikipedia results found for '{query}'."
        
        # Get the first search result
        page_title = search_results[0]
        
        # Try to get the page
        page = wikipedia.page(page_title)
        
        # Return the first 3-4 sentences of the summary
        summary_sentences = page.summary.split('.')[:4]
        summary = '. '.join(summary_sentences) + '.'
        
        return f"Wikipedia summary for '{page_title}':\n{summary}"
    
    except wikipedia.DisambiguationError as e:
        # Handle disambiguation pages with multiple possible results
        return f"Your search '{query}' may refer to multiple pages. Possible matches include:\n" + \
               "\n".join(e.options[:5])
    
    except wikipedia.PageError:
        # Handle cases where the specific page cannot be found
        return f"No exact Wikipedia page found for '{query}'. Try a different search term."
    
    except Exception as e:
        # Catch any other unexpected errors
        return f"An error occurred while searching Wikipedia: {str(e)}"

# Example usage
if __name__ == "__main__":
    print(search_wikipedia("Imran Khan"))
    print("\n---\n")
    print(search_wikipedia("Albert Einstein"))