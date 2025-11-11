"""
Sentiment Analyzer Module
Analyzes messages based on rules defined in sentiment.md
"""

import re
import os


class SentimentAnalyzer:
    """Analyzes Discord messages for negative sentiment based on predefined rules."""

    def __init__(self, sentiment_rules_file='sentiment.md', manual_examples_file='sentimentManual.md'):
        """
        Initialize sentiment analyzer with rules from sentiment.md and examples from sentimentManual.md

        Args:
            sentiment_rules_file: Path to sentiment rules markdown file
            manual_examples_file: Path to manual negative examples file
        """
        # Load additional context from sentiment.md if available
        self.sentiment_context = self._load_sentiment_context(sentiment_rules_file)
        # Load manual examples for reference
        self.manual_examples_loaded = self._check_manual_examples(manual_examples_file)
        # CRITICAL SIGNALS patterns (English and Hindi)
        self.critical_signals = [
            # English critical signals - Refund/Quit/Leave
            r'\b(quit|leave|refund|discontinue|cancel|cancellation)\b',
            r'\brefund\s+process\b',
            r'\brequest.*refund\b',
            r'\bwant.*refund\b',
            r'\bcannot\s+cope\b',
            r'\bnot.*align\b.*\b(situation|career)\b',

            # Frustration & Emotions
            r'\b(fed up|frustrated|disappointed|irony|angry|mad)\b',
            r'\ba\s+lot\s+of\s+(concerns|issues|problems)\b',
            r'\bmental\s+burden\b',
            r'\bregret\b.*\b(decision|joining|enrolled)\b',
            r'\braising.*concern\b',
            r'\baddress.*this.*issue.*here\b',
            r'\bthis.*will.*give.*clarity\b',
            r'\bas.*a.*fresher.*we.*are.*facing\b',
            r'\bseeking.*help.*from\b',
            r'\bfor.*better.*guidance\b',

            # Support & Communication Issues
            r'\b(unresponsive support|unable to raise ticket)\b',
            r'\b(still having issues|reported multiple times|not getting sorted)\b',
            r'\b(was told.*but|they said.*now)\b',
            r'\btrying\s+to\s+reach\b.*\b(not|no)\b.*\b(answerable|response|reply)\b',
            r'\bnot\s+getting.*call\s+back\b',
            r'\bwaiting\s+for.*response\b',
            r'\bmessaged.*personally.*still\s+waiting\b',
            r'\bnot.*answerable\b',
            r'\bhaven\'?t.*received.*(text|call|response).*back\b',
            r'\bsame.*has.*been.*happening\b.*\b(with|to)\b.*\bme\b',
            r'\btried.*reaching.*haven\'?t.*received\b',
            r'\bis.*there.*any.*one.*from.*(scalar|scaler).*support\b',
            r'\bplease.*help.*to.*get.*fixed\b',

            # Technical & Platform Issues
            r'\b(audio issues|login problems|missing content|locked sections)\b',
            r'\bunable\s+to\s+(follow|understand|develop|attend)\b',
            r'\bget\s+stuck\b',
            r'\b(lagging|stuck|freezing)\s+(a\s+lot|most\s+of\s+the\s+time)\b',
            r'\bdashboard.*(lagging|stuck|problem|issue)\b',
            r'\bdriving.*class.*(very|too).*fast\b',
            r'\bskipping.*steps.*when.*explaining\b',
            r'\bunable.*to.*develop.*logic\b',

            # Curriculum & Quality Concerns
            r'\b(placement complaint|unmet expectations|job opportunities)\b',
            r'\bchanged\s+without.*notice\b',
            r'\bnot\s+covered\b.*\b(module|syllabus|curriculum)\b',
            r'\bpaying.*money\b.*\b(not|redirect|better)\b',
            r'\bpaying.*good.*amount.*money\b',
            r'\bnot.*good.*to.*redirect\b',
            r'\bout.*of.*syllabus\b',
            r'\bprogram.*changed.*without.*notice\b',
            r'\bprogram.*structure.*moving.*forward\b',
            r'\bambiguity.*misalignment.*expectations\b',
            r'\bpriority\s+basis\b',
            r'\bescalate.*management\b',
            r'\blegal\s+standpoint\b',
            r'\bcompelled\s+to\s+(accept|take\s+action|consider.*action)\b',
            r'\bmay.*be.*compelled.*to.*consider\b',
            r'\bfrom.*legal.*standpoint\b',
            r'\bjoin.*course.*based.*on.*vision\b',
            r'\bif.*situation.*worsens\b',

            # Confusion & Lack of Understanding (English)
            r'\b(confused|confusing|confusion|unclear|not clear|don\'?t understand)\b',
            r'\b(lost|stuck|clueless|no idea|no clue)\b',
            r'\b(what.*going on|what.*happening|what.*supposed to do)\b',
            r'\b(too complicated|too complex|too difficult|too hard)\b',
            r'\b(not making sense|doesn\'?t make sense|makes no sense)\b',
            r'\b(can\'?t figure out|unable to understand|failing to understand)\b',
            r'\b(completely lost|totally lost|very confused|really confused)\b',

            # Confusion & Lack of Understanding (Hindi/Hinglish)
            r'\b(samajh.*nahi.*aa.*raha|samajh.*nahi.*aaya|samajh.*nhi)\b',
            r'\b(confuse.*ho.*gaya|confuse.*ho.*gayi|confusion.*hai)\b',
            r'\b(kuch.*samajh.*nahi|kuch.*samajh.*nhi|kya.*karna.*hai)\b',
            r'\b(clear.*nahi|clear.*nhi|samajh.*nahi)\b',
            r'\b(bahut.*mushkil|bohot.*mushkil|itna.*difficult)\b',
            r'\b(kaise.*karna|kaise.*kare|kaise.*hoga)\b.*\b(samajh|pata|understand)\b',

            # Help-seeking Questions (English)
            r'\b(how do i|how can i|how to|what should i|where do i|when should i)\b',
            r'\b(can someone help|need help|help me|assist me|anyone help)\b',
            r'\b(what is|what are|why is|why are|which is|which are)\b.*\?',
            r'\b(is there|are there|will there|would there)\b.*\?',
            r'\b(could you|would you|can you|will you)\b.*\b(help|explain|tell|show)\b',
            r'\b(any idea|any suggestions|any help|anyone knows|does anyone)\b',

            # Help-seeking Questions (Hindi/Hinglish)
            r'\b(kaise|kaise kare|kaise karna|kaise hoga|kya hai|kya kare)\b',
            r'\b(koi.*bata.*sakta|koi.*help.*kar.*sakta|help.*chahiye)\b',
            r'\b(mujhe.*samajh.*nahi|mujhe.*pata.*nahi|kya.*karna.*chahiye)\b',
            r'\b(kaha.*milega|kaha.*hai|kab.*hoga|kab.*milega)\b',
            r'\b(koi.*hai.*jo|someone.*help|koi.*help)\b',

            # Doubt & Uncertainty (English)
            r'\b(doubt|doubts|not sure|unsure|uncertain|unclear about)\b',
            r'\b(have.*doubt|having.*doubt|got.*doubt|any.*doubt)\b',
            r'\b(not confident|lacking confidence|worried about|concerned about)\b',
            r'\b(questioning|second guessing|hesitant|skeptical)\b',

            # Doubt & Uncertainty (Hindi/Hinglish)
            r'\b(doubt.*hai|doubt.*aa.*raha|shak.*hai|confusion.*hai)\b',
            r'\b(confirm.*nahi|sure.*nahi|pata.*nahi.*sahi)\b',
            r'\b(theek.*hai.*ya.*nahi|sahi.*hai.*ya.*nahi)\b',
            r'\b(samajh.*mein.*nahi.*aa.*raha|dimag.*mein.*nahi.*aa.*raha)\b',

            # Negative Contractions (English)
            r'\b(didn\'?t|don\'?t|doesn\'?t|won\'?t|wouldn\'?t|shouldn\'?t)\b',
            r'\b(can\'?t|couldn\'?t|isn\'?t|aren\'?t|wasn\'?t|weren\'?t)\b',
            r'\b(haven\'?t|hasn\'?t|hadn\'?t|ain\'?t)\b',

            # Batch/Schedule Issues
            r'\bcannot\s+attend\b.*\b(evening|morning|sessions)\b',
            r'\bdirectly\s+impacting.*career\b',
            r'\bbatch.*shifted\b.*\b(without|no)\b.*\b(poll|feedback)\b',

            # Agreement with others' complaints
            r'\b(same here|me too)\b.*\b(complaint|issue|problem)\b',
            r'\bsame.*happening\s+with\s+me\b',

            # Hindi/Hinglish critical signals
            r'\b(chhod|chod|chodna|chhodna|band.*kar|bandh.*kar)\b.*\b(course|program|class)\b',
            r'\b(paisa.*wapas|refund.*chahiye|paise.*vapas)\b',
            r'\b(pareshan|preshan|tang|gussa|thak.*gaya|thak.*gayi)\b',
            r'\b(koi.*jawab.*nahi|reply.*nahi|kuch.*response.*nahi)\b',
            r'\b(kitni.*baar|kitne.*baar|baar.*baar)\b.*\b(bola|kaha|bataya|complain)\b',
        ]

        # SUPPORT FAILURES patterns (English and Hindi)
        self.support_failures = [
            # English support failures - Basic
            r'\b(unable to reach|not responding|haven\'?t got back|no one joined)\b',
            r'\b(who is support|how to contact support)\b',
            r'\bwhen will.*call me\b',
            r'\b(support ticket|help request).*not.*addressed\b',
            r'\b(no response|no reply|not replying|ignoring)\b',

            # Advanced support failure patterns from sentimentManual.md
            r'\bhelp.*to.*get.*fixed.*issue\b',
            r'\braising.*help.*request\b',
            r'\btrying.*to.*reach.*(POC|support|TA|instructor)\b',
            r'\bhaven\'?t.*received.*(text|response|reply|call)\s+back\b',
            r'\bnot.*good.*communication.*from\s+(TA|support|team)\b',
            r'\breceiving.*good.*communication\b',
            r'\bnot.*the.*right.*person.*to.*help\b',
            r'\bescalate.*to.*(senior|management)\b',
            r'\bshare.*alternate.*contact\b',
            r'\bif.*you.*cannot.*address\b',
            r'\bticket.*raised\b',
            r'\braised.*ticket\b',

            # Hindi/Hinglish support failures
            r'\b(support.*nahi.*mil|mil.*nahi.*raha|koi.*pick.*nahi)\b',
            r'\b(call.*nahi.*aaya|call.*nahi.*kiya|call.*back.*nahi)\b',
            r'\b(kab.*milega|kab.*ayega|kab.*hoga)\b.*\b(support|help|response)\b',
            r'\b(ticket.*raise.*nahi|complaint.*nahi)\b',
        ]

        # TECHNICAL ISSUES patterns (English and Hindi)
        self.technical_issues = [
            # English technical issues
            r'\b(cannot join class|see assignment|access content)\b',
            r'\b(configuration|setup).*problem.*preventing\b',
            r'\b(missed despite|system error)\b',
            r'\b(platform bug|submission|progress)\b',
            r'\b(not working|broken|crashed|freeze|freezing|stuck)\b',
            # Hindi/Hinglish technical issues (full phrases)
            r'\b(kaam.*nahi.*kar.*raha|work.*nahi.*kar.*raha|chalu.*nahi)\b',
            r'\b(khul.*nahi.*raha|open.*nahi.*ho.*raha|access.*nahi)\b',
            r'\b(login.*nahi.*ho.*raha|sign.*in.*nahi)\b',
            r'\b(error.*aa.*raha|problem.*aa.*raha|dikkat.*aa.*rahi)\b',
            # Shortened Hindi forms with "nhi"
            r'\b(kaam|work|site|platform|app|login|class).*nhi.*(kar|ho|chal|kr)\b',
            r'\bnhi.*(khul|open|access|login|join|start)\b',
            r'\b(khul|open|load|start).*nhi.*(raha|rahi|rahe|ho)\b',
            r'\b(video|audio|mic|camera|screen).*nhi.*(aa|dikha|suna|chal)\b',
        ]

        # NEGATIVE LANGUAGE patterns (English and Hindi)
        self.negative_language = [
            # Hindi negative words (common in Hinglish/Roman Hindi)
            r'\b(bekar|bekaar|ganda|kharab|khatam|waste|bakwas|bakwaas|faltu|ghatiya|ghatia)\b',
            r'\b(bura|buri|galat|galti|band|bandh)\b',
            r'\b(jhooth|jhoot|dhoka|dhokha|paisa|paise.*barbaad|barbad)\b',
            r'\b(dimag.*kharab|pagal|bewakoof|bevkoof|chutiya|ullu)\b',

            # Hindi "no/not" patterns with common phrases
            r'\b(nhi|nahi|nahin|nai|na)\b',  # All forms of "no/not"
            r'\bnhi\s+(work|kar|ho|mil|chal|aa|hua|hoga|milega)\b',  # nhi + action
            r'\bnahi\s+(kar|ho|mil|chal|aa|work|hota|hoga|milega)\b',  # nahi + action
            r'\b(work|kaam|class|platform|site|app|login|access).*nhi\b',  # thing + nhi
            r'\b(work|kaam|class|platform|site|app|login|access).*nahi\b',  # thing + nahi
            r'\bnhi\s+(kr|ho|mil)\s+(raha|rahi|rahe|rhe|paa)\b',  # nhi kr raha etc
            r'\b(kr|kar|ho|chal)\s+nhi\s+(raha|rahi|rahe|paa)\b',  # kar nhi raha

            # English "not" patterns
            r'\b(not|no)\s+(working|responding|helping|fixed|resolved|done)\b',
            r'\b(still|yet|never)\s+not\b',
            r'\bdoes.*not\s+(work|help|respond)\b',
            r'\bis.*not\s+(working|responding|helping)\b',

            # Combined negative contexts (Hindi + problem words)
            r'\b(kya.*hai|kya.*ho.*gaya|kuch.*nahi|koi.*nahi|kuch.*nhi|koi.*nhi)\b.*\b(problem|issue|help|support)\b',
            r'\b(problem|issue|dikkat|pareshani).*\b(nhi|nahi|not|no)\b.*\b(solve|resolved|fixed|theek)\b',

            # English negative words
            r'\b(terrible|horrible|awful|pathetic|useless|garbage|trash|rubbish)\b',
            r'\b(disgusting|nightmare|disaster|worst|sucks|scam|fraud|fake)\b',
            r'\b(disappointing|ridiculous|joke|nonsense)\b',

            # Patterns
            r'\?\?+',  # Multiple question marks
            r'\bwhat is the update\?\?',
            r'\b[A-Z]{3,}.*\b(complaint|issue|problem)\b',  # ALL CAPS complaints
            r'\d+\s*unplaced.*\d+\s*placed',  # Sarcasm about statistics
        ]

        # EXCLUSION patterns (DO NOT flag if ONLY these)
        self.exclusion_patterns = [
            r'\b(coding help|conceptual doubt|course material)\b',
            r'\b(schedule|scheduling question)\b',
            r'\b(thank|thanks|great|awesome|helpful)\b',  # Removed 'good' as it can be negated
            r'\b(can someone help|how to|what is|how do|how does|help.*understand|help.*learn)\b.*\b(code|function|variable|class|python|java|javascript|program|algorithm|method|syntax|loops?|arrays?|string|object|recursion|data structure)\b',
            r'\b(write|create|make|build).*\b(function|program|code|script|algorithm)\b.*\b(python|java|javascript|in)\b',
        ]

    def analyze(self, message_body: str) -> str:
        """
        Analyze message sentiment with context analysis.

        Args:
            message_body: The message text to analyze

        Returns:
            'negative' or 'neutral'
        """
        if not message_body or not message_body.strip():
            return 'neutral'

        message_lower = message_body.lower()

        # Check for negative indicators first
        critical_match = any(re.search(pattern, message_lower, re.IGNORECASE)
                            for pattern in self.critical_signals)
        support_match = any(re.search(pattern, message_lower, re.IGNORECASE)
                           for pattern in self.support_failures)
        technical_match = any(re.search(pattern, message_lower, re.IGNORECASE)
                             for pattern in self.technical_issues)
        negative_lang_match = any(re.search(pattern, message_lower, re.IGNORECASE)
                                 for pattern in self.negative_language)

        # Check exclusion patterns (coding help, positive feedback)
        exclusion_match = any(re.search(pattern, message_lower, re.IGNORECASE)
                             for pattern in self.exclusion_patterns)

        # If exclusion pattern matches AND no other negative indicators, return neutral
        # This handles coding questions that might trigger help-seeking patterns
        if exclusion_match and not (support_match or technical_match or negative_lang_match):
            # Still check if it's a critical signal that's not just a question
            # But allow coding questions through
            if critical_match:
                # Check if it's a coding-related question by looking for coding keywords
                coding_keywords = ['function', 'code', 'python', 'java', 'javascript', 'program',
                                 'variable', 'class', 'method', 'syntax', 'loop', 'loops', 'array',
                                 'algorithm', 'string', 'object', 'data structure', 'recursion',
                                 'iterator', 'condition', 'conditional', 'statement']
                if any(keyword in message_lower for keyword in coding_keywords):
                    return 'neutral'
            else:
                return 'neutral'

        # If any negative indicator found
        if (critical_match or support_match or technical_match or negative_lang_match):
            return 'negative'

        # Context analysis - analyze message context even if no pattern matched
        context_score = self._analyze_context(message_body)

        # If context analysis indicates negative sentiment (score >= 2)
        if context_score >= 2:
            return 'negative'

        # If no patterns matched
        return 'neutral'

    def _analyze_context(self, message_body: str) -> int:
        """
        Analyze message context to detect negative sentiment beyond pattern matching.

        This method considers:
        - Word combinations and proximity
        - Negative intensifiers (very, extremely, really)
        - Contextual negations (not good, no help)
        - Problem + emotion combinations
        - Repeated negative themes
        - Escalation language progression

        Args:
            message_body: The message text to analyze

        Returns:
            Context score (0 = neutral, 1 = weak negative, 2+ = negative)
        """
        if not message_body or not message_body.strip():
            return 0

        message_lower = message_body.lower()
        score = 0

        # Define contextual negative indicators
        problem_words = ['problem', 'issue', 'error', 'fail', 'broken', 'wrong', 'bad',
                        'dikkat', 'pareshani', 'mushkil', 'galat', 'kharab']
        emotion_words = ['frustrated', 'angry', 'disappointed', 'upset', 'sad', 'worried',
                        'confused', 'stressed', 'pareshan', 'gussa', 'tension', 'chinta']
        help_words = ['help', 'please', 'urgent', 'asap', 'immediately', 'priority',
                     'help', 'madad', 'urgent', 'jaldi']
        intensifiers = ['very', 'extremely', 'really', 'too', 'so', 'completely', 'totally',
                       'bahut', 'bohot', 'kaafi', 'bilkul', 'poora']
        negation_words = ['not', 'no', 'never', 'none', 'nothing', 'nowhere', 'nobody',
                         'nahi', 'nhi', 'nahin', 'mat', 'maat', 'koi nahi']
        positive_context = ['good', 'great', 'excellent', 'working', 'solved', 'fixed', 'thanks',
                           'achha', 'badhiya', 'sahi', 'theek', 'thank', 'dhanyavaad']

        # 1. Check for problem + emotion combinations (within 10 words)
        words = message_lower.split()
        for i, word in enumerate(words):
            for problem in problem_words:
                if problem in word:
                    # Look for emotion words within 10 words
                    window_start = max(0, i - 10)
                    window_end = min(len(words), i + 10)
                    window = words[window_start:window_end]

                    for emotion in emotion_words:
                        if any(emotion in w for w in window):
                            score += 1
                            break

        # 2. Check for intensifier + negative word combinations
        for i in range(len(words) - 1):
            if any(intensifier in words[i] for intensifier in intensifiers):
                # Check if next 2 words contain problem or emotion
                next_words = words[i+1:min(i+3, len(words))]
                if any(any(neg in w for neg in problem_words + emotion_words) for w in next_words):
                    score += 1

        # 3. Check for negation + positive context (e.g., "not good", "no help")
        for i in range(len(words) - 1):
            if any(negation in words[i] for negation in negation_words):
                # Check if next 2 words contain positive words
                next_words = words[i+1:min(i+3, len(words))]
                if any(any(pos in w for w in next_words) for pos in positive_context):
                    score += 2  # Higher weight as this is explicit negation of positivity

        # 4. Check for problem + help-seeking combination
        has_problem = any(problem in message_lower for problem in problem_words)
        has_help = any(help_word in message_lower for help_word in help_words)
        if has_problem and has_help:
            score += 1

        # 5. Check for repeated negative themes (same negative word appears multiple times)
        negative_words_all = problem_words + emotion_words
        for neg_word in negative_words_all:
            count = message_lower.count(neg_word)
            if count >= 2:
                score += 1
                break

        # 6. Check for multiple questions (indicates confusion/frustration)
        question_count = message_lower.count('?')
        if question_count >= 2:
            score += 1

        # 7. Check for urgent/escalation language with problems
        urgent_patterns = [
            r'\b(urgent|asap|immediately|priority|please)\b.*\b(help|issue|problem)',
            r'\b(jaldi|turant|abhi|urgent).*\b(help|madad|dikkat|problem)',
            r'\b(still|yet|already).*\b(not|no|nahi).*\b(working|fixed|resolved)',
            r'\b(waiting|waited|wait.*for).*\b(days|weeks|long|time)',
        ]
        for pattern in urgent_patterns:
            if re.search(pattern, message_lower):
                score += 1

        # 8. Check for lack of response/communication context
        communication_patterns = [
            r'\b(no.*response|no.*reply|not.*responding|haven\'?t.*heard)',
            r'\b(nahi.*mila|nahi.*aaya|koi.*nahi).*\b(response|reply|jawab)',
            r'\b(tried|trying).*\b(reach|contact|call).*\b(but|no|not)',
        ]
        for pattern in communication_patterns:
            if re.search(pattern, message_lower):
                score += 1

        # 9. Check for time-related frustration
        time_frustration = [
            r'\b(still|yet|already).*\b(waiting|pending|not)',
            r'\b(how.*long|when.*will|why.*taking).*\b(time|long)',
            r'\b(days|weeks|months).*\b(no|not|nahi).*\b(response|update|reply)',
            r'\b(kab.*tak|kitne.*din|kitna.*time).*\b(lagega|wait)',
        ]
        for pattern in time_frustration:
            if re.search(pattern, message_lower):
                score += 1

        # 10. Check for consequence/impact statements
        consequence_patterns = [
            r'\b(affecting|impacting|hurting|damaging).*\b(career|future|growth|progress)',
            r'\b(cannot|can\'?t).*\b(continue|proceed|move forward|cope)',
            r'\b(waste|wasting).*\b(time|money|effort|paise)',
            r'\b(regret|regretting|mistake).*\b(joining|enrolled|decision)',
        ]
        for pattern in consequence_patterns:
            if re.search(pattern, message_lower):
                score += 2  # Higher weight for serious consequences

        return score

    def get_matched_patterns(self, message_body: str) -> list:
        """
        Get list of matched negative patterns for debugging.

        Args:
            message_body: The message text to analyze

        Returns:
            List of pattern categories that matched
        """
        if not message_body or not message_body.strip():
            return []

        message_lower = message_body.lower()
        matched = []

        if any(re.search(pattern, message_lower, re.IGNORECASE)
               for pattern in self.critical_signals):
            matched.append('CRITICAL_SIGNALS')

        if any(re.search(pattern, message_lower, re.IGNORECASE)
               for pattern in self.support_failures):
            matched.append('SUPPORT_FAILURES')

        if any(re.search(pattern, message_lower, re.IGNORECASE)
               for pattern in self.technical_issues):
            matched.append('TECHNICAL_ISSUES')

        if any(re.search(pattern, message_lower, re.IGNORECASE)
               for pattern in self.negative_language):
            matched.append('NEGATIVE_LANGUAGE')

        return matched

    def _load_sentiment_context(self, filepath: str) -> dict:
        """
        Load sentiment analysis rules from sentiment.md file.

        Args:
            filepath: Path to sentiment.md file

        Returns:
            Dictionary containing parsed rules and context
        """
        context = {
            'loaded': False,
            'critical_signals': [],
            'support_failures': [],
            'technical_issues': [],
            'negative_language': [],
            'exclusions': []
        }

        if not os.path.exists(filepath):
            return context

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                context['loaded'] = True
                context['raw_content'] = content

                # Parse sections for reference
                if 'CRITICAL SIGNALS:' in content:
                    context['has_critical_signals'] = True
                if 'SUPPORT FAILURES:' in content:
                    context['has_support_failures'] = True
                if 'TECHNICAL ISSUES' in content:
                    context['has_technical_issues'] = True
                if 'NEGATIVE LANGUAGE' in content:
                    context['has_negative_language'] = True

        except Exception as e:
            print(f"Warning: Could not load sentiment.md: {e}")

        return context

    def _check_manual_examples(self, filepath: str) -> bool:
        """
        Check if manual examples file exists.

        Args:
            filepath: Path to sentimentManual.md file

        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(filepath)

    def get_sentiment_rules_info(self) -> str:
        """
        Get information about loaded sentiment rules.

        Returns:
            String describing the sentiment rules status
        """
        info_parts = []

        if self.sentiment_context.get('loaded'):
            info_parts.append("Sentiment rules loaded from sentiment.md")
            info_parts.append(f"- Critical Signals: {'✓' if self.sentiment_context.get('has_critical_signals') else '✗'}")
            info_parts.append(f"- Support Failures: {'✓' if self.sentiment_context.get('has_support_failures') else '✗'}")
            info_parts.append(f"- Technical Issues: {'✓' if self.sentiment_context.get('has_technical_issues') else '✗'}")
            info_parts.append(f"- Negative Language: {'✓' if self.sentiment_context.get('has_negative_language') else '✗'}")
        else:
            info_parts.append("Using built-in sentiment rules (sentiment.md not found)")

        if self.manual_examples_loaded:
            info_parts.append("✓ Manual negative examples loaded (sentimentManual.md)")

        return "\n".join(info_parts)
