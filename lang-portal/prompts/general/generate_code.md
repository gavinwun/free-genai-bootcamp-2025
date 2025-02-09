## Usage

Handy codes to provide to AI to generate plans before we execute them (manually or via AI)

### 1. Generate code plan

Let the AI know it should generate the plan steps for a junior dev, add checkbox and break it down to atomic steps, add testing code if possible. Make sure the @study_sessions.py file is already available to the AI (e.g. for Windsurf IDE you can reference it in the prompt directly via @ character)

```
Can you please create a plan for a junior dev to follow to implement the /study_sessions POST route in @study_sessions.py . Create a markdown file for the plan. Add checkbox for each step. Keep steps atomic and simple. Add testing code if you can.
```