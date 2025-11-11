#!/usr/bin/env python3
"""
Test negation patterns in sentiment analysis
"""

from sentiment_analyzer import SentimentAnalyzer

def test_negation_patterns():
    """Test various negation patterns that should be flagged as negative."""

    analyzer = SentimentAnalyzer('sentiment.md')

    # Test cases with negations that should be flagged as negative
    test_messages = [
        # English negations
        "This is not good at all",
        "I'm not satisfied with the course",
        "Not getting any response from support",
        "The platform is not working properly",
        "I didn't get any help from the team",
        "This is not helpful",
        "Not able to access the portal",
        "I can't login to my account",
        "Couldn't find the lecture materials",
        "This doesn't work",
        "No response from anyone",
        "No help at all",
        "Never received my certificate",
        "This is not worth the money",
        "Not resolved yet",
        "The issue is not fixed",
        "Won't help me at all",
        "There's no point in continuing",

        # Hindi/Hinglish negations
        "Mujhe kuch nahi mila",
        "Response nahi aaya",
        "Help nahi ho rahi",
        "Clear nahi hai kuch bhi",
        "Samajh nahi aa raha",

        # Context-based negations (should be caught by context analysis)
        "The quality is not great",
        "Support is not responding",
        "Not clear what to do next",
        "I don't understand this at all",
        "This doesn't make any sense",
    ]

    print("Testing Negation Patterns")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, message in enumerate(test_messages, 1):
        sentiment = analyzer.analyze(message)
        matched_patterns = analyzer.get_matched_patterns(message)

        if sentiment == 'negative':
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"

        print(f"{i}. {status}")
        print(f"   Message: {message}")
        print(f"   Sentiment: {sentiment}")
        if matched_patterns:
            print(f"   Matched Patterns: {', '.join(matched_patterns[:3])}")
        print()

    print("=" * 80)
    print(f"Results: {passed}/{len(test_messages)} passed, {failed}/{len(test_messages)} failed")
    print(f"Success Rate: {(passed/len(test_messages)*100):.1f}%")

    return passed == len(test_messages)


if __name__ == '__main__':
    success = test_negation_patterns()
    exit(0 if success else 1)
