import * as globals from '@wandb/weave/common/css/globals.styles';
import Loader from '@wandb/weave/common/components/WandbLoader';
import getConfig from '../config';
import {Node, NodeOrVoidNode, voidNode} from '@wandb/weave/core';
import produce from 'immer';
import moment from 'moment';
import React, {FC} from 'react';
import {useCallback, useEffect, useState} from 'react';
import {Button, Icon, Input} from 'semantic-ui-react';
import styled, {ThemeProvider} from 'styled-components';

import {useWeaveContext} from '../context';
import {consoleLog} from '../util';
import {useWeaveAutomation} from './automation';
import {PersistenceManager} from './PagePanelComponents/PersistenceManager';
import {
  CHILD_PANEL_DEFAULT_CONFIG,
  ChildPanel,
  ChildPanelConfigComp,
  ChildPanelFullConfig,
} from './Panel2/ChildPanel';
import {themes} from './Panel2/Editor.styles';
import {dummyProps, useConfig} from './Panel2/panel';
import * as Styles from './Panel2/PanelExpression/styles';
import {
  PanelInteractContextProvider,
  useEditorIsOpen,
  useSetInspectingPanel,
  useCloseEditor,
} from './Panel2/PanelInteractContext';
import {PanelRenderedConfigContextProvider} from './Panel2/PanelRenderedConfigContext';
import {PanelRootBrowser} from './Panel2/PanelRootBrowser/PanelRootBrowser';
import {useNewPanelFromRootQueryCallback} from './Panel2/PanelRootBrowser/util';
import Inspector from './Sidebar/Inspector';
import {useNodeWithServerType} from '../react';
import {
  inJupyterCell,
  uriFromNode,
  weaveTypeIsPanel,
  weaveTypeIsPanelGroup,
} from './PagePanelComponents/util';
import {useCopyCodeFromURI} from './PagePanelComponents/hooks';
import {
  IconAddNew,
  IconCheckmark,
  IconClose,
  IconCopy,
  IconHome,
  IconLoading,
  IconOpenNewTab,
  IconPencilEdit,
} from './Panel2/Icons';
import {addPanelToGroupConfig} from './Panel2/PanelGroup';

const JupyterControlsHelpText = styled.div<{active: boolean}>`
  width: max-content;
  position: absolute;
  top: 50px
  border-radius: 4px;
  right: 48px;
  // transform: translate(-50%, 0);
  text-align: center;
  color: #fff;
  background-color: #1d1f24;
  padding: 10px 12px;
  font-size: 14px;
  opacity: 0.8;

  transition: display 0.3s ease-in-out;

  visibility: ${props => (props.active ? '' : 'hidden')};
  opacity: ${props => (props.active ? 0.8 : 0)};
  transition: visibility 0s, opacity 0.3s ease-in-out;
`;

const JupyterControlsMain = styled.div<{reveal?: boolean}>`
  position: absolute;
  top: 50%;
  right: ${props => (props.reveal ? '-0px' : '-60px')};
  transition: right 0.3s ease-in-out;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  transform: translate(0, -50%);
  width: 40px;
  background-color: white;
  border: 1px solid #ddd;
  border-right: none;
  border-radius: 8px 0px 0px 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;
  gap: 8px;
  padding: 8px 0px;
  z-index: 100;
`;

const JupyterControlsIcon = styled.div`
  width: 25px;
  height: 25px;
  padding: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.1s ease-in-out;
  border-radius: 4px;
  &:hover {
    background: #0096ad1a;
    color: #0096ad;
  }
`;

interface HomeProps {
  updateConfig: (newConfig: ChildPanelFullConfig) => void;
  inJupyter: boolean;
}

const Home: React.FC<HomeProps> = props => {
  const now = moment().format('YY_MM_DD_hh_mm_ss');
  const inJupyter = props.inJupyter;
  const defaultName = now;
  const [newName, setNewName] = useState('');
  const weave = useWeaveContext();
  const name = 'dashboard-' + (newName === '' ? defaultName : newName);
  const makeNewDashboard = useNewPanelFromRootQueryCallback();
  const {urlPrefixed} = getConfig();
  const newDashboard = useCallback(() => {
    makeNewDashboard(name, voidNode(), true, newDashExpr => {
      if (inJupyter) {
        const expStr = weave
          .expToString(newDashExpr)
          .replace(/\n+/g, '')
          .replace(/\s+/g, '');
        window.open(
          urlPrefixed(`?exp=${encodeURIComponent(expStr)}`),
          '_blank'
        );
      } else {
        props.updateConfig({
          vars: {},
          input_node: newDashExpr,
          id: '',
          config: undefined,
        });
      }
    });
  }, [inJupyter, makeNewDashboard, name, props, urlPrefixed, weave]);
  const [rootConfig, updateRootConfig] = useConfig();
  const updateInput = useCallback(
    (newInput: Node) => {
      props.updateConfig({
        vars: {},
        input_node: newInput,
        id: '',
        config: undefined,
      });
    },
    [props]
  );
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
      <div
        style={{
          width: '100%',
          height: '90%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          // marginTop: 16,
          // marginBottom: 16,
        }}>
        <div
          style={{
            width: '90%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            gap: 16,
          }}>
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              // width: 400,
              padding: 16,
              border: '1px solid #eee',
              gap: 16,
              width: '100%',
            }}>
            <div
              style={{
                flexGrow: 1,
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}>
              <div
                style={{width: '100%', display: 'flex', alignItems: 'center'}}
                onKeyUp={e => {
                  if (e.key === 'Enter') {
                    newDashboard();
                  }
                }}>
                <Input
                  data-cy="new-dashboard-input"
                  placeholder={defaultName}
                  style={{flexGrow: 1}}
                  value={newName}
                  onChange={(e, {value}) => setNewName(value)}
                />
              </div>
              <div
                style={{
                  display: 'flex',
                  flex: 1,
                  width: '100%',
                }}>
                <Button onClick={newDashboard}>New dashboard</Button>
              </div>
            </div>
          </div>
          <div
            style={{
              width: '100%',
              height: '100%',
              padding: 16,
              border: '1px solid #eee',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}>
            {/* <div style={{marginBottom: 32}}>Your Weave Objects</div> */}
            <div style={{flexGrow: 1, overflow: 'auto'}}>
              <PanelRootBrowser
                input={voidNode() as any}
                updateInput={updateInput as any}
                isRoot={true}
                config={rootConfig}
                updateConfig={updateRootConfig}
                context={dummyProps.context}
                updateContext={dummyProps.updateContext}
              />
              {/* <DashboardList loadDashboard={loadDashboard} /> */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const PagePanel: React.FC = props => {
  const weave = useWeaveContext();
  const urlParams = new URLSearchParams(window.location.search);
  const fullScreen = urlParams.get('fullScreen') != null;
  const expString = urlParams.get('exp');
  const expNode = urlParams.get('expNode');
  const panelId = urlParams.get('panelId') ?? '';
  const automationId = urlParams.get('automationId');
  let panelConfig = urlParams.get('panelConfig') ?? undefined;
  const [loading, setLoading] = useState(true);
  if (panelConfig != null) {
    panelConfig = JSON.parse(panelConfig);
  }
  const inJupyter = inJupyterCell();

  const setUrlExp = useCallback(
    (exp: NodeOrVoidNode) => {
      const newExpStr = weave.expToString(exp);
      if (newExpStr === expString) {
        return;
      }
      const searchParams = new URLSearchParams(window.location.search);
      searchParams.set('exp', newExpStr);
      window.history.replaceState(
        null,
        '',
        `${window.location.pathname}?${searchParams}`
      );
    },
    [expString, weave]
  );

  const [config, setConfig] = useState<ChildPanelFullConfig>(
    CHILD_PANEL_DEFAULT_CONFIG
  );
  const updateConfig = useCallback(
    (newConfig: Partial<ChildPanelFullConfig>) => {
      setConfig(currentConfig => ({...currentConfig, ...newConfig}));
      if (newConfig.input_node != null) {
        setUrlExp(newConfig.input_node);
      }
    },
    [setConfig, setUrlExp]
  );
  const updateConfig2 = useCallback(
    (
      change: (oldConfig: ChildPanelFullConfig) => Partial<ChildPanelFullConfig>
    ) => {
      setConfig(currentConfig => {
        const configChanges = change(currentConfig);
        if (configChanges.input_node != null) {
          setUrlExp(configChanges.input_node);
        }
        const newConfig = produce(currentConfig, draft => {
          for (const key of Object.keys(configChanges)) {
            (draft as any)[key] = (configChanges as any)[key];
          }
        });
        consoleLog(
          'PagePanel config update. Old: ',
          currentConfig,
          ' Changes: ',
          configChanges,
          ' New: ',
          newConfig
        );
        return newConfig;
      });
    },
    [setConfig, setUrlExp]
  );
  const [forceRemount, setForceRemount] = useState(0);

  const updateInputNode = useCallback(
    (newInputNode: NodeOrVoidNode) => {
      updateConfig({input_node: newInputNode});
      setForceRemount(r => r + 1);
    },
    [updateConfig]
  );

  useWeaveAutomation(automationId);

  useEffect(() => {
    consoleLog('PAGE PANEL MOUNT');
    setLoading(true);
    if (expString != null) {
      weave.expression(expString, []).then(res => {
        updateConfig({
          input_node: res.expr as any,
          id: panelId,
          config: panelConfig,
        } as any);
        setLoading(false);
      });
    } else if (expNode != null) {
      updateConfig({
        input_node: JSON.parse(expNode) as any,
        id: panelId,
        config: panelConfig,
      } as any);
      setLoading(false);
    } else {
      updateConfig({
        input_node: voidNode(),
        id: panelId,
        config: panelConfig,
      } as any);
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [expString, forceRemount]);

  // Moved here from PanelExpression, not sure if working yet.
  // TODO: play/pause
  const [, /*weaveIsAutoRefresh*/ setWeaveIsAutoRefresh] = React.useState(
    weave.client.isPolling()
  );
  const onPollChangeListener = React.useCallback((isPolling: boolean) => {
    setWeaveIsAutoRefresh(isPolling);
  }, []);
  React.useEffect(() => {
    weave.client.addOnPollingChangeListener(onPollChangeListener);
    return () => {
      weave.client.removeOnPollingChangeListener(onPollChangeListener);
    };
  }, [weave, onPollChangeListener]);

  const goHome = React.useCallback(() => {
    updateConfig({
      vars: {},
      input_node: voidNode(),
      id: '',
      config: undefined,
    });
  }, [updateConfig]);

  if (loading) {
    return <Loader name="page-panel-loader" />;
  }

  return (
    <ThemeProvider theme={themes.light}>
      <PanelRenderedConfigContextProvider>
        <PanelInteractContextProvider>
          <WeaveRoot className="weave-root" fullScreen={fullScreen}>
            {config.input_node.nodeType === 'void' ? (
              <Home updateConfig={updateConfig} inJupyter={inJupyter} />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}>
                {!inJupyter && (
                  <PersistenceManager
                    inputNode={config.input_node}
                    updateNode={updateInputNode}
                    goHome={goHome}
                  />
                )}
                <PageContent
                  config={config}
                  updateConfig={updateConfig}
                  updateConfig2={updateConfig2}
                  goHome={goHome}
                />
                {/* <div
                  style={{
                    flex: '0 0 22px',
                    height: '16px',
                    overflow: 'hidden',
                    backgroundColor: '#fff',
                    borderTop: '1px solid #ddd',
                  }}>
                    PLACEHOLDER FOR EXECUTION DETAILS
                  </div> */}
              </div>
            )}
            {/* <ArtifactManager /> */}
          </WeaveRoot>
        </PanelInteractContextProvider>
      </PanelRenderedConfigContextProvider>
    </ThemeProvider>
  );
};

export default PagePanel;

type PageContentProps = {
  config: ChildPanelFullConfig;
  updateConfig: (newConfig: ChildPanelFullConfig) => void;
  updateConfig2: (change: (oldConfig: any) => any) => void;
  goHome: () => void;
};

export const PageContent: FC<PageContentProps> = ({
  config,
  updateConfig,
  updateConfig2,
  goHome,
}) => {
  const weave = useWeaveContext();
  const editorIsOpen = useEditorIsOpen();
  const inJupyter = inJupyterCell();
  const {urlPrefixed} = getConfig();

  const typedInputNode = useNodeWithServerType(config.input_node);
  const isPanel = weaveTypeIsPanel(
    typedInputNode.result?.type || {type: 'Panel' as any}
  );
  const isGroup = weaveTypeIsPanelGroup(typedInputNode.result?.type);
  const maybeUri = uriFromNode(config.input_node);
  const {onCopy} = useCopyCodeFromURI(maybeUri);

  const [showJupyterControls, setShowJupyterControls] = useState(false);
  const pageWidth = 985; // static for now
  const jupyterControlsHoverWidth = 60;
  const onMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (inJupyter) {
        const x = e.clientX;
        if (pageWidth - x < jupyterControlsHoverWidth) {
          setShowJupyterControls(true);
        } else {
          setShowJupyterControls(false);
        }
      }
    },
    [inJupyter]
  );

  const openNewTab = useCallback(() => {
    const expStr = weave
      .expToString(config.input_node)
      .replace(/\n+/g, '')
      .replace(/\s+/g, '');
    window.open(urlPrefixed(`/?exp=${encodeURIComponent(expStr)}`), '_blank');
  }, [config.input_node, urlPrefixed, weave]);

  return (
    <PageContentContainer
      onMouseLeave={e => setShowJupyterControls(false)}
      onMouseMove={onMouseMove}>
      <ChildPanel
        editable={!isPanel}
        prefixHeader={
          inJupyter ? (
            <Icon
              style={{cursor: 'pointer', color: '#555'}}
              name="home"
              onClick={goHome}
            />
          ) : (
            <></>
          )
        }
        prefixButtons={
          <>
            {inJupyter && (
              <>
                <Styles.BarButton onClick={openNewTab}>
                  <Icon name="external square alternate" />
                </Styles.BarButton>
                {maybeUri && (
                  <Styles.BarButton
                    onClick={() => {
                      onCopy();
                    }}>
                    <Icon name="copy" />
                  </Styles.BarButton>
                )}
              </>
            )}
          </>
        }
        config={config}
        updateConfig={updateConfig}
        updateConfig2={updateConfig2}
      />
      <Inspector active={editorIsOpen}>
        <ChildPanelConfigComp
          // pathEl={CHILD_NAME}
          config={config}
          updateConfig={updateConfig}
          updateConfig2={updateConfig2}
        />
      </Inspector>
      {inJupyter && (
        <JupyterPageControls
          reveal={showJupyterControls}
          goHome={goHome}
          openNewTab={openNewTab}
          maybeUri={maybeUri}
          isGroup={isGroup}
          updateConfig2={updateConfig2}
        />
      )}
    </PageContentContainer>
  );
};

const JupyterPageControls: React.FC<{
  reveal: boolean;
  goHome: () => void;
  openNewTab: () => void;
  maybeUri: string | null;
  isGroup: boolean;
  updateConfig2: (change: (oldConfig: any) => any) => void;
}> = props => {
  const [hoverText, setHoverText] = useState('');
  const {copyStatus, onCopy} = useCopyCodeFromURI(props.maybeUri);
  const setInspectingPanel = useSetInspectingPanel();
  const closeEditor = useCloseEditor();
  const editorIsOpen = useEditorIsOpen();
  const addPanelToGroup = useCallback(() => {
    props.updateConfig2(oldConfig => {
      console.log(oldConfig);
      return {
        ...oldConfig,
        config: {
          ...oldConfig.config,
          config: addPanelToGroupConfig(
            oldConfig.config.config,
            ['panel'],
            'panel'
          ),
        },
      };
    });
  }, [props]);

  return (
    <JupyterControlsMain
      reveal={props.reveal}
      onMouseLeave={e => {
        setHoverText('');
      }}>
      <JupyterControlsHelpText active={hoverText !== ''}>
        {hoverText}
      </JupyterControlsHelpText>

      {props.isGroup && (
        <JupyterControlsIcon
          onClick={addPanelToGroup}
          onMouseEnter={e => {
            setHoverText('Add new panel');
          }}
          onMouseLeave={e => {
            setHoverText('');
          }}>
          <IconAddNew />
        </JupyterControlsIcon>
      )}

      {editorIsOpen ? (
        <JupyterControlsIcon
          onClick={() => {
            closeEditor();
            setHoverText('Edit configuration');
          }}
          onMouseEnter={e => {
            setHoverText('Close configuration editor');
          }}
          onMouseLeave={e => {
            setHoverText('');
          }}>
          <IconClose />
        </JupyterControlsIcon>
      ) : (
        <JupyterControlsIcon
          onClick={() => {
            setInspectingPanel(['']);
            setHoverText('Close configuration editor');
          }}
          onMouseEnter={e => {
            setHoverText('Edit configuration');
          }}
          onMouseLeave={e => {
            setHoverText('');
          }}>
          <IconPencilEdit />
        </JupyterControlsIcon>
      )}
      <JupyterControlsIcon
        onClick={onCopy}
        onMouseEnter={e => {
          setHoverText('Copy dash code');
        }}
        onMouseLeave={e => {
          setHoverText('');
        }}>
        {copyStatus === 'loading' ? (
          <IconLoading />
        ) : copyStatus === 'success' ? (
          <IconCheckmark />
        ) : (
          <IconCopy />
        )}
      </JupyterControlsIcon>
      <JupyterControlsIcon
        onClick={props.openNewTab}
        onMouseEnter={e => {
          setHoverText('Open dash in new tab');
        }}
        onMouseLeave={e => {
          setHoverText('');
        }}>
        <IconOpenNewTab />
      </JupyterControlsIcon>
      <JupyterControlsIcon
        onClick={props.goHome}
        onMouseEnter={e => {
          setHoverText('Go home');
        }}
        onMouseLeave={e => {
          setHoverText('');
        }}>
        <IconHome />
      </JupyterControlsIcon>
    </JupyterControlsMain>
  );
};

const WeaveRoot = styled.div<{fullScreen: boolean}>`
  position: ${p => (p.fullScreen ? `fixed` : `absolute`)};
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: ${globals.WHITE};
  color: ${globals.TEXT_PRIMARY_COLOR};
`;

const PageContentContainer = styled.div`
  flex: 1 1 300px;
  overflow: hidden;
  display: flex;
`;
