from weave_query import context_state

loading_builtins_token = context_state.set_loading_built_ins()

try:
    from weave_query.ecosystem.replicate.rep import *
finally:
    context_state.clear_loading_built_ins(loading_builtins_token)
