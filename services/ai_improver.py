import os
from anthropic import Anthropic

class AIResumeImprover:
    """
    Uses Claude AI to rewrite resumes for better ATS scores
    This is SmartHire's KEY DIFFERENTIATOR
    """
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not configured. Cannot improve resumes.")
        
        self.client = Anthropic(api_key=api_key)
    
    def improve_resume(self, original_text, ats_feedback, current_score):
        """
        Main improvement function
        Returns: {improved_text, changes_made}
        """
        
        # Build improvement prompt
        issues_text = "\n".join([
            f"- {issue['message']} (Severity: {issue['severity']})"
            for issue in ats_feedback.get('issues', [])
        ])
        
        suggestions_text = "\n".join([
            f"- {suggestion}"
            for suggestion in ats_feedback.get('suggestions', [])
        ])
        
        prompt = f"""You are an expert resume writer and ATS optimization specialist.

ORIGINAL RESUME:
{original_text}

CURRENT ATS SCORE: {current_score}/100
GOAL: Achieve 85+ ATS score

IDENTIFIED ISSUES:
{issues_text}

IMPROVEMENT SUGGESTIONS:
{suggestions_text}

TASK: Rewrite this resume to achieve an ATS score of 85+. Follow these rules:

1. KEYWORDS: Add relevant industry keywords naturally (don't stuff)
2. FORMATTING: Fix any formatting inconsistencies
3. COMPLETENESS: Ensure all sections are present and well-structured
4. CLARITY: Make achievements specific and quantifiable
5. LENGTH: Keep to 1-2 pages (400-800 words)
6. TRUTHFULNESS: Only enhance phrasing, DO NOT fabricate experience

STRUCTURE TO FOLLOW:
[Contact Information]
[Professional Summary - 2-3 sentences]
[Work Experience - with bullet points using STAR method]
[Education]
[Technical Skills - as comma-separated list]
[Projects - if applicable]

IMPORTANT:
- Use consistent date format (e.g., "Jan 2023 - Present")
- Start bullet points with strong action verbs (Built, Developed, Led)
- Add metrics where possible ("improved by 40%", "managed team of 5")
- Keep professional tone
- Preserve all factual information from original

Return ONLY the improved resume text, properly formatted and ready to use."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            improved_text = message.content[0].text.strip()
            
            # Analyze changes made
            changes_made = self._analyze_changes(original_text, improved_text, ats_feedback)
            
            return {
                "improved_text": improved_text,
                "changes_made": changes_made
            }
            
        except Exception as e:
            raise Exception(f"AI improvement failed: {str(e)}")
    
    def _analyze_changes(self, original, improved, ats_feedback):
        """
        Identify what was changed
        """
        changes = []
        
        # Check if keywords were added
        original_lower = original.lower()
        improved_lower = improved.lower()
        
        # Common keywords to check
        tech_keywords = ['python', 'java', 'javascript', 'react', 'api', 'sql', 'cloud', 'agile']
        added_keywords = [kw for kw in tech_keywords if kw not in original_lower and kw in improved_lower]
        
        if added_keywords:
            changes.append(f"Added technical keywords: {', '.join(added_keywords)}")
        
        # Check if structure improved
        if 'completeness' in str(ats_feedback.get('issues', [])):
            changes.append("Added missing resume sections")
        
        # Check if formatting improved
        if 'formatting' in str(ats_feedback.get('issues', [])):
            changes.append("Fixed date formatting and consistency")
        
        # Check length changes
        original_words = len(original.split())
        improved_words = len(improved.split())
        word_diff = improved_words - original_words
        
        if abs(word_diff) > 50:
            if word_diff > 0:
                changes.append(f"Expanded content (+{word_diff} words)")
            else:
                changes.append(f"Condensed content ({word_diff} words)")
        
        # Generic improvements
        changes.append("Enhanced action verbs and professional phrasing")
        changes.append("Improved bullet point structure")
        
        return changes
    
    def quick_improve(self, original_text):
        """
        Quick improvement without full ATS analysis
        Useful for "Try AI Improvement" demo
        """
        prompt = f"""Quickly improve this resume for ATS systems. Focus on:
1. Adding relevant technical keywords
2. Fixing formatting
3. Using strong action verbs

Original Resume:
{original_text[:1500]}

Return improved version (keep it concise):"""

        try:
            message = self.client.messages.create(
                model="claude-haiku-4-20250514",  # Faster, cheaper model
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Quick improvement failed: {str(e)}")
