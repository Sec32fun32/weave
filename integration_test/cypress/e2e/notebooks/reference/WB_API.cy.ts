import {checkWeaveNotebookOutputs} from '../notebooks';

describe('../weave/legacy/examples/reference/WB_API.ipynb notebook test', () => {
  it('passes', () =>
    checkWeaveNotebookOutputs(
      '../weave/legacy/examples/reference/WB_API.ipynb'
    ));
});
