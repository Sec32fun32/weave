"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[1550],{1811:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>r,contentTitle:()=>i,default:()=>u,frontMatter:()=>a,metadata:()=>c,toc:()=>d});var o=n(85893),s=n(11151);const a={title:"Custom Model Cost"},i="Setting up a custom cost model",c={id:"reference/gen_notebooks/custom_model_cost",title:"Custom Model Cost",description:"Open in Colab",source:"@site/docs/reference/gen_notebooks/custom_model_cost.md",sourceDirName:"reference/gen_notebooks",slug:"/reference/gen_notebooks/custom_model_cost",permalink:"/reference/gen_notebooks/custom_model_cost",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/reference/gen_notebooks/custom_model_cost.md",tags:[],version:"current",lastUpdatedAt:1726609569e3,frontMatter:{title:"Custom Model Cost"},sidebar:"notebookSidebar",previous:{title:"Code Generation",permalink:"/reference/gen_notebooks/codegen"},next:{title:"Prompt Optimization",permalink:"/reference/gen_notebooks/dspy_prompt_optimization"}},r={},d=[{value:"Set up the environment",id:"set-up-the-environment",level:2},{value:"Setting up a model with weave",id:"setting-up-a-model-with-weave",level:2},{value:"Add a custom cost",id:"add-a-custom-cost",level:2}];function l(e){const t={admonition:"admonition",code:"code",em:"em",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...(0,s.a)(),...e.components};return(0,o.jsxs)(o.Fragment,{children:[(0,o.jsxs)(t.admonition,{title:"This is a notebook",type:"tip",children:[(0,o.jsx)("a",{href:"https://colab.research.google.com/github/wandb/weave/blob/master/docs/./notebooks/custom_model_cost.ipynb",target:"_blank",rel:"noopener noreferrer",class:"navbar__item navbar__link button button--secondary button--med margin-right--sm notebook-cta-button",children:(0,o.jsxs)("div",{children:[(0,o.jsx)("img",{src:"https://upload.wikimedia.org/wikipedia/commons/archive/d/d0/20221103151430%21Google_Colaboratory_SVG_Logo.svg",alt:"Open In Colab",height:"20px"}),(0,o.jsx)("div",{children:"Open in Colab"})]})}),(0,o.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/docs/./notebooks/custom_model_cost.ipynb",target:"_blank",rel:"noopener noreferrer",class:"navbar__item navbar__link button button--secondary button--med margin-right--sm notebook-cta-button",children:(0,o.jsxs)("div",{children:[(0,o.jsx)("img",{src:"https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg",alt:"View in Github",height:"15px"}),(0,o.jsx)("div",{children:"View in Github"})]})})]}),"\n",(0,o.jsx)("img",{src:"http://wandb.me/logo-im-png",width:"400",alt:"Weights & Biases"}),"\n",(0,o.jsx)(t.h1,{id:"setting-up-a-custom-cost-model",children:"Setting up a custom cost model"}),"\n",(0,o.jsx)(t.p,{children:"Weave calculates costs based on the number of tokens used and the model used.\nWeave grabs this usage and model from the output and associates them with the call."}),"\n",(0,o.jsx)(t.p,{children:"Let's set up a simple custom model, that calculates its own token usage, and stores that in weave."}),"\n",(0,o.jsx)(t.h2,{id:"set-up-the-environment",children:"Set up the environment"}),"\n",(0,o.jsxs)(t.p,{children:["We install and import all needed packages.\nWe set ",(0,o.jsx)(t.code,{children:"WANDB_API_KEY"})," in our env so that we may easily login with ",(0,o.jsx)(t.code,{children:"wandb.login()"})," (this should be given to the colab as a secret)."]}),"\n",(0,o.jsxs)(t.p,{children:["We set the project in W&B we want to log this into in ",(0,o.jsx)(t.code,{children:"name_of_wandb_project"}),"."]}),"\n",(0,o.jsxs)(t.p,{children:[(0,o.jsx)(t.strong,{children:(0,o.jsx)(t.em,{children:"NOTE:"})})," ",(0,o.jsx)(t.code,{children:"name_of_wandb_project"})," may also be in the format of ",(0,o.jsx)(t.code,{children:"{team_name}/{project_name}"})," to specify a team to log the traces into."]}),"\n",(0,o.jsxs)(t.p,{children:["We then fetch a weave client by calling ",(0,o.jsx)(t.code,{children:"weave.init()"})]}),"\n",(0,o.jsx)(t.pre,{children:(0,o.jsx)(t.code,{className:"language-python",children:"%pip install wandb weave datetime --quiet\n"})}),"\n",(0,o.jsx)(t.pre,{children:(0,o.jsx)(t.code,{className:"language-python",children:'import os\n\nimport wandb\nfrom google.colab import userdata\n\nimport weave\n\nos.environ["WANDB_API_KEY"] = userdata.get("WANDB_API_KEY")\nname_of_wandb_project = "custom-cost-model"\n\nwandb.login()\n'})}),"\n",(0,o.jsx)(t.pre,{children:(0,o.jsx)(t.code,{className:"language-python",children:"weave_client = weave.init(name_of_wandb_project)\n"})}),"\n",(0,o.jsx)(t.h2,{id:"setting-up-a-model-with-weave",children:"Setting up a model with weave"}),"\n",(0,o.jsx)(t.pre,{children:(0,o.jsx)(t.code,{className:"language-python",children:'from weave import Model\n\n\nclass YourModel(Model):\n    attribute1: str\n    attribute2: int\n\n    def simple_token_count(self, text: str) -> int:\n        return len(text) // 3\n\n    # This is a custom op that we are defining\n    # It takes in a string, and outputs a dict with the usage counts, model name, and the output\n    @weave.op()\n    def custom_model_generate(self, input_data: str) -> dict:\n        # Model logic goes here\n        # Here is where you would have a custom generate function\n        prediction = self.attribute1 + " " + input_data\n\n        # Usage counts\n        prompt_tokens = self.simple_token_count(input_data)\n        completion_tokens = self.simple_token_count(prediction)\n\n        # We return a dictionary with the usage counts, model name, and the output\n        # Weave will automatically associate this with the trace\n        # This object {usage, model, output} matches the output of a OpenAI Call\n        return {\n            "usage": {\n                "input_tokens": prompt_tokens,\n                "output_tokens": completion_tokens,\n            },\n            "model": "your_model_name",\n            "output": prediction,\n        }\n\n    # In our predict function we call our custom generate function, and return the output.\n    @weave.op()\n    def predict(self, input_data: str) -> dict:\n        # Here is where you would do any post processing of the data\n        outputs = self.custom_model_generate(input_data)\n        return outputs["output"]\n'})}),"\n",(0,o.jsx)(t.h2,{id:"add-a-custom-cost",children:"Add a custom cost"}),"\n",(0,o.jsxs)(t.p,{children:["Here we add a custom cost, and now that we have a custom cost, and our calls have usage, we can fetch the calls with ",(0,o.jsx)(t.code,{children:"include_cost"})," and our calls with have costs under ",(0,o.jsx)(t.code,{children:"summary.weave.costs"}),"."]}),"\n",(0,o.jsx)(t.pre,{children:(0,o.jsx)(t.code,{className:"language-python",children:'model = YourModel(attribute1="Hello", attribute2=1)\nmodel.predict("world")\n\n# We then add a custom cost to our project\nweave_client.add_cost(\n    llm_id="your_model_name", prompt_token_cost=0.1, completion_token_cost=0.2\n)\n\n# We can then query for the calls, and with include_costs=True\n# we receive the costs back attached to the calls\ncalls = weave_client.get_calls(filter={"trace_roots_only": True}, include_costs=True)\n\nlist(calls)\n'})})]})}function u(e={}){const{wrapper:t}={...(0,s.a)(),...e.components};return t?(0,o.jsx)(t,{...e,children:(0,o.jsx)(l,{...e})}):l(e)}},11151:(e,t,n)=>{n.d(t,{Z:()=>c,a:()=>i});var o=n(67294);const s={},a=o.createContext(s);function i(e){const t=o.useContext(a);return o.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function c(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:i(e.components),o.createElement(a.Provider,{value:t},e.children)}}}]);