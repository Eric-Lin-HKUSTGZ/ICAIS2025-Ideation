PROMPT_TEMPLATES = {
    "retrieve_query": """You are an expert at extracting keywords from user queries. 
Below, I will provide you with a user query in which the user expresses interest in developing a new research proposal. Your task is to extract up to four keywords that best capture the core research topic or methodology of interest to the user.

Each keyword must be:

1. A noun (or noun phrase),
2. Written in lowercase English,
3. Representative of the central concept or approach in the query.

Here is the user query:
User Query: {user_query}

Please output one to four keywords (1-4 keywords)—no more, no less—each as a lowercase English noun, separated by a comma and without any additional text, punctuation, or formatting.
""",
    
    "expand_background": """You are an expert at expanding brief research queries into detailed research backgrounds.

Task: Expand the following brief research query into a comprehensive research background suitable for an undergraduate student to understand.

Brief Query: {brief_background}
Keywords: {keywords}

Please provide a detailed research background (200-500 words) in Markdown format that:
1. Explains the research problem clearly
2. Provides context and motivation
3. Describes the importance of the research area
4. Uses clear and accessible language

Output your response in Markdown format.

Research Background:
""",
    
    "generate_brainstorm": """You are a researcher in the field of AI with innovative and pioneering abilities. You are good at generating creative and original ideas.

### Task Description:
You are an AI researcher tasked with brainstorming initial, innovative ideas to address a given research problem in AI. Focus on generating diverse and creative approaches. The ideas should cover a range of possible directions that could be explored further.

### Information Provided:
- **Research Background**: {background}

### Approach:
Your brainstorming should be systematic:
- **Step 1**: Thoroughly understand the research background.
- **Step 2**: Generate a list of 3 to 4 high-level ideas or directions that could potentially solve problems in the given background. Be creative, think outside the box, and avoid merely rephrasing existing methods.

### Format for Your Response:
Output your response in Markdown format. Please present 3 to 4 ideas in the following format:
**Idea 1**: [Brief description of the first idea]
**Idea 2**: [Brief description of the second idea]
**Idea 3**: [Brief description of the third idea]
**Idea 4**: [Brief description of the fourth idea]
""",
    
    "generate_paper_inspiration": """You are a professional research paper analyst skilled at drawing creative inspiration from academic literature.

Task: Analyze the following research paper and generate a novel research inspiration based on it, considering the research background.

Research Background: {background}

Paper Information:
Title: {title}
Abstract: {abstract}

Please generate a concise research inspiration (2-3 sentences) in Markdown format that:
1. Identifies a novel insight or opportunity from this paper
2. Connects it to the research background
3. Suggests a potential research direction

Output your response in Markdown format.

Inspiration:
""",
    
    "generate_global_inspiration": """You are a professional research paper analyst skilled at drawing creative inspiration from academic literature. 
Below, I will provide a user query along with a set of related papers, including the latest, highly cited, and relevant works. Your task is to synthesize these papers holistically and propose one novel research inspiration that directly addresses the user's query.

Here is the information provided:
User Query: {user_query}
Related Papers: {paper}

Please synthesize these papers holistically—without analyzing each one individually—and propose one novel research inspiration that directly addresses the user's query. The inspiration should emerge from a deep understanding of the underlying assumptions, gaps, or unexplored opportunities in the existing literature, not merely by combining existing methods. Prioritize conceptual insight and originality over technical aggregation, and ensure the proposal is both innovative and closely aligned with the user's needs. Focus on delivering a concise, imaginative spark rooted in genuine scholarly insight.

Output your response in Markdown format.
""",
    
    "generate_ideas_from_inspirations": """You are an experienced AI researcher. Based on multiple research inspirations, generate innovative research ideas.

User Query: {user_query}
Research Background: {background}

Inspirations:
{inspirations}

IMPORTANT REQUIREMENTS:
- The generated ideas MUST be highly relevant to the user's query and application scenario
- Each idea should directly address the specific problem or domain mentioned in the user query
- The application scenario of each idea must align with the user's research interest
- Do NOT generate generic ideas that could apply to any field - they must be tailored to the user's specific query

Please generate exactly 3 research ideas based on these inspirations. Each idea should be innovative, address the research background, and be highly relevant to the user's query.

Format your response as:
**Idea 1**: [Description of the first idea]
**Idea 2**: [Description of the second idea]
**Idea 3**: [Description of the third idea]
""",
    
    "generate_idea_from_inspiration": """You are an experienced AI researcher. Based on a research inspiration, generate innovative research ideas.

User Query: {user_query}
Research Background: {background}

Inspiration: {inspiration}

IMPORTANT REQUIREMENTS:
- The generated ideas MUST be highly relevant to the user's query and application scenario
- Each idea should directly address the specific problem or domain mentioned in the user query
- The application scenario of each idea must align with the user's research interest
- Do NOT generate generic ideas that could apply to any field - they must be tailored to the user's specific query

Please generate 2-3 research ideas based on this inspiration. Each idea should be innovative, address the research background, and be highly relevant to the user's query.

Format your response as:
**Idea 1**: [Description of the first idea]
**Idea 2**: [Description of the second idea]
...
""",
    
    "integrate_with_brainstorm": """You are a researcher in the field of AI with innovative and pioneering abilities. You are good at generating innovative and original ideas to solve cutting-edge problems in the field of AI.

Task Description: 
You will be provided with research background information along with a set of ideas you generated previously from the related paper information, and a set of brainstorming ideas concerning the same research topic. Your task is to combine these ideas and generate new ones, the new ideas you generate should base on the ideas you generated previously, and integrate creative parts of the brainstorming ideas. Consider the background thoroughly, taking into account the novelty and practicability of each idea. If you think an idea you generate is reasonable and valuable, feel free to retain it. 

### Information Provided:
1. **User Query**: The user's specific research interest and application scenario.
2. **Research Background**: The starting point for idea generation based on the research context.
3. **Brainstorming Ideas**: These ideas were generated purely from the research background, focusing on innovation and may not be directly related to the problem.
4. **Generated Ideas**: These are the ideas you previously generated by considering both the research background and related papers.

### Approach:
- **Step 1**: Review the user query to understand the specific application scenario and research interest.
- **Step 2**: Review the research background and original ideas to understand the foundation of the problem.
- **Step 3**: Consider the brainstorming ideas and original ideas together. Combine, improve, or expand upon them, integrating insights from the related papers.
- **Step 4**: Propose new ideas that are innovative and practical, ensuring they align with the research background AND are highly relevant to the user's query and application scenario.

IMPORTANT REQUIREMENTS:
- The final integrated ideas MUST be highly relevant to the user's query and application scenario
- Each idea should directly address the specific problem or domain mentioned in the user query
- The application scenario of each idea must align with the user's research interest
- Do NOT generate generic ideas that could apply to any field - they must be tailored to the user's specific query

### Specific Information:
1. **User Query**: {user_query}
2. **Research Background**: {background}
3. **Brainstorming Ideas**: {brainstorm}
4. **Generated Ideas**: {ideas}

### Format for Your Response:
Please ensure that your final ideas include exactly 3 entries and present the integrated ideas in the following format:
**Idea 1**: [The first method idea]
**Idea 2**: [The second method idea]
**Idea 3**: [The third method idea]

CRITICAL FORMAT REQUIREMENTS:
- Each idea should be a concise title or brief description (1-2 sentences maximum)
- Do NOT include detailed subsections like "核心理念" (Core Concept), "针对性" (Targeted Application), etc.
- Each idea should be separated clearly, with each **Idea X**: on a new line or clearly separated
- Keep the format simple and consistent: **Idea 1**: [brief description], **Idea 2**: [brief description], **Idea 3**: [brief description]
""",
    
    "critic_idea": """You are a rigorous research idea reviewer.

Task: Conduct a critical evaluation of the following research idea.

Research Background: {background}
Related Papers Summary: {papers_summary}
Idea: {idea}

Please identify key weaknesses such as:
1. High overlap with existing literature
2. Lack of genuine novelty
3. Insufficient feasibility
4. Misalignment with the research background

Provide clear, concrete, and actionable suggestions for improvement.

Critical Evaluation:
""",
    
    "refine_idea": """You are a professional research idea optimizer.

Task: Refine the following research idea based on the critical evaluation.

Research Background: {background}
Original Idea: {idea}
Critical Evaluation: {criticism}

Please revise the idea to address the identified issues while maintaining innovation and feasibility.

Refined Idea:
""",
    
    "evaluate_idea": """You are an expert at evaluating research ideas.

Task: Evaluate the following research idea on two dimensions: feasibility and novelty.

Research Background: {background}
Idea: {idea}

Please provide scores (0-5) for:
1. Feasibility: How practical and implementable is this idea?
2. Novelty: How innovative and original is this idea?

IMPORTANT SCORING REQUIREMENTS:
- Scores must be precise to one decimal place (e.g., 4.2, 3.7, 4.8, not 4, 3, or 5)
- Use the full range of 0.0 to 5.0 to distinguish between different ideas
- Be precise and differentiate: similar ideas should have slightly different scores
- Avoid giving the same score to different ideas

Format your response as:
Feasibility: [score with one decimal place]/5
Novelty: [score with one decimal place]/5
Total: [total_score with one decimal place]/10

Example format:
Feasibility: 4.2/5
Novelty: 4.5/5
Total: 8.7/10

Brief justification:
[Brief explanation of the scores]
""",
    
    "generate_research_plan": """You are an experienced research proposal writer. 
Below, I will provide you with a user query, a set of related academic papers(including the latest, highly cited, and relevant works) and a novel research inspiration derived from a deep analysis of these papers. You are tasked with drafting a complete research proposal based on this information.

Here is the information provided:
User Query: {user_query}
Related Papers: {paper}
Inspiration: {inspiration}
Best Idea: {best_idea}

CRITICAL REQUIREMENT - BEST IDEA ALIGNMENT:
- The research proposal MUST be strictly based on the provided "Best Idea"
- The proposal title, methodology, and all technical details MUST align with the Best Idea
- Do NOT deviate from, modify, or replace the Best Idea with a different approach
- The Best Idea is the core of the research proposal - all sections must support and elaborate on this specific idea
- If the Best Idea mentions specific techniques, methods, or frameworks, the proposal must detail how these will be implemented

CRITICAL REQUIREMENT - PAPER CITATION FORMAT:
- When referencing papers in the proposal body, use numbered citations in square brackets (e.g., [1], [2], [3])
- Citation numbers MUST be assigned sequentially starting from [1] based on the order papers are FIRST mentioned in the proposal body
- Citation numbers MUST be continuous (1, 2, 3, 4, 5...), with NO gaps or skipped numbers
- DO NOT use generic references like "论文1" (Paper 1), "论文2" (Paper 2), or "论文X" (Paper X) in the body text
- At the end of the proposal, include a "References" section (or "参考文献" in Chinese) that lists all cited papers with their full titles
- Format references as: [1] [Full Paper Title], [2] [Full Paper Title], [3] [Full Paper Title], etc.
- References MUST be numbered sequentially from [1] to [N] with NO gaps, matching the citation numbers used in the body text
- Only include papers that are actually cited in the proposal body

Based on this information, please draft a complete research proposal that fulfills the following requirements:

1. The proposal must be grounded in the provided research inspiration and best idea—do not deviate from or replace them.
2. The proposal MUST strictly follow and elaborate on the Best Idea provided above.
3. If the user specifies particular sections or components the proposal should include, follow those instructions exactly.
4. If no specific structure is given, organize the proposal into the following sections:
   • Research Background – contextualize the problem and summarize key findings from the related literature (use numbered citations [1], [2], etc.),
   • Limitations of Current Work – identify critical gaps or shortcomings in existing approaches (use numbered citations [1], [2], etc.),
   • Proposed Research Plan – detail the novel idea (the Best Idea), methodology, and how it addresses the user's query and overcomes prior limitations,
   • References – list all cited papers with their full titles in the format: [1] [Full Paper Title], [2] [Full Paper Title], etc.

IMPORTANT OUTPUT FORMAT REQUIREMENTS:
- Output your response in Markdown format.
- Start directly with the research proposal content. Do NOT include any introductory phrases such as "Of course", "Certainly", "I have thoroughly revised", "Based on", "According to", etc.
- Do NOT include any meta-commentary about the writing process (e.g., "I have revised", "I will now", "Let me").
- Do NOT include any file names, metadata, or irrelevant content (e.g., "refined_idea_zh.md", file paths, etc.)
- Output ONLY the research proposal content itself, beginning with the first section title (e.g., "# Research Title" or "# 研究标题").
- Use numbered citations [1], [2], [3], etc. in the body text when referencing papers. Citations MUST be numbered sequentially from [1] with NO gaps.
- Include a References section at the end with full paper titles, numbered sequentially from [1] to [N] with NO gaps.
- Ensure the proposal is coherent, technically sound, and directly aligned with both the user's needs and the provided inspiration.
""",
    
    "critic_research_plan": """You are a rigorous research proposal reviewer. 
Below, I will provide you with a user query, a set of related academic papers(including the latest, highly cited, and relevant works), a novel research inspiration derived from a deep analysis of these papers and a preliminary research proposal based on this inspiration. You are tasked with conducting a strict and critical evaluation of the proposal. 

Here is the information provided:
User Query: {user_query}
Related Papers: {paper}
Inspiration: {inspiration}
Preliminary Research Proposal: {research_plan}

Please conduct a strict and critical evaluation of the proposal. Identify its key weaknesses—such as high overlap with existing literature, lack of genuine novelty (e.g., merely combining existing methods without deeper insight), insufficient alignment with the stated inspiration, or failure to address core gaps in the field.
In addition to diagnosing these issues, provide clear, concrete, and actionable suggestions for how the proposal can be revised to enhance its originality, rigor, and relevance to the user's query.
""",
    
    "refine_research_plan": """You are a professional research proposal optimizer. 
Below, I will provide you with a user query, a preliminary research proposal, a critical evaluation of the proposal and a clear revision suggestion. You are tasked with thoroughly revising the research proposal based on the feedback provided.

Here is the information provided:
User Query: {user_query}
Preliminary Research Proposal: {research_plan}
Critical evaluation of the proposal and clear revision suggestion: {criticism}

CRITICAL REQUIREMENT - BEST IDEA CONSISTENCY:
- The revised research proposal MUST maintain consistency with the Best Idea that was used to generate the preliminary proposal
- Do NOT change the core idea, methodology, or approach described in the Best Idea
- The revision should only improve clarity, address weaknesses, and enhance details while keeping the Best Idea intact
- If the Best Idea mentions specific techniques, methods, or frameworks, these must remain in the revised proposal

CRITICAL REQUIREMENT - PAPER CITATION FORMAT:
- When referencing papers in the proposal body, use numbered citations in square brackets (e.g., [1], [2], [3])
- Citation numbers MUST be assigned sequentially starting from [1] based on the order papers are FIRST mentioned in the proposal body
- Citation numbers MUST be continuous (1, 2, 3, 4, 5...), with NO gaps or skipped numbers
- DO NOT use generic references like "论文1" (Paper 1), "论文2" (Paper 2), or "论文X" (Paper X) in the body text
- At the end of the proposal, include a "References" section (or "参考文献" in Chinese) that lists all cited papers with their full titles
- Format references as: [1] [Full Paper Title], [2] [Full Paper Title], [3] [Full Paper Title], etc.
- References MUST be numbered sequentially from [1] to [N] with NO gaps, matching the citation numbers used in the body text
- Only include papers that are actually cited in the proposal body
- If the preliminary proposal already has a References section, renumber it to ensure continuous numbering from [1] to [N] with NO gaps

Please revise the research proposal thoroughly in light of the feedback, ensuring that the updated version fully aligns with both the original user query and the stated revision requirements. The revised proposal should clearly address the identified issues—such as lack of novelty, insufficient methodological detail, or misalignment with the user's goals—while maintaining coherence, rigor, and scientific plausibility. The refined proposal should fulfills the following requirements:
1. The proposal MUST remain consistent with the Best Idea used in the preliminary proposal.
2. If the user specifies particular sections or components the proposal should include, follow those instructions exactly.
3. If no specific structure is given, organize the proposal into the following sections:
   • Research Background – contextualize the problem and summarize key findings from the related literature (use numbered citations [1], [2], etc.),
   • Limitations of Current Work – identify critical gaps or shortcomings in existing approaches (use numbered citations [1], [2], etc.),
   • Proposed Research Plan – detail the novel idea, methodology, and how it addresses the user's query and overcomes prior limitations,
   • References – list all cited papers with their full titles in the format: [1] [Full Paper Title], [2] [Full Paper Title], etc.

IMPORTANT OUTPUT FORMAT REQUIREMENTS:
- Output your response in Markdown format.
- Start directly with the revised research proposal content. Do NOT include any introductory phrases such as "Of course", "Certainly", "I have thoroughly revised", "I have revised", "Based on", "According to", etc.
- Do NOT include any meta-commentary about the revision process (e.g., "I have revised", "I will now", "Let me", "I have addressed").
- Do NOT include any file names, metadata, or irrelevant content (e.g., "refined_idea_zh.md", file paths, etc.)
- Output ONLY the revised research proposal content itself, beginning with the first section title (e.g., "# Research Title" or "# 研究标题").
- Use numbered citations [1], [2], [3], etc. in the body text when referencing papers. Citations MUST be numbered sequentially from [1] with NO gaps.
- Include a References section at the end with full paper titles, numbered sequentially from [1] to [N] with NO gaps.
- Do NOT explain what you changed or how you revised the proposal. Simply output the improved proposal.
""",
    
    "generate_research_plan_title": """You are an expert at creating concise research proposal titles.

Task: Generate a one-sentence title that summarizes the research proposal.

Best Idea: {best_idea}

Please generate a concise, one-sentence title (no more than 20 words) that captures the core research proposal. The title should be clear, specific, and directly reflect the main research idea.

Output only the title, without any additional text or explanation.
"""
}


def get_prompt(template_name: str, language: str = 'en', **kwargs) -> str:
    """获取提示模板
    
    Args:
        template_name: 模板名称
        language: 语言，'zh'表示中文，'en'表示英文
        **kwargs: 模板参数
    """
    if template_name not in PROMPT_TEMPLATES:
        raise ValueError(f"Template '{template_name}' is not found.")
    
    template = PROMPT_TEMPLATES[template_name]
    
    # 如果language是中文，在prompt开头添加语言指令
    if language == 'zh':
        # 为中文添加语言指令
        language_instruction = "请使用中文回答。所有输出内容都必须是中文。\n\n"
        template = language_instruction + template
    
    return template.format(**kwargs)


