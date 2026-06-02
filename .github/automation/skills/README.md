# Team Skills

This folder stores team-level skill command templates for the local automation runner.

## File

- skills.yaml: Step-level command templates.
- skill_runner.py: Shared step executor for team defaults.

## Supported steps

- run_agent
- quality_gate
- commit_and_push

## Placeholders

- {issue_number}
- {issue_title}
- {issue_identifier}
- {issue_url}
- {issue_body}
- {workspace}
- {workflow}
- {prompt}
- {branch_name}
- {base_branch}
- {agent_command}
- {quality_commands}

## Notes

- If a step command is empty, the runner uses built-in logic for that step.
- Disable all skills by setting AUTOMATION_USE_SKILLS=false.
- Override file path with AUTOMATION_SKILLS_FILE.

## Team Recommendation

- Keep skills.yaml as the team policy layer.
- Put reusable logic in skill_runner.py.
- Customize only command templates and env vars per repository.
