"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[3453],{22805:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>l,contentTitle:()=>r,default:()=>p,frontMatter:()=>a,metadata:()=>s,toc:()=>c});var t=i(85893),o=i(11151);const a={},r="Google Gemini",s={id:"guides/integrations/google-gemini",title:"Google Gemini",description:"Google offers two ways of calling Gemini via API:",source:"@site/docs/guides/integrations/google-gemini.md",sourceDirName:"guides/integrations",slug:"/guides/integrations/google-gemini",permalink:"/guides/integrations/google-gemini",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/integrations/google-gemini.md",tags:[],version:"current",lastUpdatedAt:1730319461e3,frontMatter:{},sidebar:"documentationSidebar",previous:{title:"MistralAI",permalink:"/guides/integrations/mistral"},next:{title:"Together AI",permalink:"/guides/integrations/together_ai"}},l={},c=[{value:"Tracing",id:"tracing",level:2},{value:"Track your own ops",id:"track-your-own-ops",level:2},{value:"Create a <code>Model</code> for easier experimentation",id:"create-a-model-for-easier-experimentation",level:2},{value:"Serving a Weave Model",id:"serving-a-weave-model",level:3},{value:"Vertex API",id:"vertex-api",level:2}];function d(e){const n={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",li:"li",ol:"ol",p:"p",pre:"pre",...(0,o.a)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.h1,{id:"google-gemini",children:"Google Gemini"}),"\n",(0,t.jsx)(n.p,{children:"Google offers two ways of calling Gemini via API:"}),"\n",(0,t.jsxs)(n.ol,{children:["\n",(0,t.jsxs)(n.li,{children:["Via the ",(0,t.jsx)(n.a,{href:"https://cloud.google.com/vertexai/docs",children:"Vertex APIs"}),"."]}),"\n",(0,t.jsxs)(n.li,{children:["Via the ",(0,t.jsx)(n.a,{href:"https://ai.google.dev/gemini-api/docs/quickstart?lang=python",children:"Gemini API SDK"}),"."]}),"\n"]}),"\n",(0,t.jsx)(n.h2,{id:"tracing",children:"Tracing"}),"\n",(0,t.jsx)(n.p,{children:"It\u2019s important to store traces of language model applications in a central location, both during development and in production. These traces can be useful for debugging, and as a dataset that will help you improve your application."}),"\n",(0,t.jsxs)(n.p,{children:["Weave will automatically capture traces for ",(0,t.jsx)(n.a,{href:"https://ai.google.dev/gemini-api/docs/quickstart?lang=python",children:"Gemini API SDK"}),". To start tracking, calling ",(0,t.jsx)(n.code,{children:'weave.init(project_name="<YOUR-WANDB-PROJECT-NAME>")'})," and use the library as normal."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'import os\nimport google.generativeai as genai\nimport weave\n\nweave.init(project_name="google_ai_studio-test")\n\ngenai.configure(api_key=os.environ["GOOGLE_API_KEY"])\nmodel = genai.GenerativeModel("gemini-1.5-flash")\nresponse = model.generate_content("Write a story about an AI and magic")\n'})}),"\n",(0,t.jsx)(n.h2,{id:"track-your-own-ops",children:"Track your own ops"}),"\n",(0,t.jsxs)(n.p,{children:["Wrapping a function with ",(0,t.jsx)(n.code,{children:"@weave.op"})," starts capturing inputs, outputs and app logic so you can debug how data flows through your app. You can deeply nest ops and build a tree of functions that you want to track. This also starts automatically versioning code as you experiment to capture ad-hoc details that haven't been committed to git."]}),"\n",(0,t.jsxs)(n.p,{children:["Simply create a function decorated with ",(0,t.jsx)(n.a,{href:"/guides/tracking/ops",children:(0,t.jsx)(n.code,{children:"@weave.op"})}),"."]}),"\n",(0,t.jsxs)(n.p,{children:["In the example below, we have the function ",(0,t.jsx)(n.code,{children:"recommend_places_to_visit"})," which is a function wrapped with ",(0,t.jsx)(n.code,{children:"@weave.op"})," that recommends places to visit in a city."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'import os\nimport google.generativeai as genai\nimport weave\n\nweave.init(project_name="google_ai_studio-test")\ngenai.configure(api_key=os.environ["GOOGLE_API_KEY"])\n\n\n@weave.op()\ndef recommend_places_to_visit(city: str, model: str = "gemini-1.5-flash"):\n    model = genai.GenerativeModel(\n        model_name=model,\n        system_instruction="You are a helpful assistant meant to suggest all budget-friendly places to visit in a city",\n    )\n    response = model.generate_content(city)\n    return response.text\n\n\nrecommend_places_to_visit("New York")\nrecommend_places_to_visit("Paris")\nrecommend_places_to_visit("Kolkata")\n'})}),"\n",(0,t.jsxs)(n.h2,{id:"create-a-model-for-easier-experimentation",children:["Create a ",(0,t.jsx)(n.code,{children:"Model"})," for easier experimentation"]}),"\n",(0,t.jsxs)(n.p,{children:["Organizing experimentation is difficult when there are many moving pieces. By using the ",(0,t.jsx)(n.a,{href:"../core-types/models",children:(0,t.jsx)(n.code,{children:"Model"})})," class, you can capture and organize the experimental details of your app like your system prompt or the model you're using. This helps organize and compare different iterations of your app."]}),"\n",(0,t.jsxs)(n.p,{children:["In addition to versioning code and capturing inputs/outputs, ",(0,t.jsx)(n.a,{href:"../core-types/models",children:(0,t.jsx)(n.code,{children:"Model"})}),"s capture structured parameters that control your application\u2019s behavior, making it easy to find what parameters worked best. You can also use Weave Models with ",(0,t.jsx)(n.code,{children:"serve"}),", and ",(0,t.jsx)(n.a,{href:"/guides/core-types/evaluations",children:(0,t.jsx)(n.code,{children:"Evaluation"})}),"s."]}),"\n",(0,t.jsxs)(n.p,{children:["In the example below, you can experiment with ",(0,t.jsx)(n.code,{children:"CityVisitRecommender"}),". Every time you change one of these, you'll get a new ",(0,t.jsx)(n.em,{children:"version"})," of ",(0,t.jsx)(n.code,{children:"CityVisitRecommender"}),"."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'import os\nimport google.generativeai as genai\nimport weave\n\n\nclass CityVisitRecommender(weave.Model):\n    model: str\n\n    @weave.op()\n    def predict(self, city: str) -> str:\n        model = genai.GenerativeModel(\n            model_name=self.model,\n            system_instruction="You are a helpful assistant meant to suggest all budget-friendly places to visit in a city",\n        )\n        response = model.generate_content(city)\n        return response.text\n\n\nweave.init(project_name="google_ai_studio-test")\ngenai.configure(api_key=os.environ["GOOGLE_API_KEY"])\ncity_recommender = CityVisitRecommender(model="gemini-1.5-flash")\nprint(city_recommender.predict("New York"))\nprint(city_recommender.predict("San Francisco"))\nprint(city_recommender.predict("Los Angeles"))\n'})}),"\n",(0,t.jsx)(n.h3,{id:"serving-a-weave-model",children:"Serving a Weave Model"}),"\n",(0,t.jsxs)(n.p,{children:["Given a weave reference to any ",(0,t.jsx)(n.code,{children:"weave.Model"})," object, you can spin up a fastapi server and ",(0,t.jsx)(n.a,{href:"https://wandb.github.io/weave/guides/tools/serve",children:"serve"})," it. You can serve your model by using the following command in the terminal:"]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-shell",children:"weave serve weave:///your_entity/project-name/YourModel:<hash>\n"})}),"\n",(0,t.jsx)(n.h2,{id:"vertex-api",children:"Vertex API"}),"\n",(0,t.jsxs)(n.p,{children:["Full Weave support for the ",(0,t.jsx)(n.code,{children:"Vertex AI SDK"})," python package is currently in development, however there is a way you can integrate Weave with the Vertex API."]}),"\n",(0,t.jsxs)(n.p,{children:["Vertex API supports OpenAI SDK compatibility (",(0,t.jsx)(n.a,{href:"https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/call-gemini-using-openai-library",children:"docs"}),"), and if this is a way you build your application, Weave will automatically track your LLM calls via our ",(0,t.jsx)(n.a,{href:"/guides/integrations/openai",children:"OpenAI"})," SDK integration."]}),"\n",(0,t.jsx)(n.p,{children:"* Please note that some features may not fully work as Vertex API doesn't implement the full OpenAI SDK capabilities."})]})}function p(e={}){const{wrapper:n}={...(0,o.a)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(d,{...e})}):d(e)}},11151:(e,n,i)=>{i.d(n,{Z:()=>s,a:()=>r});var t=i(67294);const o={},a=t.createContext(o);function r(e){const n=t.useContext(a);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function s(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:r(e.components),t.createElement(a.Provider,{value:n},e.children)}}}]);