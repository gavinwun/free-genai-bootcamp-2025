# Backend Portal Implementation Findings

I am using Windsurf pro plan and the below are the findings during implementing the remaining todo backend API routes -

1. DeepSeek V3 isn't able to handle coding tasks, where the model struggled to find TODO comments
2. DeepSeek R1 was able to find TODO comments in coding tasks, but ended up creating the wrong route - e.g. # todo POST /study_sessions/:id/review became # todo PUT /study_sessions/:id 
3. DeepSeek R1 went on a very in-depth thinking and created alot of specs for a single route and examples, which I guess was good if it had gotten the correct routes to implement
4. I then switched to Claude 3.5 Sonnet, and it's analysis and coding abilities with live files are definitely far more superior
5. Claude 3.5 Sonnet does make mistakes as well, where it changed the usage of app.db to g.db because it was following Flask pattern/conventions