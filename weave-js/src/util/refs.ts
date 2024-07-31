const PROTOCOL = 'weave://';

export const makeRefCall = (
  entity: string,
  project: string,
  callId: string
): string => {
  return `${PROTOCOL}/${encodeURIComponent(entity)}/${encodeURIComponent(project)}/call/${encodeURIComponent(callId)}`;
};

export const makeRefObject = (
  entity: string,
  project: string,
  objectType: string,
  objectId: string,
  objectVersion: string,
  refExtra: string | undefined
): string => {
  let ref = `${PROTOCOL}/${encodeURIComponent(entity)}/${encodeURIComponent(project)}/${encodeURIComponent(objectType)}/${encodeURIComponent(objectId)}:${encodeURIComponent(objectVersion)}`;
  if (refExtra) {
    ref += `/${refExtra}`;
  }
  return ref;
};

export const abbreviateRef = (ref: string): string => {
  return PROTOCOL + '/...' + ref.slice(-6);
};
