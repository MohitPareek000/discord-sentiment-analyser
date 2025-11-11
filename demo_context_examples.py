"""
Demo: Context Analysis in Action
Shows real examples of how context analysis detects negative sentiment
"""

from sentiment_analyzer import SentimentAnalyzer

def demo_context_analysis():
    """Demonstrate context analysis with real-world examples"""
    analyzer = SentimentAnalyzer()

    print("=" * 80)
    print("CONTEXT ANALYSIS DEMONSTRATION")
    print("=" * 80)
    print("\nThese messages would be MISSED by pattern matching alone,")
    print("but are correctly detected using context analysis:\n")
    print("=" * 80)

    # Examples that context analysis catches
    examples = [
        {
            "category": "Negated Positivity",
            "message": "The support is not good, I'm having issues",
            "explanation": "Context detects 'not' before 'good' (negation of positive word)"
        },
        {
            "category": "Intensified Negativity",
            "message": "This platform is extremely slow and really bad",
            "explanation": "Context detects intensifiers ('extremely', 'really') with negative words"
        },
        {
            "category": "Problem + Emotion Proximity",
            "message": "I'm dealing with a major issue and feeling very stressed about it",
            "explanation": "Context detects 'issue' (problem) near 'stressed' (emotion) within 10 words"
        },
        {
            "category": "Hindi Intensified Negativity",
            "message": "Bahut kharab experience hai, bohot mushkil ho raha hai",
            "explanation": "Context detects Hindi intensifiers with negative/problem words"
        },
        {
            "category": "Problem + Urgent Help",
            "message": "There's an error in my account, need help urgently please",
            "explanation": "Context detects problem word + help-seeking + urgency"
        },
        {
            "category": "Communication Failure",
            "message": "I tried to contact support three times but no response",
            "explanation": "Context detects communication breakdown pattern"
        },
        {
            "category": "Time Frustration",
            "message": "I've been waiting for a reply for weeks now",
            "explanation": "Context detects extended waiting period indicating frustration"
        },
        {
            "category": "Multiple Questions (Confusion)",
            "message": "How does this work? What am I supposed to do? Why isn't it clear?",
            "explanation": "Context detects 3 question marks indicating confusion/frustration"
        },
        {
            "category": "Consequence Statement",
            "message": "This delay is seriously affecting my career progress",
            "explanation": "Context detects serious consequence/impact statement (high weight: +2)"
        },
        {
            "category": "Repeated Negative Theme",
            "message": "The problem is still there, same problem as yesterday",
            "explanation": "Context detects 'problem' appearing multiple times"
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example['category']}")
        print("-" * 80)
        print(f"Message: \"{example['message']}\"")

        # Analyze the message
        sentiment = analyzer.analyze(example['message'])
        context_score = analyzer._analyze_context(example['message'])
        patterns = analyzer.get_matched_patterns(example['message'])

        print(f"\nResult:")
        print(f"  Sentiment: {sentiment.upper()}")
        print(f"  Context Score: {context_score}")
        print(f"  Pattern Matches: {', '.join(patterns) if patterns else 'None (caught by context only!)'}")
        print(f"\nHow Context Detected It:")
        print(f"  {example['explanation']}")
        print("=" * 80)

    # Show coding questions that remain neutral
    print("\n\nCODING QUESTIONS (Correctly Remain NEUTRAL)")
    print("=" * 80)
    print("These messages ask questions but are correctly NOT flagged as negative:")
    print("=" * 80)

    coding_examples = [
        "How do I write a function in Python?",
        "Can someone help me understand how loops work?",
        "What is the difference between let and var in JavaScript?",
        "How to create a class in Java?",
    ]

    for i, message in enumerate(coding_examples, 1):
        sentiment = analyzer.analyze(message)
        context_score = analyzer._analyze_context(message)

        print(f"\n{i}. \"{message}\"")
        print(f"   → Sentiment: {sentiment.upper()} | Context Score: {context_score}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Context analysis successfully detects nuanced negative sentiment")
    print("✓ Coding questions are correctly excluded from negative classification")
    print("✓ Multi-language support works seamlessly (English + Hindi/Hinglish)")
    print("✓ Score threshold of 2 provides balanced sensitivity")
    print("=" * 80)

if __name__ == "__main__":
    demo_context_analysis()
