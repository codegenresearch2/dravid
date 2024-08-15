from .nextjs_prompt import nextjs_prompt

framework_prompts = {
    "nextjs": nextjs_prompt
}


def framework_specific_prompt(framework):
    if not framework:
        return ""
    fun = framework_prompts.get(framework)
    return fun()
