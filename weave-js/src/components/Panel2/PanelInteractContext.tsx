/* Non-persisted UI state. */

import React, {useCallback, useContext, useState} from 'react';

import {usePanelContext} from './PanelContext';

interface PanelInteractState {
  highlightInputExpr?: boolean;
}

export interface PanelInteractContextState {
  // State is stored by panel path. panel path is managed by PanelContext.
  editorSidebarOpen: boolean;
  selectedPath: string[];
  panelState: {[pathString: string]: PanelInteractState};
}

export interface PanelInteractContextValue {
  state: PanelInteractContextState;
  setState: (
    newState: (
      prevState: PanelInteractContextState
    ) => PanelInteractContextState
  ) => void;
}

export const PanelInteractContext =
  React.createContext<PanelInteractContextValue | null>(null);

export const PanelInteractContextProvider: React.FC<{}> = React.memo(
  ({children}) => {
    const [state, setState] = useState<PanelInteractContextState>({
      selectedPath: [],
      editorSidebarOpen: false,
      panelState: {},
    });

    return (
      <PanelInteractContext.Provider value={{state, setState}}>
        {children}
      </PanelInteractContext.Provider>
    );
  }
);

const usePanelInteractContext = () => {
  const context = useContext(PanelInteractContext);
  if (context == null) {
    throw new Error(
      'usePanelInteractContext must be used within a PanelInteractContextProvider'
    );
  }
  return context;
};

const usePanelInteractStateByPath = (path: string[]) => {
  const {state} = usePanelInteractContext();
  const pathString = path.join('.');
  return state.panelState[pathString];
};

export const usePanelInputExprIsHighlightedByPath = (path: string[]) => {
  return usePanelInteractStateByPath(path)?.highlightInputExpr === true;
};

const useSetPanelStateByPath = () => {
  const {setState} = usePanelInteractContext();

  return useCallback(
    (
      path: string[],
      changeState: (prevState: PanelInteractState) => PanelInteractState
    ) => {
      const pathString = path.join('.');
      setState(prevState => {
        return {
          ...prevState,
          panelState: {
            ...prevState.panelState,
            [pathString]: changeState(prevState.panelState[pathString]),
          },
        };
      });
    },
    [setState]
  );
};

export const useSetPanelInputExprIsHighlighted = () => {
  const setPanelState = useSetPanelStateByPath();
  return useCallback(
    (path: string[], highlight: boolean) => {
      setPanelState(path, prevState => {
        return {
          ...prevState,
          highlightInputExpr: highlight,
        };
      });
    },
    [setPanelState]
  );
};

export const useSetInspectingPanel = () => {
  const {setState} = usePanelInteractContext();
  return useCallback(
    (path: string[]) => {
      setState(prevState => ({
        ...prevState,
        editorSidebarOpen: true,
        selectedPath: path,
      }));
    },
    [setState]
  );
};

export const useSetInspectingChildPanel = () => {
  const setInspectingPanel = useSetInspectingPanel();
  const {path} = usePanelContext();
  return useCallback(
    (childPath: string) => {
      setInspectingPanel(path.concat([childPath]));
    },
    [path, setInspectingPanel]
  );
};

export const useCloseEditor = () => {
  const {setState} = usePanelInteractContext();
  return useCallback(() => {
    setState(prevState => ({
      ...prevState,
      editorSidebarOpen: false,
    }));
  }, [setState]);
};

export const useEditorIsOpen = () => {
  const {state} = usePanelInteractContext();
  return state.editorSidebarOpen;
};

export const useSelectedPath = () => {
  const {state} = usePanelInteractContext();
  return state.selectedPath;
};
