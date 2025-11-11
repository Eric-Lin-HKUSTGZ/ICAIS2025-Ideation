PROMPT_TEMPLATES = {
    "retrieve_query": """You are an expert at extracting keywords from user queries. 
Below, I will provide you with a user query in which the user expresses interest in developing a new research proposal. Your task is to extract up to two keywords that best capture the core research topic or methodology of interest to the user.

Each keyword must be:

1. A noun (or noun phrase),
2. Written in lowercase English,
3. Representative of the central concept or approach in the query.

Here is the user query:
User Query: {user_query}

Please output exactly one or two keywords—no more, no less—each as a lowercase English noun, separated by a comma and without any additional text, punctuation, or formatting.
""",
    
    "expand_background": """You are an expert at expanding brief research queries into detailed research backgrounds.

Task: Expand the following brief research query into a comprehensive research background suitable for an undergraduate student to understand.

Brief Query: {brief_background}
Keywords: {keywords}

Please provide a detailed research background (200-500 words) that:
1. Explains the research problem clearly
2. Provides context and motivation
3. Describes the importance of the research area
4. Uses clear and accessible language

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
Please present 3 to 4 ideas in the following format:
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

Please generate a concise research inspiration (2-3 sentences) that:
1. Identifies a novel insight or opportunity from this paper
2. Connects it to the research background
3. Suggests a potential research direction

Inspiration:
""",
    
    "generate_global_inspiration": """You are a professional research paper analyst skilled at drawing creative inspiration from academic literature. 
Below, I will provide a user query along with a set of related papers, including the latest, highly cited, and relevant works. Your task is to synthesize these papers holistically and propose one novel research inspiration that directly addresses the user's query.

Here is the information provided:
User Query: {user_query}
Related Papers: {paper}

Please synthesize these papers holistically—without analyzing each one individually—and propose one novel research inspiration that directly addresses the user's query. The inspiration should emerge from a deep understanding of the underlying assumptions, gaps, or unexplored opportunities in the existing literature, not merely by combining existing methods. Prioritize conceptual insight and originality over technical aggregation, and ensure the proposal is both innovative and closely aligned with the user's needs. Focus on delivering a concise, imaginative spark rooted in genuine scholarly insight.
""",
    
    "generate_ideas_from_inspirations": """You are an experienced AI researcher. Based on multiple research inspirations, generate innovative research ideas.

Research Background: {background}

Inspirations:
{inspirations}

Please generate exactly 3 research ideas based on these inspirations. Each idea should be innovative and address the research background.

Format your response as:
**Idea 1**: [Description of the first idea]
**Idea 2**: [Description of the second idea]
**Idea 3**: [Description of the third idea]
""",
    
    "generate_idea_from_inspiration": """You are an experienced AI researcher. Based on a research inspiration, generate innovative research ideas.

Research Background: {background}

Inspiration: {inspiration}

Please generate 2-3 research ideas based on this inspiration. Each idea should be innovative and address the research background.

Format your response as:
**Idea 1**: [Description of the first idea]
**Idea 2**: [Description of the second idea]
...
""",
    
    "integrate_with_brainstorm": """You are a researcher in the field of AI with innovative and pioneering abilities. You are good at generating innovative and original ideas to solve cutting-edge problems in the field of AI.

Task Description: 
You will be provided with research background information along with a set of ideas you generated previously from the related paper information, and a set of brainstorming ideas concerning the same research topic. Your task is to combine these ideas and generate new ones, the new ideas you generate should base on the ideas you generated previously, and integrate creative parts of the brainstorming ideas. Consider the background thoroughly, taking into account the novelty and practicability of each idea. If you think an idea you generate is reasonable and valuable, feel free to retain it. 

### Information Provided:
1. **Research Background**: The starting point for idea generation based on the research context.
2. **Brainstorming Ideas**: These ideas were generated purely from the research background, focusing on innovation and may not be directly related to the problem.
3. **Generated Ideas**: These are the ideas you previously generated by considering both the research background and related papers.

### Approach:
- **Step 1**: Review the research background and original ideas to understand the foundation of the problem.
- **Step 2**: Consider the brainstorming ideas and original ideas together. Combine, improve, or expand upon them, integrating insights from the related papers.
- **Step 3**: Propose new ideas that are innovative and practical, ensuring they align with the research background.

### Specific Information:
1. **Research Background**: {background}
2. **Brainstorming Ideas**: {brainstorm}
3. **Generated Ideas**: {ideas}

### Format for Your Response:
Please ensure that your final ideas include exactly 3 entries and present the integrated ideas in the following format:
**Idea 1**: [The first method idea]
**Idea 2**: [The second method idea]
**Idea 3**: [The third method idea]
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

Based on this information, please draft a complete research proposal that fulfills the following requirements:

1. The proposal must be grounded in the provided research inspiration and best idea—do not deviate from or replace them.
2. If the user specifies particular sections or components the proposal should include, follow those instructions exactly.
3. If no specific structure is given, organize the proposal into the following three sections:
   • Research Background – contextualize the problem and summarize key findings from the related literature,
   • Limitations of Current Work – identify critical gaps or shortcomings in existing approaches, and
   • Proposed Research Plan – detail the novel idea, methodology, and how it addresses the user's query and overcomes prior limitations.

IMPORTANT OUTPUT FORMAT REQUIREMENTS:
- Start directly with the research proposal content. Do NOT include any introductory phrases such as "Of course", "Certainly", "I have thoroughly revised", "Based on", "According to", etc.
- Do NOT include any meta-commentary about the writing process (e.g., "I have revised", "I will now", "Let me").
- Output ONLY the research proposal content itself, beginning with the first section title.
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

Please revise the research proposal thoroughly in light of the feedback, ensuring that the updated version fully aligns with both the original user query and the stated revision requirements. The revised proposal should clearly address the identified issues—such as lack of novelty, insufficient methodological detail, or misalignment with the user's goals—while maintaining coherence, rigor, and scientific plausibility. The refined proposal should fulfills the following requirements:
1. If the user specifies particular sections or components the proposal should include, follow those instructions exactly.
2. If no specific structure is given, organize the proposal into the following three sections:
   • Research Background – contextualize the problem and summarize key findings from the related literature,
   • Limitations of Current Work – identify critical gaps or shortcomings in existing approaches, and
   • Proposed Research Plan – detail the novel idea, methodology, and how it addresses the user's query and overcomes prior limitations.

IMPORTANT OUTPUT FORMAT REQUIREMENTS:
- Start directly with the revised research proposal content. Do NOT include any introductory phrases such as "Of course", "Certainly", "I have thoroughly revised", "I have revised", "Based on", "According to", etc.
- Do NOT include any meta-commentary about the revision process (e.g., "I have revised", "I will now", "Let me", "I have addressed").
- Output ONLY the revised research proposal content itself, beginning with the first section title.
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


