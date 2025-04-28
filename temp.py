import wikipedia
query = input("Enter command")
query = query.replace("wikipedia", "")
results = wikipedia.summary(query, sentences=3)
print(results)
