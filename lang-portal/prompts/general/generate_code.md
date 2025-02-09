## Usage

Handy codes to provide to AI to generate plans before we execute them (manually or via AI)

### 1. Generate code plan

Let the AI know it should generate the plan steps for a junior dev, add checkbox and break it down to atomic steps, add testing code if possible. Make sure the @study_sessions.py file is already available to the AI (e.g. for Windsurf IDE you can reference it in the prompt directly via @ character)

```
Can you please create a plan for a junior dev to follow to implement the /study_sessions POST route in @study_sessions.py . Create a markdown file for the plan. Add checkbox for each step. Keep steps atomic and simple. Add testing code if you can.
```

### 2. Implement code with AI

Get AI to implement one step at a time, then iterate through the plan to make sure everything is covered.

```
Please start implementing the plan @POST_study_sessions_implementation.md  , only do step 1, taking into account any prerequisites in the plan. Work on on @study_sessions.py . Mark of the steps that has been done as well.
```