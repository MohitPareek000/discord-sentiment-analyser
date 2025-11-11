"""
Test script to demonstrate context analysis feature
"""

from sentiment_analyzer import SentimentAnalyzer

def test_context_analysis():
    """Test the context analysis with various messages"""
    analyzer = SentimentAnalyzer()

    # Test messages that should be detected via context analysis
    test_messages = [
        # Context: Negated positivity
        {
            "message": "This is not good at all",
            "expected": "negative",
            "reason": "Negated positivity: 'not good'"
        },
        {
            "message": "No help from anyone, very disappointed",
            "expected": "negative",
            "reason": "Negated positivity + intensified emotion"
        },

        # Context: Problem + emotion proximity
        {
            "message": "I have a big issue and I'm really frustrated about it",
            "expected": "negative",
            "reason": "Problem word 'issue' near emotion word 'frustrated'"
        },

        # Context: Intensified negativity
        {
            "message": "This is extremely bad and very wrong",
            "expected": "negative",
            "reason": "Intensifiers with negative words"
        },
        {
            "message": "bahut kharab hai yaar, bohot problem aa raha",
            "expected": "negative",
            "reason": "Hindi intensifiers with negative words"
        },

        # Context: Problem + help seeking
        {
            "message": "There is an error, please help urgently",
            "expected": "negative",
            "reason": "Problem with urgent help request"
        },

        # Context: Multiple questions (confusion)
        {
            "message": "What should I do? How does this work? Why is this happening?",
            "expected": "negative",
            "reason": "Multiple questions indicating confusion"
        },

        # Context: Communication failure
        {
            "message": "I tried reaching out but no response yet",
            "expected": "negative",
            "reason": "Communication failure pattern"
        },

        # Context: Time frustration
        {
            "message": "Still waiting for an update, it's been days",
            "expected": "negative",
            "reason": "Time-related frustration"
        },

        # Context: Consequence statement
        {
            "message": "This is affecting my career and wasting my time",
            "expected": "negative",
            "reason": "Serious consequence statement"
        },

        # Neutral messages (should NOT be flagged)
        {
            "message": "How do I write a function in Python?",
            "expected": "neutral",
            "reason": "Simple coding question"
        },
        {
            "message": "Thanks for the help, everything is working great!",
            "expected": "neutral",
            "reason": "Positive feedback"
        },
        {
            "message": "When is the next class scheduled?",
            "expected": "neutral",
            "reason": "Simple scheduling question"
        },
    ]

    print("=" * 80)
    print("CONTEXT ANALYSIS TEST RESULTS")
    print("=" * 80)
    print()

    correct = 0
    total = len(test_messages)

    for i, test in enumerate(test_messages, 1):
        result = analyzer.analyze(test["message"])
        expected = test["expected"]
        is_correct = result == expected

        if is_correct:
            correct += 1
            status = "✓ PASS"
        else:
            status = "✗ FAIL"

        print(f"Test {i}: {status}")
        print(f"Message: {test['message']}")
        print(f"Expected: {expected} | Got: {result}")
        print(f"Reason: {test['reason']}")

        # Get context score for debugging
        if hasattr(analyzer, '_analyze_context'):
            context_score = analyzer._analyze_context(test['message'])
            print(f"Context Score: {context_score}")

        print("-" * 80)

    print()
    print("=" * 80)
    print(f"RESULTS: {correct}/{total} tests passed ({(correct/total)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    test_context_analysis()
