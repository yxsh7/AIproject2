"""Prompt templates for AI analysis agents"""

CODE_COMPLEXITY_PROMPT = """You are an expert software engineer analyzing code commits for complexity and quality.

Analyze the following git commit:

**Commit Message:**
{commit_message}

**Files Changed:** {files_changed}
**Additions:** {additions}
**Deletions:** {deletions}

**Code Diff:**
{diff}

Please analyze this commit and provide:

1. **Complexity Score (0-10)**: How cognitively complex is this change?
   - 1-3: Simple (typo fixes, config changes, trivial updates)
   - 4-6: Moderate (feature additions, bug fixes, refactoring)
   - 7-9: High (architectural changes, complex algorithms, system redesign)
   - 10: Very High (major system overhauls, critical infrastructure)

2. **Quality Score (0-10)**: Code quality assessment
   - Best practices adherence
   - Code organization
   - Potential issues or tech debt

3. **Impact Level**: low, medium, high, critical
   - Consider: core vs peripheral systems, user-facing vs internal

4. **Work Type**: refactoring, feature, bug_fix, documentation, testing, config, other

5. **Technical Debt Delta**: Did this ADD (+) or REMOVE (-) technical debt? (integer, e.g., +5 or -10)

6. **Affected Systems**: List of systems/modules affected

7. **Novelty**: routine, moderate, high
   - Is this boilerplate/repetitive or novel problem-solving?

8. **Explanation**: 2-3 sentence explanation of the change and why you scored it this way

Respond in JSON format:
```json
{{
  "complexity_score": <0-10>,
  "quality_score": <0-10>,
  "impact_level": "<low|medium|high|critical>",
  "work_type": "<type>",
  "technical_debt_delta": <integer>,
  "affected_systems": ["system1", "system2"],
  "novelty": "<routine|moderate|high>",
  "explanation": "<explanation>"
}}
```
"""

WORK_TYPE_CLASSIFIER_PROMPT = """You are an expert at understanding engineering work from Jira tickets.

Analyze the following Jira ticket:

**Ticket Key:** {ticket_key}
**Title:** {title}
**Type:** {ticket_type}
**Description:**
{description}

**Comments:**
{comments}

**Status:** {status}

Please classify this work and provide:

1. **Primary Work Type**:
   - code: Writing production code
   - research: Technology evaluation, investigation, exploration
   - documentation: Writing docs, diagrams, guides
   - dashboard: Creating analytics dashboards, reports
   - meeting: Meeting-heavy coordination work
   - mentoring: Helping other developers, pair programming
   - operations: Deployment, infrastructure, maintenance
   - design: System design, architecture planning
   - testing: Writing tests, QA work
   - bug_fix: Fixing bugs
   - other: Anything else

2. **Complexity Score (0-10)**: How complex is this work?
   - Consider: technical difficulty, unknowns, scope

3. **Impact Score (0-10)**: Business and technical impact
   - Consider: user impact, system criticality, strategic value

4. **Time Estimate (hours)**: How many hours does this likely take?

5. **Artifacts**: List of concrete outputs expected
   - Examples: "Code PR", "Research document", "Dashboard link", "Architecture diagram"

6. **Explanation**: 2-3 sentences explaining your classification

Respond in JSON format:
```json
{{
  "work_type": "<type>",
  "sub_type": "<optional sub-classification>",
  "complexity_score": <0-10>,
  "impact_score": <0-10>,
  "time_estimate_hours": <number>,
  "artifacts": [
    {{"type": "<artifact_type>", "description": "<description>"}}
  ],
  "explanation": "<explanation>"
}}
```
"""

COLLABORATION_ANALYZER_PROMPT = """You are an expert at analyzing developer collaboration and mentoring.

Analyze the following code review:

**Pull Request Title:** {pr_title}
**Pull Request Description:** {pr_description}

**Review Comments:** {review_comments}
**Number of Comments:** {comment_count}
**Review State:** {review_state}

Please analyze this code review and provide:

1. **Review Quality (0-10)**: How helpful and thorough is this review?
   - 1-3: Minimal (just "LGTM", no substance)
   - 4-6: Adequate (some useful feedback)
   - 7-9: Excellent (detailed, educational, catches issues)
   - 10: Outstanding (comprehensive security/architecture insights)

2. **Mentoring Detected**: true/false
   - Does the review provide explanations and learning opportunities?

3. **Security Issues Found**: Number of security-related comments

4. **Architecture Feedback**: true/false
   - Does the review provide high-level design feedback?

5. **Code Quality Feedback**: true/false
   - Does the review address code style, patterns, best practices?

6. **Helpfulness**: minimal, moderate, high, exceptional

7. **Explanation**: 2-3 sentences about the review quality

Respond in JSON format:
```json
{{
  "quality_score": <0-10>,
  "mentoring_detected": <true|false>,
  "security_issues_found": <number>,
  "architecture_feedback": <true|false>,
  "code_quality_feedback": <true|false>,
  "helpfulness": "<minimal|moderate|high|exceptional>",
  "explanation": "<explanation>"
}}
```
"""

IMPACT_SCORER_PROMPT = """You are an expert at assessing the business and technical impact of engineering work.

Analyze the following work activity:

**Work Summary:** {work_summary}
**Work Type:** {work_type}
**System Context:** {system_context}

Please assess the impact and provide:

1. **Impact Score (0-10)**: Overall impact
   - 1-3: Low (internal tooling, minor improvements)
   - 4-6: Medium (team productivity, moderate user impact)
   - 7-9: High (significant user value, critical systems)
   - 10: Critical (major releases, system-wide impact)

2. **Impact Areas**: List applicable areas
   - reliability, performance, security, usability, cost_savings, developer_productivity, customer_experience

3. **Affected Users**: estimate or description
   - Examples: "All users", "10K+ users", "Internal team", "5 developers"

4. **Business Value**: low, medium, high, critical

5. **Strategic Alignment**: How well does this align with company goals?
   - routine, aligned, strategic, transformational

6. **Explanation**: 2-3 sentences justifying the impact score

Respond in JSON format:
```json
{{
  "impact_score": <0-10>,
  "impact_areas": ["area1", "area2"],
  "affected_users": "<description>",
  "business_value": "<low|medium|high|critical>",
  "strategic_alignment": "<routine|aligned|strategic|transformational>",
  "explanation": "<explanation>"
}}
```
"""

INSIGHT_GENERATION_PROMPT = """You are an AI engineering manager assistant. Generate actionable insights from productivity data.

**Developer:** {developer_name} ({role_level})
**Time Period:** {period}

**Productivity Data:**
- Overall Score: {overall_score}/100
- Code Quality: {code_quality}/100
- Complexity: {complexity}/100
- Impact: {impact}/100
- Collaboration: {collaboration}/100

**Work Breakdown:**
{work_breakdown}

**Recent Activities:**
{recent_activities}

**Trends:**
{trends}

Generate insights including:

1. **Strengths**: What is the developer doing well? (2-3 bullet points)

2. **Observations**: Notable patterns or changes (2-3 bullet points)
   - Examples: "Working late nights frequently", "High context switching", "Consistent delivery"

3. **Suggestions**: Actionable recommendations (2-3 bullet points)
   - For developer and/or manager

4. **Alerts**: Any concerning patterns that need attention
   - Examples: burnout risk, performance drop, workload imbalance

5. **Opportunities**: Growth or improvement opportunities

Respond in JSON format:
```json
{{
  "strengths": ["strength1", "strength2"],
  "observations": ["observation1", "observation2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "alerts": [
    {{"type": "<alert_type>", "description": "<description>", "priority": "<low|medium|high>"}}
  ],
  "opportunities": ["opportunity1", "opportunity2"]
}}
```
"""
