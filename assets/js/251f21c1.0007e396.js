"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[6837],{70091:(e,t,o)=>{o.r(t),o.d(t,{assets:()=>i,contentTitle:()=>a,default:()=>u,frontMatter:()=>c,metadata:()=>r,toc:()=>l});var s=o(85893),n=o(11151);const c={},a="Costs",r={id:"guides/tracking/costs",title:"Costs",description:"Adding a custom cost",source:"@site/docs/guides/tracking/costs.md",sourceDirName:"guides/tracking",slug:"/guides/tracking/costs",permalink:"/guides/tracking/costs",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/tracking/costs.md",tags:[],version:"current",lastUpdatedAt:173029988e4,frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Feedback",permalink:"/guides/tracking/feedback"},next:{title:"Logging media",permalink:"/guides/core-types/media"}},i={},l=[{value:"Adding a custom cost",id:"adding-a-custom-cost",level:2},{value:"Querying for costs",id:"querying-for-costs",level:2},{value:"Purging a custom cost",id:"purging-a-custom-cost",level:2},{value:"Calculating costs for a Project",id:"calculating-costs-for-a-project",level:2},{value:"Setting up a custom model with custom costs",id:"setting-up-a-custom-model-with-custom-costs",level:2}];function d(e){const t={a:"a",code:"code",h1:"h1",h2:"h2",p:"p",pre:"pre",...(0,n.a)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(t.h1,{id:"costs",children:"Costs"}),"\n",(0,s.jsx)(t.h2,{id:"adding-a-custom-cost",children:"Adding a custom cost"}),"\n",(0,s.jsxs)(t.p,{children:["You can add a custom cost by using the ",(0,s.jsx)(t.a,{href:"/reference/python-sdk/weave/trace/weave.trace.weave_client#method-add_cost",children:(0,s.jsx)(t.code,{children:"add_cost"})})," method.\nThe three required fields are ",(0,s.jsx)(t.code,{children:"llm_id"}),", ",(0,s.jsx)(t.code,{children:"prompt_token_cost"}),", and ",(0,s.jsx)(t.code,{children:"completion_token_cost"}),".\n",(0,s.jsx)(t.code,{children:"llm_id"})," is the name of the LLM (e.g. ",(0,s.jsx)(t.code,{children:"gpt-4o"}),"). ",(0,s.jsx)(t.code,{children:"prompt_token_cost"})," and ",(0,s.jsx)(t.code,{children:"completion_token_cost"})," are cost per token for the LLM (if the LLM prices were specified inper million tokens, make sure to convert the value).\nYou can also set ",(0,s.jsx)(t.code,{children:"effective_date"})," to a datetime, to make the cost effective at a specific date, this defaults to the current date."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-python",children:'import weave\nfrom datetime import datetime\n\nclient = weave.init("my_custom_cost_model")\n\nclient.add_cost(\n    llm_id="your_model_name",\n    prompt_token_cost=0.01,\n    completion_token_cost=0.02\n)\n\nclient.add_costs({\n    llm_id="your_model_name",\n    prompt_token_cost=10,\n    completion_token_cost=20,\n    # If for example I want to raise the price of the model after a certain date\n    effective_date=datetime(2025, 4, 22),\n)\n'})}),"\n",(0,s.jsx)(t.h2,{id:"querying-for-costs",children:"Querying for costs"}),"\n",(0,s.jsxs)(t.p,{children:["You can query for costs by using the ",(0,s.jsx)(t.a,{href:"/reference/python-sdk/weave/trace/weave.trace.weave_client#method-query_costs",children:(0,s.jsx)(t.code,{children:"query_costs"})})," method.\nThere are a few ways to query for costs, you can pass in a singular cost id, or a list of LLM model names."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-python",children:'import weave\n\nclient = weave.init("my_custom_cost_model")\n\ncosts = client.query_costs(llm_ids=["your_model_name"])\n\ncost = client.query_costs(costs[0].id)\n'})}),"\n",(0,s.jsx)(t.h2,{id:"purging-a-custom-cost",children:"Purging a custom cost"}),"\n",(0,s.jsxs)(t.p,{children:["You can purge a custom cost by using the ",(0,s.jsx)(t.a,{href:"/reference/python-sdk/weave/trace/weave.trace.weave_client#method-purge_costs",children:(0,s.jsx)(t.code,{children:"purge_costs"})})," method. You pass in a list of cost ids, and the costs with those ids are purged."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-python",children:'import weave\n\nclient = weave.init("my_custom_cost_model")\n\ncosts = client.query_costs(llm_ids=["your_model_name"])\nclient.purge_costs([cost.id for cost in costs])\n'})}),"\n",(0,s.jsx)(t.h2,{id:"calculating-costs-for-a-project",children:"Calculating costs for a Project"}),"\n",(0,s.jsxs)(t.p,{children:["You can calculate costs for a project by using our ",(0,s.jsx)(t.code,{children:"calls_query"})," and adding ",(0,s.jsx)(t.code,{children:"include_costs=True"})," with a little bit of setup."]}),"\n",(0,s.jsx)(t.pre,{children:(0,s.jsx)(t.code,{className:"language-python",children:'import weave\n\nweave.init("project_costs")\n@weave.op()\ndef get_costs_for_project(project_name: str):\n    total_cost = 0\n    requests = 0\n\n    client = weave.init(project_name)\n    # Fetch all the calls in the project\n    calls = list(\n        client.get_calls(filter={"trace_roots_only": True}, include_costs=True)\n    )\n\n    for call in calls:\n        # If the call has costs, we add them to the total cost\n        if call.summary["weave"] is not None and call.summary["weave"].get("costs", None) is not None:\n            for k, cost in call.summary["weave"]["costs"].items():\n                requests += cost["requests"]\n                total_cost += cost["prompt_tokens_total_cost"]\n                total_cost += cost["completion_tokens_total_cost"]\n\n    # We return the total cost, requests, and calls\n    return {\n        "total_cost": total_cost,\n        "requests": requests,\n        "calls": len(calls),\n    }\n\n# Since we decorated our function with @weave.op(),\n# our totals are stored in weave for historic cost total calculations\nget_costs_for_project("my_custom_cost_model")\n'})}),"\n",(0,s.jsx)(t.h2,{id:"setting-up-a-custom-model-with-custom-costs",children:"Setting up a custom model with custom costs"}),"\n",(0,s.jsxs)(t.p,{children:["Try our cookbook for a ",(0,s.jsx)(t.a,{href:"/reference/gen_notebooks/custom_model_cost",children:"Setting up costs with a custom model"})," or ",(0,s.jsx)("a",{href:"https://colab.research.google.com/github/wandb/weave/blob/master/docs/./notebooks/custom_model_cost.ipynb",target:"_blank",rel:"noopener noreferrer",class:"navbar__item navbar__link button button--secondary button--med margin-right--sm notebook-cta-button",children:(0,s.jsxs)("div",{children:[(0,s.jsx)("img",{src:"https://upload.wikimedia.org/wikipedia/commons/archive/d/d0/20221103151430%21Google_Colaboratory_SVG_Logo.svg",alt:"Open In Colab",height:"20px"}),(0,s.jsx)("div",{children:"Open in Colab"})]})})]})]})}function u(e={}){const{wrapper:t}={...(0,n.a)(),...e.components};return t?(0,s.jsx)(t,{...e,children:(0,s.jsx)(d,{...e})}):d(e)}},11151:(e,t,o)=>{o.d(t,{Z:()=>r,a:()=>a});var s=o(67294);const n={},c=s.createContext(n);function a(e){const t=s.useContext(c);return s.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function r(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(n):e.components||n:a(e.components),s.createElement(c.Provider,{value:t},e.children)}}}]);