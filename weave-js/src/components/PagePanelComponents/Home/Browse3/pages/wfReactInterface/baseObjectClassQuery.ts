import {useDeepMemo} from '@wandb/weave/hookUtils';
import {useEffect, useRef, useState} from 'react';
import {z} from 'zod';

import {
  TestOnlyExampleSchema,
  TestOnlyNestedBaseObjectSchema,
} from './generatedBaseObjectClasses.zod';
import {TraceServerClient} from './traceServerClient';
import {useGetTraceServerClientContext} from './traceServerClientContext';
import {
  TraceObjCreateReq,
  TraceObjCreateRes,
  TraceObjQueryReq,
  TraceObjSchema,
} from './traceServerClientTypes';
import {Loadable} from './wfDataModelHooksInterface';

// TODO: This should be generated from the registry!
const collectionRegistry = {
  TestOnlyExample: TestOnlyExampleSchema,
  TestOnlyNestedBaseObject: TestOnlyNestedBaseObjectSchema,
};

export const useCollectionObjects = <
  C extends keyof typeof collectionRegistry,
  T = z.infer<(typeof collectionRegistry)[C]>
>(
  collectionName: C,
  req: TraceObjQueryReq
): Loadable<Array<TraceObjSchema<T, C>>> => {
  const [objects, setObjects] = useState<Array<TraceObjSchema<T, C>>>([]);
  const getTsClient = useGetTraceServerClientContext();
  const client = getTsClient();
  const deepReq = useDeepMemo(req);
  const currReq = useRef(deepReq);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    currReq.current = deepReq;
    getCollectionObjects(client, collectionName, deepReq).then(
      collectionObjects => {
        if (isMounted && currReq.current === deepReq) {
          setObjects(collectionObjects as Array<TraceObjSchema<T, C>>);
          setLoading(false);
        }
      }
    );
    return () => {
      isMounted = false;
    };
  }, [client, collectionName, deepReq]);

  return {result: objects, loading};
};

const getCollectionObjects = async <
  C extends keyof typeof collectionRegistry,
  T = z.infer<(typeof collectionRegistry)[C]>
>(
  client: TraceServerClient,
  collectionName: C,
  req: TraceObjQueryReq
): Promise<Array<TraceObjSchema<T, C>>> => {
  const knownCollection = collectionRegistry[collectionName];
  if (!knownCollection) {
    console.warn(`Unknown collection: ${collectionName}`);
    return [];
  }

  const reqWithCollection: TraceObjQueryReq = {
    ...req,
    filter: {...req.filter, base_object_classes: [collectionName]},
  };

  const objectPromise = client.objsQuery(reqWithCollection);

  const objects = await objectPromise;

  return objects.objs
    .map(obj => ({obj, parsed: knownCollection.safeParse(obj.val)}))
    .filter(({parsed}) => parsed.success)
    .map(({obj, parsed}) => ({...obj, val: parsed.data!})) as Array<
    TraceObjSchema<T, C>
  >;
};

export const useCreateCollectionObject = <
  C extends keyof typeof collectionRegistry,
  T = z.infer<(typeof collectionRegistry)[C]>
>(
  collectionName: C
): ((req: TraceObjCreateReq<T>) => Promise<TraceObjCreateRes>) => {
  const getTsClient = useGetTraceServerClientContext();
  const client = getTsClient();
  return (req: TraceObjCreateReq<T>) =>
    createCollectionObject(client, collectionName, req);
};

const createCollectionObject = async <
  C extends keyof typeof collectionRegistry,
  T = z.infer<(typeof collectionRegistry)[C]>
>(
  client: TraceServerClient,
  collectionName: C,
  req: TraceObjCreateReq<T>
): Promise<TraceObjCreateRes> => {
  const knownCollection = collectionRegistry[collectionName];
  if (!knownCollection) {
    throw new Error(`Unknown collection: ${collectionName}`);
  }

  const verifiedObject = knownCollection.safeParse(req.obj.val);

  if (!verifiedObject.success) {
    throw new Error(
      `Invalid object: ${JSON.stringify(verifiedObject.error.errors)}`
    );
  }

  const reqWithCollection: TraceObjCreateReq = {
    ...req,
    obj: {
      ...req.obj,
      val: {...req.obj.val, _bases: [collectionName, 'BaseModel']},
    },
  };

  const createPromse = client.objCreate(reqWithCollection);

  return createPromse;
};
