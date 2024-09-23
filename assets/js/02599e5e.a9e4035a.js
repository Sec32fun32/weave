"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[701],{13751:(e,c,d)=>{d.r(c),d.d(c,{assets:()=>i,contentTitle:()=>t,default:()=>o,frontMatter:()=>a,metadata:()=>n,toc:()=>h});var s=d(85893),r=d(11151);const a={sidebar_label:"feedback"},t="weave.trace.feedback",n={id:"reference/python-sdk/weave/trace/weave.trace.feedback",title:"weave.trace.feedback",description:"Classes for working with feedback on a project or ref level.",source:"@site/docs/reference/python-sdk/weave/trace/weave.trace.feedback.md",sourceDirName:"reference/python-sdk/weave/trace",slug:"/reference/python-sdk/weave/trace/weave.trace.feedback",permalink:"/reference/python-sdk/weave/trace/weave.trace.feedback",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/reference/python-sdk/weave/trace/weave.trace.feedback.md",tags:[],version:"current",lastUpdatedAt:172710544e4,frontMatter:{sidebar_label:"feedback"},sidebar:"pythonSdkSidebar",previous:{title:"weave",permalink:"/reference/python-sdk/weave/"},next:{title:"op",permalink:"/reference/python-sdk/weave/trace/weave.trace.op"}},i={},h=[{value:"Classes",id:"classes",level:2},{value:"<kbd>class</kbd> <code>Feedbacks</code>",id:"class-feedbacks",level:2},{value:"<kbd>method</kbd> <code>__init__</code>",id:"method-__init__",level:3},{value:"<kbd>method</kbd> <code>refs</code>",id:"method-refs",level:3},{value:"<kbd>class</kbd> <code>FeedbackQuery</code>",id:"class-feedbackquery",level:2},{value:"<kbd>method</kbd> <code>__init__</code>",id:"method-__init__-1",level:3},{value:"<kbd>method</kbd> <code>execute</code>",id:"method-execute",level:3},{value:"<kbd>method</kbd> <code>refresh</code>",id:"method-refresh",level:3},{value:"<kbd>method</kbd> <code>refs</code>",id:"method-refs-1",level:3},{value:"<kbd>class</kbd> <code>RefFeedbackQuery</code>",id:"class-reffeedbackquery",level:2},{value:"<kbd>method</kbd> <code>__init__</code>",id:"method-__init__-2",level:3},{value:"<kbd>method</kbd> <code>add</code>",id:"method-add",level:3},{value:"<kbd>method</kbd> <code>add_note</code>",id:"method-add_note",level:3},{value:"<kbd>method</kbd> <code>add_reaction</code>",id:"method-add_reaction",level:3},{value:"<kbd>method</kbd> <code>execute</code>",id:"method-execute-1",level:3},{value:"<kbd>method</kbd> <code>purge</code>",id:"method-purge",level:3},{value:"<kbd>method</kbd> <code>refresh</code>",id:"method-refresh-1",level:3},{value:"<kbd>method</kbd> <code>refs</code>",id:"method-refs-2",level:3}];function l(e){const c={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",hr:"hr",li:"li",p:"p",pre:"pre",ul:"ul",...(0,r.a)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(c.h1,{id:"weavetracefeedback",children:"weave.trace.feedback"}),"\n",(0,s.jsx)(c.p,{children:"Classes for working with feedback on a project or ref level."}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)(c.h1,{id:"api-overview",children:"API Overview"}),"\n",(0,s.jsx)(c.h2,{id:"classes",children:"Classes"}),"\n",(0,s.jsxs)(c.ul,{children:["\n",(0,s.jsxs)(c.li,{children:[(0,s.jsx)(c.a,{href:"#class-feedbacks",children:(0,s.jsx)(c.code,{children:"feedback.Feedbacks"})}),": A collection of Feedback objects with utilities."]}),"\n",(0,s.jsxs)(c.li,{children:[(0,s.jsx)(c.a,{href:"#class-feedbackquery",children:(0,s.jsx)(c.code,{children:"feedback.FeedbackQuery"})}),": Lazy-loading object for fetching feedback from the server."]}),"\n",(0,s.jsxs)(c.li,{children:[(0,s.jsx)(c.a,{href:"#class-reffeedbackquery",children:(0,s.jsx)(c.code,{children:"feedback.RefFeedbackQuery"})}),": Object for interacting with feedback associated with a particular ref."]}),"\n"]}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L17",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h2,{id:"class-feedbacks",children:[(0,s.jsx)("kbd",{children:"class"})," ",(0,s.jsx)(c.code,{children:"Feedbacks"})]}),"\n",(0,s.jsx)(c.p,{children:"A collection of Feedback objects with utilities."}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L22",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-__init__",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"__init__"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"__init__(show_refs: bool, feedbacks: Optional[Iterable[Feedback]] = None) \u2192 None\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L28",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-refs",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"refs"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"refs() \u2192 Refs\n"})}),"\n",(0,s.jsx)(c.p,{children:"Return the unique refs associated with these feedbacks."}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L80",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h2,{id:"class-feedbackquery",children:[(0,s.jsx)("kbd",{children:"class"})," ",(0,s.jsx)(c.code,{children:"FeedbackQuery"})]}),"\n",(0,s.jsx)(c.p,{children:"Lazy-loading object for fetching feedback from the server."}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L93",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-__init__-1",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"__init__"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"__init__(\n    entity: str,\n    project: str,\n    query: Query,\n    offset: Optional[int] = None,\n    limit: Optional[int] = None,\n    show_refs: bool = False\n)\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L141",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-execute",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"execute"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"execute() \u2192 Feedbacks\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L122",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-refresh",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"refresh"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"refresh() \u2192 Feedbacks\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L147",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-refs-1",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"refs"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"refs() \u2192 Refs\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L164",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h2,{id:"class-reffeedbackquery",children:[(0,s.jsx)("kbd",{children:"class"})," ",(0,s.jsx)(c.code,{children:"RefFeedbackQuery"})]}),"\n",(0,s.jsx)(c.p,{children:"Object for interacting with feedback associated with a particular ref."}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L169",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-__init__-2",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"__init__"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"__init__(ref: str) \u2192 None\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L200",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-add",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"add"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"add(\n    feedback_type: str,\n    payload: Optional[dict[str, Any]] = None,\n    creator: Optional[str] = None,\n    **kwargs: dict[str, Any]\n) \u2192 str\n"})}),"\n",(0,s.jsx)(c.p,{children:"Add feedback to the ref."}),"\n",(0,s.jsx)(c.p,{children:'feedback_type: A string identifying the type of feedback. The "wandb." prefix is reserved. creator: The name to display for the originator of the feedback.'}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L228",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-add_note",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"add_note"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"add_note(note: str, creator: Optional[str] = None) \u2192 str\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L219",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-add_reaction",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"add_reaction"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"add_reaction(emoji: str, creator: Optional[str] = None) \u2192 str\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L141",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-execute-1",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"execute"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"execute() \u2192 Feedbacks\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L237",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-purge",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"purge"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"purge(feedback_id: str) \u2192 None\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L122",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-refresh-1",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"refresh"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"refresh() \u2192 Feedbacks\n"})}),"\n",(0,s.jsx)(c.hr,{}),"\n",(0,s.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/weave/trace/feedback.py#L147",children:(0,s.jsx)("img",{align:"right",src:"https://img.shields.io/badge/-source-cccccc?style=flat-square"})}),"\n",(0,s.jsxs)(c.h3,{id:"method-refs-2",children:[(0,s.jsx)("kbd",{children:"method"})," ",(0,s.jsx)(c.code,{children:"refs"})]}),"\n",(0,s.jsx)(c.pre,{children:(0,s.jsx)(c.code,{className:"language-python",children:"refs() \u2192 Refs\n"})})]})}function o(e={}){const{wrapper:c}={...(0,r.a)(),...e.components};return c?(0,s.jsx)(c,{...e,children:(0,s.jsx)(l,{...e})}):l(e)}},11151:(e,c,d)=>{d.d(c,{Z:()=>n,a:()=>t});var s=d(67294);const r={},a=s.createContext(r);function t(e){const c=s.useContext(a);return s.useMemo((function(){return"function"==typeof e?e(c):{...c,...e}}),[c,e])}function n(e){let c;return c=e.disableParentContext?"function"==typeof e.components?e.components(r):e.components||r:t(e.components),s.createElement(a.Provider,{value:c},e.children)}}}]);