import _ from 'lodash';

import {
  FeedbackCreateReq,
  FeedbackCreateRes,
  FeedbackPurgeReq,
  FeedbackPurgeRes,
  FeedbackReplaceReq,
  FeedbackReplaceRes,
  TraceCallsDeleteReq,
  TraceCallUpdateReq,
  TraceRefsReadBatchReq,
  TraceRefsReadBatchRes,
} from './traceServerClientTypes';
import {DirectTraceServerClient} from './traceServerDirectClient';

const DEFAULT_BATCH_INTERVAL = 150;
const MAX_REFS_PER_BATCH = 1000;

export class TraceServerClient extends DirectTraceServerClient {
  private readBatchCollectors: Array<{
    req: TraceRefsReadBatchReq;
    resolvePromise: (res: TraceRefsReadBatchRes) => void;
    rejectPromise: (err: any) => void;
  }> = [];
  private onDeleteListeners: Array<() => void>;
  private onRenameListeners: Array<() => void>;
  // weave_ref -> feedback_ref -> callback
  // For feedback without a feedback_ref, (the default case)
  // the key is the empty string (this.FEEDBACK_REF_DEFAULT).
  private onFeedbackListeners: Record<
    string,
    Record<string, Array<() => void>>
  >;

  constructor(baseUrl: string) {
    super(baseUrl);
    this.readBatchCollectors = [];
    this.scheduleReadBatch();
    this.onDeleteListeners = [];
    this.onRenameListeners = [];
    this.onFeedbackListeners = {};
  }

  private FEEDBACK_REF_DEFAULT = '';

  /**
   * Registers a callback to be called when a delete operation occurs.
   * This method is purely for local notification within the client
   *    and does not interact with the REST API.
   *
   * @param callback A function to be called when a delete operation is triggered.
   * @returns A function to unregister the callback.
   */
  public registerOnDeleteListener(callback: () => void): () => void {
    this.onDeleteListeners.push(callback);
    return () => {
      this.onDeleteListeners = this.onDeleteListeners.filter(
        listener => listener !== callback
      );
    };
  }
  public registerOnRenameListener(callback: () => void): () => void {
    this.onRenameListeners.push(callback);
    return () => {
      this.onRenameListeners = this.onRenameListeners.filter(
        listener => listener !== callback
      );
    };
  }
  public registerOnFeedbackListener(
    weaveRef: string,
    callback: () => void,
    feedbackRef?: string
  ): () => void {
    const feedbackRefResolved = feedbackRef ?? this.FEEDBACK_REF_DEFAULT;
    if (!(feedbackRefResolved in this.onFeedbackListeners)) {
      this.onFeedbackListeners[feedbackRefResolved] = {};
    }
    if (!(weaveRef in this.onFeedbackListeners[feedbackRefResolved])) {
      this.onFeedbackListeners[feedbackRefResolved][weaveRef] = [];
    }
    this.onFeedbackListeners[feedbackRefResolved][weaveRef].push(callback);
    return () => {
      const newListeners = this.onFeedbackListeners[feedbackRefResolved][
        weaveRef
      ].filter(listener => listener !== callback);
      if (newListeners.length) {
        this.onFeedbackListeners[feedbackRefResolved][weaveRef] = newListeners;
      } else {
        delete this.onFeedbackListeners[feedbackRefResolved][weaveRef];
      }
    };
  }

  public callsDelete(req: TraceCallsDeleteReq): Promise<void> {
    const res = super.callsDelete(req).then(() => {
      this.onDeleteListeners.forEach(listener => listener());
    });
    return res;
  }

  public callUpdate(req: TraceCallUpdateReq): Promise<void> {
    const res = super.callUpdate(req).then(() => {
      this.onRenameListeners.forEach(listener => listener());
    });
    return res;
  }

  public feedbackCreate(req: FeedbackCreateReq): Promise<FeedbackCreateRes> {
    const res = super.feedbackCreate(req).then(createRes => {
      const feedbackRefResolved =
        req.payload?.feedback_ref ?? this.FEEDBACK_REF_DEFAULT;
      const listeners =
        this.onFeedbackListeners[feedbackRefResolved][req.weave_ref] ?? [];
      listeners.forEach(listener => listener());
      return createRes;
    });
    return res;
  }
  public feedbackPurge(req: FeedbackPurgeReq): Promise<FeedbackPurgeRes> {
    const res = super.feedbackPurge(req).then(purgeRes => {
      // TODO: Since purge takes a query, we need to change the result to include
      //       information about the refs that were modified.
      //       For now, just call all registered feedback listeners.
      for (const listeners of Object.values(this.onFeedbackListeners)) {
        for (const listenersForWeaveRef of Object.values(listeners)) {
          listenersForWeaveRef.forEach(listener => listener());
        }
      }
      return purgeRes;
    });
    return res;
  }

  public feedbackReplace(req: FeedbackReplaceReq): Promise<FeedbackReplaceRes> {
    const res = super.feedbackReplace(req).then(replaceRes => {
      const feedbackRefResolved =
        req.payload?.feedback_ref ?? this.FEEDBACK_REF_DEFAULT;
      const listeners =
        this.onFeedbackListeners[feedbackRefResolved][req.weave_ref] ?? [];
      listeners.forEach(listener => listener());
      return replaceRes;
    });
    return res;
  }

  public readBatch(req: TraceRefsReadBatchReq): Promise<TraceRefsReadBatchRes> {
    return this.requestReadBatch(req);
  }

  private requestReadBatch(
    req: TraceRefsReadBatchReq
  ): Promise<TraceRefsReadBatchRes> {
    return new Promise<TraceRefsReadBatchRes>((resolve, reject) => {
      this.readBatchCollectors.push({
        req,
        resolvePromise: resolve,
        rejectPromise: reject,
      });
    });
  }

  private async doReadBatch() {
    if (this.readBatchCollectors.length === 0) {
      return;
    }
    const collectors = [...this.readBatchCollectors];
    this.readBatchCollectors = [];
    const refs = _.uniq(collectors.map(c => c.req.refs).flat());
    const valMap = new Map<string, any>();
    while (refs.length > 0) {
      const refsForBatch = refs.splice(0, MAX_REFS_PER_BATCH);
      const res = await this.readBatchDirect({refs: refsForBatch});
      const vals = res.vals;
      for (let i = 0; i < refsForBatch.length; i++) {
        valMap.set(refsForBatch[i], vals[i]);
      }
    }
    collectors.forEach(collector => {
      const req = collector.req;
      const refVals = req.refs.map(ref => valMap.get(ref));
      collector.resolvePromise({vals: refVals});
    });
  }

  private async scheduleReadBatch() {
    await this.doReadBatch();
    setTimeout(this.scheduleReadBatch.bind(this), DEFAULT_BATCH_INTERVAL);
  }

  private readBatchDirect(
    req: TraceRefsReadBatchReq
  ): Promise<TraceRefsReadBatchRes> {
    return super.readBatch(req);
  }
}
