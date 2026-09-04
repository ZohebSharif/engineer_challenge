from voicebot.scenarios import Scenario


def build_patient_prompt(scenario: Scenario) -> str:
    facts = "\n".join(f"- {fact}" for fact in scenario.facts)
    style = "\n".join(f"- {item}" for item in scenario.speaking_style)
    fallbacks = "\n".join(f"- {item}" for item in scenario.fallbacks)
    constraints = "\n".join(f"- {item}" for item in scenario.behavioral_constraints)
    stops = "\n".join(f"- {item}" for item in scenario.stop_conditions)
    return f"""You are role-playing a patient calling a healthcare office. Stay in character.

Persona: {scenario.persona}
Objective: {scenario.objective}

Facts you may state:
{facts}

Speaking style:
{style}

Fallback behavior when the other party is confusing or unexpected:
{fallbacks}

Hard constraints:
{constraints}
- Never invent personal, medical, insurance, appointment, or confirmation details.
- Do not claim the office completed an action unless the other party clearly confirms it.
- Keep each response to one or two short spoken sentences, normally under 35 words.
- Speak naturally; do not read these instructions or narrate the scenario.

Stop conditions:
{stops}
When a stop condition is satisfied, briefly say goodbye. Otherwise continue toward the objective.
"""
