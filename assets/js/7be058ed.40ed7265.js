"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[3453],{5592:(e,i,n)=>{n.r(i),n.d(i,{assets:()=>l,contentTitle:()=>r,default:()=>g,frontMatter:()=>a,metadata:()=>s,toc:()=>c});var t=n(5893),o=n(1151);const a={},r="Google Gemini",s={id:"guides/integrations/google-gemini",title:"Google Gemini",description:"Google offers two ways of calling Gemini via API:",source:"@site/docs/guides/integrations/google-gemini.md",sourceDirName:"guides/integrations",slug:"/guides/integrations/google-gemini",permalink:"/weave/guides/integrations/google-gemini",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/integrations/google-gemini.md",tags:[],version:"current",frontMatter:{},sidebar:"documentationSidebar",previous:{title:"DSPy",permalink:"/weave/guides/integrations/dspy"},next:{title:"Together AI",permalink:"/weave/guides/integrations/together_ai"}},l={},c=[{value:"Vertex API",id:"vertex-api",level:2},{value:"Gemini API",id:"gemini-api",level:2}];function d(e){const i={a:"a",admonition:"admonition",code:"code",h1:"h1",h2:"h2",li:"li",ol:"ol",p:"p",...(0,o.a)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(i.h1,{id:"google-gemini",children:"Google Gemini"}),"\n",(0,t.jsx)(i.p,{children:"Google offers two ways of calling Gemini via API:"}),"\n",(0,t.jsxs)(i.ol,{children:["\n",(0,t.jsxs)(i.li,{children:["Via the Vertex APIs (",(0,t.jsx)(i.a,{href:"https://cloud.google.com/vertexai/docs",children:"docs"}),")"]}),"\n",(0,t.jsxs)(i.li,{children:["Via the Gemini API (",(0,t.jsx)(i.a,{href:"https://ai.google.dev/gemini-api/docs/quickstart?lang=python",children:"docs"}),")"]}),"\n"]}),"\n",(0,t.jsx)(i.h2,{id:"vertex-api",children:"Vertex API"}),"\n",(0,t.jsxs)(i.p,{children:["Full Weave support for the ",(0,t.jsx)(i.code,{children:"Vertex AI SDK"})," python package is currently in development, however there is a way you can integrate Weave with the Vertex API."]}),"\n",(0,t.jsxs)(i.p,{children:["Vertex API supports OpenAI SDK compatibility (",(0,t.jsx)(i.a,{href:"https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/call-gemini-using-openai-library",children:"docs"}),"), and if this is a way you build your application, Weave will automatically track your LLM calls via our ",(0,t.jsx)(i.a,{href:"/guides/integrations/openai",children:"OpenAI"})," SDK integration."]}),"\n",(0,t.jsx)(i.p,{children:"* Please note that some features may not fully work as Vertex API doesn't implement the full OpenAI SDK capabilities."}),"\n",(0,t.jsx)(i.h2,{id:"gemini-api",children:"Gemini API"}),"\n",(0,t.jsx)(i.admonition,{type:"info",children:(0,t.jsxs)(i.p,{children:["Weave native client integration with the ",(0,t.jsx)(i.code,{children:"google-generativeai"})," python package is currently in development"]})}),"\n",(0,t.jsxs)(i.p,{children:["While we build the native integration with the Gemini API native python package, you can easily integrate Weave with the Gemini API yourself simply by initializing Weave with ",(0,t.jsx)(i.code,{children:"weave.init('<your-project-name>')"})," and then wrapping the calls that call your LLMs with ",(0,t.jsx)(i.code,{children:"weave.op()"}),". See our guide on ",(0,t.jsx)(i.a,{href:"/guides/tracking/tracing",children:"tracing"})," for more details."]})]})}function g(e={}){const{wrapper:i}={...(0,o.a)(),...e.components};return i?(0,t.jsx)(i,{...e,children:(0,t.jsx)(d,{...e})}):d(e)}},1151:(e,i,n)=>{n.d(i,{Z:()=>s,a:()=>r});var t=n(7294);const o={},a=t.createContext(o);function r(e){const i=t.useContext(a);return t.useMemo((function(){return"function"==typeof e?e(i):{...i,...e}}),[i,e])}function s(e){let i;return i=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:r(e.components),t.createElement(a.Provider,{value:i},e.children)}}}]);