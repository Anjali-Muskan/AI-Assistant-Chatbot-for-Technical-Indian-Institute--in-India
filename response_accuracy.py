import pandas as pd
from difflib import SequenceMatcher

# Load the test dataset
df = pd.read_csv('chatbot_test_data.csv')

# Function to compare expected vs actual response using similarity ratio
def is_accurate(expected, actual, threshold=0.85):
    similarity = SequenceMatcher(None, expected.lower(), actual.lower()).ratio()
    return similarity >= threshold

# Apply comparison and store results
df['is_correct'] = df.apply(lambda row: is_accurate(row['expected_response'], row['bot_response']), axis=1)

# Accuracy calculation
total = len(df)
correct = df['is_correct'].sum()
accuracy = (correct / total) * 100

print(f"Total Test Cases: {total}")
print(f"Correct Responses: {correct}")
print(f"Chatbot Accuracy: {accuracy:.2f}%")
