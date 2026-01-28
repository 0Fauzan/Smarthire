# services/ats_scorer.py (CREATE THIS NEW FILE)
import re
import os
from anthropic import Anthropic

class ATSScorer:
    """
    ATS (Applicant Tracking System) Scoring Engine
    Analyzes resumes and provides actionable feedback
    """
    
    def __init__(self):
        # Initialize Claude AI client
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if api_key:
            self.client = Anthropic(api_key=api_key)
            self.use_ai = True
        else:
            self.use_ai = False
            print("Warning: ANTHROPIC_API_KEY not set. Using basic scoring only.")
        
        # Common ATS keywords by role
        self.keyword_database = {
            'software_engineer': [
                'python', 'java', 'javascript', 'typescript', 'react', 'node',
                'api', 'rest', 'database', 'sql', 'nosql', 'mongodb',
                'git', 'github', 'agile', 'scrum', 'docker', 'kubernetes',
                'aws', 'cloud', 'ci/cd', 'testing', 'unit test'
            ],
            'data_scientist': [
                'python', 'r', 'sql', 'machine learning', 'deep learning',
                'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
                'data analysis', 'statistics', 'visualization', 'tableau',
                'big data', 'spark', 'hadoop'
            ],
            'product_manager': [
                'roadmap', 'stakeholder', 'user research', 'analytics',
                'metrics', 'kpi', 'agile', 'scrum', 'jira',
                'product strategy', 'market research', 'a/b testing',
                'user experience', 'prioritization'
            ],
            'general': [
                'leadership', 'teamwork', 'communication', 'problem solving',
                'project management', 'collaboration', 'strategic thinking'
            ]
        }
    
    def calculate_ats_score(self, resume_text, parsed_sections):
        """
        Main scoring function
        Returns: {score, breakdown, issues, suggestions}
        """
        # Calculate individual scores
        keyword_score = self._score_keywords(resume_text, parsed_sections)
        formatting_score = self._score_formatting(resume_text, parsed_sections)
        completeness_score = self._score_completeness(parsed_sections)
        length_score = self._score_length(resume_text)
        
        # Weighted average (total = 100)
        total_score = (
            keyword_score * 0.40 +      # 40% - Most important
            formatting_score * 0.25 +    # 25% - ATS readability
            completeness_score * 0.25 +  # 25% - All sections present
            length_score * 0.10          # 10% - Appropriate length
        )
        
        # Identify specific issues
        issues = self._identify_issues(
            keyword_score, formatting_score, 
            completeness_score, length_score, 
            parsed_sections
        )
        
        # Generate actionable suggestions
        suggestions = self._generate_suggestions(issues)
        
        # Get AI enhancement if available
        if self.use_ai:
            ai_feedback = self._get_ai_feedback(resume_text, total_score, issues)
        else:
            ai_feedback = None
        
        return {
            'score': round(total_score),
            'breakdown': {
                'keywords': round(keyword_score),
                'formatting': round(formatting_score),
                'completeness': round(completeness_score),
                'length': round(length_score)
            },
            'issues': issues,
            'suggestions': suggestions,
            'ai_feedback': ai_feedback
        }
    
    def _score_keywords(self, text, sections):
        """Score keyword relevance (0-100)"""
        text_lower = text.lower()
        
        # Detect role from resume
        role = self._detect_role(text_lower)
        relevant_keywords = self.keyword_database.get(role, []) + self.keyword_database['general']
        
        # Count found keywords
        found_keywords = sum(1 for kw in relevant_keywords if kw in text_lower)
        
        if not relevant_keywords:
            return 70  # Neutral if role unclear
        
        keyword_ratio = found_keywords / len(relevant_keywords)
        score = min(100, int(keyword_ratio * 100 * 1.3))  # Slight boost
        
        return max(30, score)  # Minimum 30
    
    def _score_formatting(self, text, sections):
        """Score formatting quality (0-100)"""
        score = 100
        
        # Check section separation
        if len(text.split('\n\n')) < 3:
            score -= 15
        
        # Check for consistent date formatting
        date_patterns = re.findall(r'\b\d{4}\b|\b\d{2}/\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b', text)
        if len(set([len(d) for d in date_patterns])) > 2:
            score -= 10
        
        # Check for excessive special characters
        special_chars = len(re.findall(r'[★•●◆◇▪▫]', text))
        if special_chars > 20:
            score -= 10
        
        # Check for proper capitalization
        lines = text.split('\n')
        lowercase_headers = sum(1 for line in lines[:10] if line and line[0].islower())
        if lowercase_headers > 3:
            score -= 10
        
        return max(40, score)
    
    def _score_completeness(self, sections):
        """Score section completeness (0-100)"""
        required_sections = ['contact', 'experience', 'education', 'skills']
        found_sections = sum(1 for s in required_sections if sections.get(s))
        
        completeness_ratio = found_sections / len(required_sections)
        return int(completeness_ratio * 100)
    
    def _score_length(self, text):
        """Score resume length (0-100)"""
        word_count = len(text.split())
        
        if 400 <= word_count <= 800:  # 1-2 pages ideal
            return 100
        elif word_count < 300:
            return 60  # Too short
        elif word_count > 1200:
            return 70  # Too long
        else:
            return 85
    
    def _detect_role(self, text_lower):
        """Detect likely role from resume content"""
        role_keywords = {
            'software_engineer': ['software', 'developer', 'engineer', 'programming'],
            'data_scientist': ['data', 'scientist', 'analytics', 'machine learning'],
            'product_manager': ['product', 'manager', 'roadmap', 'strategy']
        }
        
        role_scores = {}
        for role, keywords in role_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            role_scores[role] = score
        
        # Return role with highest score, or 'general' if none match
        if max(role_scores.values()) == 0:
            return 'general'
        
        return max(role_scores, key=role_scores.get)
    
    def _identify_issues(self, kw_score, fmt_score, comp_score, len_score, sections):
        """Identify specific fixable issues"""
        issues = []
        
        if kw_score < 70:
            issues.append({
                'type': 'keywords',
                'severity': 'high',
                'message': 'Missing industry-relevant keywords',
                'icon': '❌'
            })
        
        if fmt_score < 75:
            issues.append({
                'type': 'formatting',
                'severity': 'medium',
                'message': 'Inconsistent formatting detected',
                'icon': '⚠️'
            })
        
        if comp_score < 75:
            missing = []
            if not sections.get('skills'):
                missing.append('Skills')
            if not sections.get('experience'):
                missing.append('Experience')
            if not sections.get('education'):
                missing.append('Education')
            
            if missing:
                issues.append({
                    'type': 'completeness',
                    'severity': 'high',
                    'message': f'Missing sections: {", ".join(missing)}',
                    'icon': '❌'
                })
        
        if len_score < 80:
            word_count = len(sections.get('original_text', '').split()) if 'original_text' in sections else 0
            if word_count < 400:
                issues.append({
                    'type': 'length',
                    'severity': 'medium',
                    'message': 'Resume is too short (under 1 page)',
                    'icon': '⚠️'
                })
            elif word_count > 1200:
                issues.append({
                    'type': 'length',
                    'severity': 'low',
                    'message': 'Resume is too long (over 2 pages)',
                    'icon': 'ℹ️'
                })
        
        return issues
    
    def _generate_suggestions(self, issues):
        """Generate actionable improvement suggestions"""
        suggestions = []
        
        for issue in issues:
            if issue['type'] == 'keywords':
                suggestions.append("Add relevant technical keywords like 'API development', 'cloud computing', 'agile methodologies'")
            elif issue['type'] == 'formatting':
                suggestions.append("Use consistent date format throughout (e.g., 'Jan 2023 - Present')")
            elif issue['type'] == 'completeness':
                suggestions.append(f"Add missing section: {issue['message'].split(': ')[1]}")
            elif issue['type'] == 'length':
                if 'short' in issue['message']:
                    suggestions.append("Expand experience descriptions with specific achievements and metrics")
                else:
                    suggestions.append("Condense content to 1-2 pages by removing redundant information")
        
        return suggestions
    
    def _get_ai_feedback(self, resume_text, score, issues):
        """Get additional AI-powered feedback"""
        if not self.use_ai:
            return None
        
        try:
            prompt = f"""Analyze this resume and provide brief, actionable feedback.

Resume Text:
{resume_text[:2000]}  # First 2000 chars

Current ATS Score: {score}/100

Issues Found:
{chr(10).join([f"- {issue['message']}" for issue in issues])}

Provide:
1. One key strength
2. Top improvement priority
3. One specific example of how to improve

Keep response under 150 words."""

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
        
        except Exception as e:
            print(f"AI feedback error: {e}")
            return None
