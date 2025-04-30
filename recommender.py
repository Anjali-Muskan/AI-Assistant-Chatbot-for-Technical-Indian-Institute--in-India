import pandas as pd

def recommend_institutes(location, exam, category):
    df = pd.read_csv("sample_institutions.csv")

    # Basic filters
    filtered = df[
        (df["State"].str.lower() == location.lower()) &
        (df["Entrance Exam"].str.lower() == exam.lower()) &
        (df["Category"].str.lower() == category.lower())
    ]

    if filtered.empty:
        return "No exact match found. Try broadening your filters."

    # Return top 3 recommendations
    recommendations = []
    for _, row in filtered.head(3).iterrows():
        msg = f"{row['Institute Name']} ({row['State']})\n" \
              f"Course: {row['Course Offered']} | Fee: ₹{row['Fee Structure']}\n" \
              f"Last Date: {row['Application Deadline']} | Placement: {row['Placement Rate']}\n"
        recommendations.append(msg)

    return "\n".join(recommendations)
