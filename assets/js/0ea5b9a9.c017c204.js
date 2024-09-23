"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[2413],{102:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>d,contentTitle:()=>r,default:()=>p,frontMatter:()=>i,metadata:()=>o,toc:()=>c});var a=n(85893),s=n(11151);const i={},r="DSPy",o={id:"guides/integrations/dspy",title:"DSPy",description:"DSPy is a framework for algorithmically optimizing LM prompts and weights, especially when LMs are used one or more times within a pipeline. Weave automatically tracks and logs calls made using DSPy modules and functions.",source:"@site/docs/guides/integrations/dspy.md",sourceDirName:"guides/integrations",slug:"/guides/integrations/dspy",permalink:"/guides/integrations/dspy",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/integrations/dspy.md",tags:[],version:"current",lastUpdatedAt:172710544e4,frontMatter:{},sidebar:"documentationSidebar",previous:{title:"LlamaIndex",permalink:"/guides/integrations/llamaindex"},next:{title:"Platform & Security",permalink:"/guides/platform/"}},d={},c=[{value:"Tracing",id:"tracing",level:2},{value:"Track your own ops",id:"track-your-own-ops",level:2},{value:"Create a <code>Model</code> for easier experimentation",id:"create-a-model-for-easier-experimentation",level:2},{value:"Serving a Weave Model",id:"serving-a-weave-model",level:3}];function l(e){const t={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",h3:"h3",img:"img",p:"p",pre:"pre",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",...(0,s.a)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(t.h1,{id:"dspy",children:"DSPy"}),"\n",(0,a.jsxs)(t.p,{children:[(0,a.jsx)(t.a,{href:"https://dspy-docs.vercel.app/",children:"DSPy"})," is a framework for algorithmically optimizing LM prompts and weights, especially when LMs are used one or more times within a pipeline. Weave automatically tracks and logs calls made using DSPy modules and functions."]}),"\n",(0,a.jsx)(t.h2,{id:"tracing",children:"Tracing"}),"\n",(0,a.jsx)(t.p,{children:"It\u2019s important to store traces of language model applications in a central location, both during development and in production. These traces can be useful for debugging, and as a dataset that will help you improve your application."}),"\n",(0,a.jsxs)(t.p,{children:["Weave will automatically capture traces for ",(0,a.jsx)(t.a,{href:"https://dspy-docs.vercel.app/",children:"DSPy"}),". To start tracking, calling ",(0,a.jsx)(t.code,{children:'weave.init(project_name="<YOUR-WANDB-PROJECT-NAME>")'})," and use the library as normal."]}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-python",children:'import os\nimport dspy\nimport weave\n\nos.environ["OPENAI_API_KEY"] = "<YOUR-OPENAI-API-KEY>"\n\nweave.init(project_name="<YOUR-WANDB-PROJECT-NAME>")\n\ngpt3_turbo = dspy.OpenAI(model="gpt-3.5-turbo-1106", max_tokens=300)\ndspy.configure(lm=gpt3_turbo)\nclassify = dspy.Predict("sentence -> sentiment")\nclassify(sentence="it\'s a charming and often affecting journey.")\n'})}),"\n",(0,a.jsx)(t.p,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/geekyrakshit/dspy-project/weave/calls",children:(0,a.jsx)(t.img,{alt:"dspy_trace.png",src:n(67124).Z+"",width:"2880",height:"1800"})})}),"\n",(0,a.jsx)(t.h2,{id:"track-your-own-ops",children:"Track your own ops"}),"\n",(0,a.jsxs)(t.p,{children:["Wrapping a function with ",(0,a.jsx)(t.code,{children:"@weave.op"})," starts capturing inputs, outputs and app logic so you can debug how data flows through your app. You can deeply nest ops and build a tree of functions that you want to track. This also starts automatically versioning code as you experiment to capture ad-hoc details that haven't been committed to git."]}),"\n",(0,a.jsxs)(t.p,{children:["Simply create a function decorated with ",(0,a.jsx)(t.a,{href:"/guides/tracking/ops",children:(0,a.jsx)(t.code,{children:"@weave.op"})}),"."]}),"\n",(0,a.jsxs)(t.p,{children:["In the example below, we have the function ",(0,a.jsx)(t.code,{children:"validate_context_and_answer"})," which is the metric function wrapped with ",(0,a.jsx)(t.code,{children:"@weave.op"}),". This helps us see how intermediate steps, like the optimization step for a DSPy application, are affecting the results."]}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-python",children:'import dspy\nfrom dspy.datasets import HotPotQA\nfrom dspy.teleprompt import BootstrapFewShot\n\nimport weave\n\n\nclass GenerateAnswer(dspy.Signature):\n    """Answer questions with short factoid answers."""\n\n    context = dspy.InputField(desc="may contain relevant facts")\n    question = dspy.InputField()\n    answer = dspy.OutputField(desc="often between 1 and 5 words")\n\n\nclass RAG(dspy.Module):\n    def __init__(self, num_passages=3):\n        super().__init__()\n\n        self.retrieve = dspy.Retrieve(k=num_passages)\n        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)\n    \n    def forward(self, question):\n        context = self.retrieve(question).passages\n        prediction = self.generate_answer(context=context, question=question)\n        return dspy.Prediction(context=context, answer=prediction.answer)\n\n@weave.op()\ndef validate_context_and_answer(example, pred, trace=None):\n    answer_EM = dspy.evaluate.answer_exact_match(example, pred)\n    answer_PM = dspy.evaluate.answer_passage_match(example, pred)\n    return answer_EM and answer_PM\n\n\nweave.init(project_name="dspy_rag")\nturbo = dspy.OpenAI(model=\'gpt-3.5-turbo\')\ncolbertv2_wiki17_abstracts = dspy.ColBERTv2(url=\'http://20.102.90.50:2017/wiki17_abstracts\')\ndspy.settings.configure(lm=turbo, rm=colbertv2_wiki17_abstracts)\ndataset = HotPotQA(train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0)\ntrainset = [x.with_inputs(\'question\') for x in dataset.train]\ndevset = [x.with_inputs(\'question\') for x in dataset.dev]\nteleprompter = BootstrapFewShot(metric=validate_context_and_answer)\ncompiled_rag = teleprompter.compile(RAG(), trainset=trainset)\n'})}),"\n",(0,a.jsxs)(t.table,{children:[(0,a.jsx)(t.thead,{children:(0,a.jsxs)(t.tr,{children:[(0,a.jsx)(t.th,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/geekyrakshit/dspy_rag/weave/calls?filter=%7B%22traceRootsOnly%22%3Atrue%7D&peekPath=%2Fgeekyrakshit%2Fdspy_rag%2Fcalls%2F8f643d8d-5b97-4494-b98f-ffc28bd8bf46",children:(0,a.jsx)(t.img,{alt:"dspy_without_weave_op.png",src:n(46720).Z+"",width:"2880",height:"1800"})})}),(0,a.jsx)(t.th,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/geekyrakshit/dspy_rag/weave/calls?filter=%7B%22traceRootsOnly%22%3Atrue%7D&peekPath=%2Fgeekyrakshit%2Fdspy_rag%2Fcalls%2F76dfb9bc-12e6-421b-b9dd-f10916494a27%3Fpath%3Dvalidate_context_and_answer*0%26tracetree%3D1",children:(0,a.jsx)(t.img,{alt:"dspy_with_weave_op.png",src:n(70251).Z+"",width:"2880",height:"1800"})})})]})}),(0,a.jsx)(t.tbody,{children:(0,a.jsxs)(t.tr,{children:[(0,a.jsx)(t.td,{children:"Not tracing the metric function"}),(0,a.jsxs)(t.td,{children:["Tracing the metric function using ",(0,a.jsx)(t.code,{children:"@weave.op()"})]})]})})]}),"\n",(0,a.jsxs)(t.h2,{id:"create-a-model-for-easier-experimentation",children:["Create a ",(0,a.jsx)(t.code,{children:"Model"})," for easier experimentation"]}),"\n",(0,a.jsxs)(t.p,{children:["Organizing experimentation is difficult when there are many moving pieces. By using the ",(0,a.jsx)(t.a,{href:"/guides/core-types/models",children:(0,a.jsx)(t.code,{children:"Model"})})," class, you can capture and organize the experimental details of your app like your system prompt or the model you're using. This helps organize and compare different iterations of your app."]}),"\n",(0,a.jsxs)(t.p,{children:["In addition to versioning code and capturing inputs/outputs, ",(0,a.jsx)(t.a,{href:"/guides/core-types/models",children:(0,a.jsx)(t.code,{children:"Model"})}),"s capture structured parameters that control your application\u2019s behavior, making it easy to find what parameters worked best. You can also use Weave Models with ",(0,a.jsx)(t.code,{children:"serve"}),", and ",(0,a.jsx)(t.a,{href:"/guides/core-types/evaluations",children:(0,a.jsx)(t.code,{children:"Evaluation"})}),"s."]}),"\n",(0,a.jsxs)(t.p,{children:["In the example below, you can experiment with ",(0,a.jsx)(t.code,{children:"WeaveModel"}),". Every time you change one of these, you'll get a new ",(0,a.jsx)(t.em,{children:"version"})," of ",(0,a.jsx)(t.code,{children:"WeaveModel"}),"."]}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-python",children:'import dspy\nimport weave\n\nweave.init(project_name="dspy_rag")\n\ngpt3_turbo = dspy.OpenAI(model=\'gpt-3.5-turbo-1106\', max_tokens=300)\ndspy.configure(lm=gpt3_turbo)\n\n\nclass CheckCitationFaithfulness(dspy.Signature):\n    """Verify that the text is based on the provided context."""\n\n    context = dspy.InputField(desc="facts here are assumed to be true")\n    text = dspy.InputField()\n    faithfulness = dspy.OutputField(desc="True/False indicating if text is faithful to context")\n\n\nclass WeaveModel(weave.Model):\n    signature: type\n\n    @weave.op()\n    def predict(self, context: str, text: str) -> bool:\n        return dspy.ChainOfThought(self.signature)(context=context, text=text)\n\ncontext = "The 21-year-old made seven appearances for the Hammers and netted his only goal for them in a Europa League qualification round match against Andorran side FC Lustrains last season. Lee had two loan spells in League One last term, with Blackpool and then Colchester United. He scored twice for the U\'s but was unable to save them from relegation. The length of Lee\'s contract with the promoted Tykes has not been revealed. Find all the latest football transfers on our dedicated page."\ntext = "Lee scored 3 goals for Colchester United."\n\nmodel = WeaveModel(signature=CheckCitationFaithfulness)\nprint(model.predict(context, text))\n'})}),"\n",(0,a.jsxs)(t.table,{children:[(0,a.jsx)(t.thead,{children:(0,a.jsxs)(t.tr,{children:[(0,a.jsx)(t.th,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/geekyrakshit/dspy_rag/weave/calls?filter=%7B%22traceRootsOnly%22%3Atrue%2C%22opVersionRefs%22%3A%5B%22weave%3A%2F%2F%2Fgeekyrakshit%2Fdspy_rag%2Fop%2FWeaveModel.predict%3A*%22%5D%7D&peekPath=%2Fgeekyrakshit%2Fdspy_rag%2Fobjects%2FWeaveModel%2Fversions%2FKq8TSGXULeiFmLaXJsJkueJd7RQqEX9R7XpGpg7xC2Q%3F%26",children:(0,a.jsx)(t.img,{alt:"dspy_weave_model_v1.png",src:n(66974).Z+"",width:"2880",height:"1800"})})}),(0,a.jsx)(t.th,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/geekyrakshit/dspy_rag/weave/calls?filter=%7B%22traceRootsOnly%22%3Atrue%2C%22opVersionRefs%22%3A%5B%22weave%3A%2F%2F%2Fgeekyrakshit%2Fdspy_rag%2Fop%2FWeaveModel.predict%3A*%22%5D%7D&peekPath=%2Fgeekyrakshit%2Fdspy_rag%2Fobjects%2FWeaveModel%2Fversions%2FsxYxUemiZYVOPCUU2ziMJhk3rvw2QEz7iNqEfXLBqfI%3F%26",children:(0,a.jsx)(t.img,{alt:"dspy_weave_model_v2.png",src:n(97294).Z+"",width:"2880",height:"1800"})})})]})}),(0,a.jsx)(t.tbody,{children:(0,a.jsxs)(t.tr,{children:[(0,a.jsxs)(t.td,{children:["Version 1 of the ",(0,a.jsx)(t.code,{children:"WeaveModel"})]}),(0,a.jsxs)(t.td,{children:["Version 2 of the ",(0,a.jsx)(t.code,{children:"WeaveModel"})]})]})})]}),"\n",(0,a.jsx)(t.h3,{id:"serving-a-weave-model",children:"Serving a Weave Model"}),"\n",(0,a.jsxs)(t.p,{children:["Given a weave reference any WeaveModel object, you can spin up a fastapi server and ",(0,a.jsx)(t.a,{href:"https://wandb.github.io/weave/guides/tools/serve",children:"serve"})," it."]}),"\n",(0,a.jsxs)(t.table,{children:[(0,a.jsx)(t.thead,{children:(0,a.jsx)(t.tr,{children:(0,a.jsx)(t.th,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/geekyrakshit/dspy_rag/weave/calls?filter=%7B%22traceRootsOnly%22%3Atrue%7D&peekPath=%2Fgeekyrakshit%2Fdspy_rag%2Fobjects%2FWeaveModel%2Fversions%2FsxYxUemiZYVOPCUU2ziMJhk3rvw2QEz7iNqEfXLBqfI%3F%26",children:(0,a.jsx)(t.img,{alt:"dspy_weave_model_serve.png",src:n(91792).Z+"",width:"2880",height:"1800"})})})})}),(0,a.jsx)(t.tbody,{children:(0,a.jsx)(t.tr,{children:(0,a.jsx)(t.td,{children:"You can find the weave reference of any WeaveModel by navigating to the model and copying it from the UI."})})})]}),"\n",(0,a.jsx)(t.p,{children:"You can serve your model by using the following command in the terminal:"}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-shell",children:"weave serve weave:///your_entity/project-name/YourModel:<hash>\n"})})]})}function p(e={}){const{wrapper:t}={...(0,s.a)(),...e.components};return t?(0,a.jsx)(t,{...e,children:(0,a.jsx)(l,{...e})}):l(e)}},67124:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/dspy_trace-e6d1a18840179b844d3bacc4b6a0ae78.png"},91792:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/dspy_weave_model_serve-42a1bd85f6d4291fe0032102ff8af340.png"},66974:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/dspy_weave_model_v1-c357d2827e67a6b699da7078f80c774c.png"},97294:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/dspy_weave_model_v2-9bede075e7027ad6d38eaf411912846a.png"},70251:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/dspy_with_weave_op-7cea6e57bfbd93800e41bf114adfa5d6.png"},46720:(e,t,n)=>{n.d(t,{Z:()=>a});const a=n.p+"assets/images/dspy_without_weave_op-2303632f9401c650d0360b7e0581aaa5.png"},11151:(e,t,n)=>{n.d(t,{Z:()=>o,a:()=>r});var a=n(67294);const s={},i=a.createContext(s);function r(e){const t=a.useContext(i);return a.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function o(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:r(e.components),a.createElement(i.Provider,{value:t},e.children)}}}]);